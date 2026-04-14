# CleanCred
### Turning Clean Actions into Real Rewards

##  Overview

**CleanCred** is an AI-powered sustainability platform that motivates people to clean their surroundings by rewarding them with credits for verified environmental actions.

Users upload proof (images/videos) of cleaning activities, and the system uses AI to validate the action and assign reward points. These points can later be redeemed through partner platforms like food delivery, ticketing, or e-commerce services. The platform also builds a community-driven ecosystem where users can report waste hotspots and contribute collectively to cleaner environments.

## 🚨 Problem Statement

Waste accumulation in public spaces is a major issue.<br>
Even though people notice it, very few take action because: <br>

* People lack motivation to take initiative
* No system exists to verify or reward cleaning efforts
* Waste hotspots go unreported and ignored

## 💡 Solution

CleanCred solves this by:
* Incentivizing cleaning through rewards
* Using AI to validate user-submitted proof
* Allowing users to report garbage hotspots
* Building a community around environmental action

## ⚙️ Features

📸 Upload image/video proof of cleaning <br>
🤖 AI-based validation (Gemini API) <br>
🗺️ Location tagging using maps (Leaflet.js) <br>
💰 Credit-based reward system <br>
🧑‍🤝‍🧑 Community platform for social impact <br>
🚨 Garbage hotspot reporting system <br>
🏆 Leaderboard (user ranking based on contributions) <br>

## 🛠️ Tech Stack

# Frontend
HTML
CSS
JavaScript

# Backend
Python (Flask)

# Database
Firebase

# Hosting
Render

# APIs & Libraries
Gemini AI API <br>
Leaflet.js (maps & location visualization)

## 🧠 How It Works

1. User Registration

Users begin by entering basic details such as name and city, enabling localized tracking of contributions.

2. Dashboard Overview

After logging in, users access a dashboard that includes: <br>
 * User level (based on contribution)
 * Live feed of activities
 * Interactive map showing garbage hotspots
 
3. Identifying a Dirty Area
   
* User spots a polluted location
* Captures a before image of the area

4. Cleaning & Proof Submission

Users document the cleaning process by uploading: <br>
📸 Before image (dirty area) <br>
🎥 Video of waste disposal <br>
📸 After image (cleaned area) <br>

5. AI-Based Verification & Reward System
   
Gemini AI evaluates:<br>
* Authenticity of cleaning
* Type of waste
* Level of effort <br>
Points are awarded dynamically based on impact

6. Reporting Garbage Hotspots

If users cannot clean: <br>
* Upload the image of the place
* They can report the location manually Or use auto-detect for location tagging
* Reported areas appear on the map

7. Community Cleaning Events
   
* Users can create cleaning events
* Others can join and participate
* Encourages collaborative action

8. Event Contribution & Completion
   
* Participants upload before/after proof with event ID
* After verification: <br>
✅ Event is marked complete <br>
🏅 Rewards and certificates are issued <br>

9. Leaderboard & Rewards
    
Users can track:<br>
🏆 Ranking <br>
💰 Points<br>
🎁 Reward eligibility<br>


## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cleancred.git
cd cleancred
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file and add:

```
GEMINI_API_KEY=your_api_key
FIREBASE_CONFIG=your_config
```

### 5. Run the app

```bash
python app.py
```

## 🌍 Deployment

Deployed using Render.

## 🎯 Future Scope

* Integration with platforms like Swiggy, Zomato, BookMyShow
* NGO and government collaboration
* Advanced AI verification
* Gamification (leaderboards, badges)
* Mobile app development


## 🤝 Contribution

Contributions are welcome!
Feel free to fork this repo and submit a pull request.

## 👩‍💻 Author

**Bhavana Priya**
Instrumentation & Control Engineering Student
Passionate about sustainability, AI, and real-world problem solving

