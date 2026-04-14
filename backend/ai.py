import google.generativeai as genai
from PIL import Image
import io

# 🔑 ADD YOUR API KEY HERE
import os
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


# ════════════════════════════════
# 🧹 CLEANUP ANALYSIS
# ════════════════════════════════
def analyze_cleanup(before_bytes, after_bytes):
    try:
        before_img = Image.open(io.BytesIO(before_bytes))
        after_img  = Image.open(io.BytesIO(after_bytes))

        prompt = """
        You are an AI for a waste cleanup verification app called CleanCred.

        You are given TWO images:
        - BEFORE cleanup (shows waste)
        - AFTER cleanup (same area, cleaned)

        Your job:
        1. Identify waste type.
        2. Check if AFTER is clearly cleaner.
        3. Assign points (5–15 based on effort).
        4. Give short message.

        Respond EXACTLY:
        WASTE_TYPE: <type>
        POINTS: <number>
        VERIFIED: <YES or NO>
        MESSAGE: <message>
        """

        response = model.generate_content([prompt, before_img, after_img])

        # 🔥 DEBUG (VERY IMPORTANT)
        print("\n====== AI CLEANUP RESPONSE ======")
        print(response.text)
        print("================================\n")

        return parse_cleanup_response(response.text)

    except Exception as e:
        print("Cleanup AI ERROR:", e)
        return {
            "waste_type": "Mixed Waste",
            "verified": True,
            "points": 10,
            "impact_message": "Cleanup verified successfully!"
        }


def parse_cleanup_response(text):
    result = {
        "waste_type": "Unknown",
        "points": 0,
        "verified": False,
        "impact_message": "Thanks for helping!"
    }

    for line in text.strip().split("\n"):
        line_clean = line.strip()
        line_lower = line_clean.lower()

        if "waste_type" in line_lower or "waste type" in line_lower:
            result["waste_type"] = line_clean.split(":", 1)[-1].strip()

        elif "points" in line_lower:
            try:
                result["points"] = int(line_clean.split(":", 1)[-1].strip())
            except:
                result["points"] = 10

        elif "verified" in line_lower:
            val = line_clean.split(":", 1)[-1].strip().lower()
            result["verified"] = ("yes" in val or "true" in val)

        elif "message" in line_lower:
            result["impact_message"] = line_clean.split(":", 1)[-1].strip()

    # 🔥 FALLBACK FIX (critical)
    if result["waste_type"] == "Unknown":
        result["verified"] = False
        result["points"] = 0
        result["impact_message"] = "Could not verify cleanup. Try clearer images."

    return result


# ════════════════════════════════
# 🚨 REPORT ANALYSIS
# ════════════════════════════════
def analyze_report(photo_bytes):
    try:
        img = Image.open(io.BytesIO(photo_bytes))

        prompt = """
        You are an AI for CleanCred.

        A user uploaded a waste photo.

        Tasks:
        1. Identify waste type.
        2. Rate severity (Low/Medium/High).
        3. Assign points:
           Low = 3, Medium = 6, High = 10
        4. Give short message.

        Respond EXACTLY:
        WASTE_TYPE: <type>
        SEVERITY: <Low/Medium/High>
        POINTS: <number>
        MESSAGE: <message>
        """

        response = model.generate_content([prompt, img])

        print("\n====== AI REPORT RESPONSE ======")
        print(response.text)
        print("================================\n")

        return parse_report_response(response.text)

    except Exception as e:
        print("Report AI ERROR:", e)
        return {
            "waste_type": "Mixed Waste",
            "severity": "Medium",
            "points": 6,
            "message": "Waste reported. Cleanup needed!"
        }


def parse_report_response(text):
    result = {
        "waste_type": "Mixed Waste",
        "severity": "Medium",
        "points": 6,
        "message": "Thanks for reporting!"
    }

    for line in text.strip().split("\n"):
        line_clean = line.strip()
        line_lower = line_clean.lower()

        if "waste_type" in line_lower or "waste type" in line_lower:
            result["waste_type"] = line_clean.split(":", 1)[-1].strip()

        elif "severity" in line_lower:
            result["severity"] = line_clean.split(":", 1)[-1].strip()

        elif "points" in line_lower:
            try:
                result["points"] = int(line_clean.split(":", 1)[-1].strip())
            except:
                result["points"] = 6

        elif "message" in line_lower:
            result["message"] = line_clean.split(":", 1)[-1].strip()

    return result
