from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from backend.ai import analyze_cleanup, analyze_report
from datetime import datetime
import sqlite3
import json
import os
import uuid

app = Flask(__name__, static_folder='../frontend')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'cleancred.db')


# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    try:
        c = conn.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS points (
                id    INTEGER PRIMARY KEY,
                total INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS cleanups (
                id          TEXT PRIMARY KEY,
                waste_type  TEXT,
                points      INTEGER,
                message     TEXT,
                verified    INTEGER,
                created_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS reports (
                id          TEXT PRIMARY KEY,
                location    TEXT,
                lat         REAL,
                lng         REAL,
                reporter    TEXT,
                severity    TEXT,
                waste_type  TEXT,
                points      INTEGER,
                created_at  TEXT,
                status      TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                location    TEXT,
                date        TEXT,
                description TEXT,
                leader      TEXT,
                lat         REAL,
                lng         REAL,
                members     TEXT,
                status      TEXT,
                created_at  TEXT
            );
        ''')
        c.execute('INSERT OR IGNORE INTO points (id, total) VALUES (1, 0)')
        conn.commit()
    finally:
        conn.close()


init_db()


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def get_total_points() -> int:
    conn = get_db()
    try:
        row = conn.execute('SELECT total FROM points WHERE id=1').fetchone()
        return row['total'] if row else 0
    finally:
        conn.close()


def add_points(amount: int) -> int:
    """Add points and return the new total."""
    conn = get_db()
    try:
        conn.execute('UPDATE points SET total = total + ? WHERE id=1', (amount,))
        conn.commit()
        row = conn.execute('SELECT total FROM points WHERE id=1').fetchone()
        return row['total'] if row else 0
    finally:
        conn.close()


def safe_float(value, default: float) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def uid() -> str:
    return str(uuid.uuid4())[:8]


def now_display() -> str:
    """Human-readable timestamp for UI display."""
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def now_iso() -> str:
    """ISO timestamp for correct DB ordering."""
    return datetime.now().isoformat()


# ══════════════════════════════════════════════════════════════
# STATIC / FRONTEND
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)


# ══════════════════════════════════════════════════════════════
# POINTS
# ══════════════════════════════════════════════════════════════

@app.route('/points', methods=['GET'])
def route_get_points():
    return jsonify({"total_points": get_total_points()})


# ══════════════════════════════════════════════════════════════
# CLEANUPS
# ══════════════════════════════════════════════════════════════

@app.route('/cleanups', methods=['GET'])
def route_get_cleanups():
    conn = get_db()
    try:
        rows = conn.execute(
            'SELECT * FROM cleanups ORDER BY created_at DESC'
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.route('/analyze', methods=['POST'])
def route_analyze():
    before_file = request.files.get('before')
    after_file  = request.files.get('after')
    video_file  = request.files.get('video')

    if not before_file or not after_file or not video_file:
        return jsonify({"error": "before, after, and video files are all required"}), 400

    result = analyze_cleanup(before_file.read(), after_file.read())

    if result["verified"] and result["points"] > 0:
        total = add_points(result["points"])
        conn  = get_db()
        try:
            conn.execute(
                'INSERT INTO cleanups VALUES (?,?,?,?,?,?)',
                (uid(), result["waste_type"], result["points"],
                 result["impact_message"], 1, now_display())
            )
            conn.commit()
        finally:
            conn.close()
    else:
        result["points"]         = 0
        result["impact_message"] = (
            "Cleanup not verified. Make sure the after photo clearly shows "
            "the area is cleaner."
        )
        total = get_total_points()

    result["total_points"] = total
    return jsonify(result)


# ══════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════

@app.route('/reports', methods=['GET'])
def route_get_reports():
    conn = get_db()
    try:
        rows = conn.execute(
            'SELECT * FROM reports ORDER BY created_at DESC'
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.route('/report', methods=['POST'])
def route_report():
    photo    = request.files.get('photo')
    location = request.form.get('location', 'Unknown location').strip() or 'Unknown location'
    reporter = request.form.get('reporter', 'Anonymous').strip() or 'Anonymous'
    lat      = safe_float(request.form.get('lat'), 10.7867)
    lng      = safe_float(request.form.get('lng'), 76.6548)

    if not photo:
        return jsonify({"error": "A waste photo is required"}), 400

    result    = analyze_report(photo.read())
    report_id = uid()

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO reports VALUES (?,?,?,?,?,?,?,?,?,?)',
            (report_id, location, lat, lng, reporter,
             result["severity"], result["waste_type"],
             result["points"], now_iso(), "reported")
        )
        conn.commit()
    finally:
        conn.close()

    total = add_points(result["points"])

    return jsonify({
        "success":      True,
        "severity":     result["severity"],
        "waste_type":   result["waste_type"],
        "points":       result["points"],
        "total_points": total,
        "message":      result["message"],
        "report_id":    report_id
    })


# ══════════════════════════════════════════════════════════════
# EVENTS
# ══════════════════════════════════════════════════════════════

@app.route('/events', methods=['GET', 'POST'])
def route_events():
    if request.method == 'GET':
        conn = get_db()
        try:
            rows   = conn.execute('SELECT * FROM events ORDER BY date ASC').fetchall()
            result = []
            for r in rows:
                e = dict(r)
                e['members'] = json.loads(e['members'])
                result.append(e)
            return jsonify(result)
        finally:
            conn.close()

    # POST — create event
    data = request.get_json() if request.is_json else request.form.to_dict()

    location    = data.get('location', '').strip()
    date        = data.get('date', '').strip()
    description = data.get('description', '').strip()
    leader      = data.get('leader', 'Anonymous').strip() or 'Anonymous'
    lat         = safe_float(data.get('lat'), 10.7867)
    lng         = safe_float(data.get('lng'), 76.6548)

    if not location or not date:
        return jsonify({"error": "location and date are required"}), 400

    event_id   = uid()
    members    = json.dumps([leader])
    created_at = datetime.now().strftime("%d %b %Y")

    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?)',
            (event_id, location, date, description,
             leader, lat, lng, members, "upcoming", created_at)
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        "success": True,
        "event": {
            "id": event_id, "location": location, "date": date,
            "description": description, "leader": leader,
            "lat": lat, "lng": lng, "members": [leader],
            "status": "upcoming", "created_at": created_at
        }
    })


@app.route('/events/<event_id>/join', methods=['POST'])
def route_join_event(event_id):
    data = request.get_json() if request.is_json else request.form.to_dict()
    name = data.get('name', 'Anonymous').strip() or 'Anonymous'

    conn = get_db()
    try:
        row = conn.execute(
            'SELECT * FROM events WHERE id=?', (event_id,)
        ).fetchone()

        if not row:
            return jsonify({"error": "Event not found"}), 404

        members = json.loads(row['members'])
        if name not in members:
            members.append(name)
            conn.execute(
                'UPDATE events SET members=? WHERE id=?',
                (json.dumps(members), event_id)
            )
            conn.commit()
    finally:
        conn.close()

    return jsonify({"success": True, "members": members})


@app.route('/events/<event_id>/complete', methods=['POST'])
def route_complete_event(event_id):
    before_file = request.files.get('before')
    after_file  = request.files.get('after')

    if not before_file or not after_file:
        return jsonify({"error": "before and after photos are required"}), 400

    result = analyze_cleanup(before_file.read(), after_file.read())

    conn = get_db()
    try:
        row = conn.execute(
            'SELECT * FROM events WHERE id=?', (event_id,)
        ).fetchone()

        if not row:
            return jsonify({"error": "Event not found"}), 404

        if not result["verified"]:
            return jsonify({
                "success":  False,
                "verified": False,
                "message":  "Cleanup not verified. Upload clearer before/after photos."
            })

        members      = json.loads(row['members'])
        member_count = len(members)
        base_pts     = result["points"]
        leader_bonus  = (base_pts * 2) + 50   # flat multiplier, not scaled by member count
        member_reward = base_pts + 20

        conn.execute(
            'UPDATE events SET status=? WHERE id=?',
            ("completed", event_id)
        )
        conn.commit()
    finally:
        conn.close()

    total = add_points(leader_bonus)

    return jsonify({
        "success":       True,
        "verified":      True,
        "leader_points": leader_bonus,
        "member_points": member_reward,
        "member_count":  member_count,
        "certificate":   True,
        "total_points":  total,
        "bonus_message": (
            f"Leader bonus: +{leader_bonus} pts | "
            f"Each member: +{member_reward} pts"
        )
    })


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # debug=False for production; use gunicorn instead:
    #   gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(debug=False, host='0.0.0.0', port=5000)
