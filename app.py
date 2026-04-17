from flask import Flask, render_template, request
from groq import Groq
import random

app = Flask(__name__)

# 🔑 API KEY (अपनी नई key डालना)
client = Groq(api_key="GROQ_API_KEY")

# 🧠 Chat Memory (per user)
chat_memory = {}

# 🧠 Multi-user memory
users = {}

# 🧠 No Repeat System
used_ideas = {}

# 📚 Category-wise Project Ideas
project_ideas = {
    "arduino": [
        {"name": "Smart Irrigation", "desc": "Auto watering system", "materials": "Arduino, soil sensor, pump", "working": "Dry soil → pump ON"},
        {"name": "Obstacle Robot", "desc": "Obstacle avoid robot", "materials": "Arduino, ultrasonic sensor", "working": "Object detect → turn"},
        {"name": "Smart Street Light", "desc": "Auto light system", "materials": "LDR, Arduino", "working": "Dark → ON"},
        {"name": "Fire Alarm", "desc": "Fire detection system", "materials": "Flame sensor, buzzer", "working": "Fire detect → alarm"},
        {"name": "Water Level Indicator", "desc": "Tank level check", "materials": "Wires, buzzer", "working": "Water touch → signal"},
        {"name": "Smart Door Lock", "desc": "Password lock", "materials": "Keypad, Arduino", "working": "Correct code → unlock"},
        {"name": "Temperature Monitor", "desc": "Temp display system", "materials": "Temp sensor", "working": "Sensor → value show"},
        {"name": "Auto Fan", "desc": "Temp based fan", "materials": "Motor, sensor", "working": "Heat ↑ → fan ON"},
        {"name": "Bluetooth Car", "desc": "Mobile control car", "materials": "Arduino, Bluetooth module", "working": "Phone → control"},
        {"name": "Rain Sensor Alarm", "desc": "Rain detection", "materials": "Rain sensor", "working": "Water → alert"}
    ],

    "science": [
        {"name": "Balloon Car", "desc": "Air powered car", "materials": "Balloon, straw", "working": "Air push → move"},
        {"name": "Water Filter", "desc": "Purification model", "materials": "Sand, gravel", "working": "Layer filter"},
        {"name": "Volcano Model", "desc": "Eruption demo", "materials": "Baking soda, vinegar", "working": "Reaction → foam"},
        {"name": "Electric Circuit", "desc": "Basic circuit", "materials": "Battery, wire", "working": "Closed loop → bulb ON"},
        {"name": "Windmill", "desc": "Energy model", "materials": "Paper blades", "working": "Wind → rotation"},
        {"name": "Periscope", "desc": "Mirror view tool", "materials": "Mirrors, box", "working": "Light reflection"},
        {"name": "Solar Cooker", "desc": "Sun cooking model", "materials": "Foil, box", "working": "Sun heat trap"},
        {"name": "Magnet Crane", "desc": "Magnetic lifting", "materials": "Magnet", "working": "Magnet pull"},
        {"name": "Pulley System", "desc": "Lift mechanism", "materials": "Rope, wheel", "working": "Force reduce"},
        {"name": "Hydraulic Lift", "desc": "Water pressure lift", "materials": "Syringe", "working": "ضغط → movement"}
    ],

    "ai": [
        {"name": "Face Detection", "desc": "Face detect system", "materials": "Python, OpenCV", "working": "Camera → detect"},
        {"name": "Voice Assistant", "desc": "AI voice system", "materials": "Python, mic", "working": "Voice → reply"},
        {"name": "Chatbot", "desc": "AI chat system", "materials": "Python", "working": "Input → response"},
        {"name": "Hand Gesture Control", "desc": "Gesture detection", "materials": "Camera", "working": "Hand detect"},
        {"name": "AI Calculator", "desc": "Voice calculator", "materials": "Python", "working": "Voice → solve"},
        {"name": "Object Detection", "desc": "Object identify", "materials": "Camera", "working": "AI detect object"},
        {"name": "Text Reader", "desc": "Text to speech", "materials": "Python", "working": "Text → voice"},
        {"name": "Spam Detector", "desc": "Email filter", "materials": "Dataset", "working": "AI classify"},
        {"name": "Emotion Detector", "desc": "Face emotion detect", "materials": "Camera", "working": "Expression → detect"},
        {"name": "AI Translator", "desc": "Language convert", "materials": "Python API", "working": "Input → translate"}
    ]
}

# 🧠 Update Memory
def update_memory(user_id, user_message):
    if user_id not in users:
        users[user_id] = {"name": "", "class": "", "interest": ""}

    msg = user_message.lower()

    if "mera naam" in msg or "my name is" in msg:
        users[user_id]["name"] = user_message.split()[-1]

    if "class" in msg:
        for i in range(1, 13):
            if str(i) in msg:
                users[user_id]["class"] = str(i)

    if "pasand" in msg or "interest" in msg:
        users[user_id]["interest"] = user_message


# 🤖 Generate Response
def generate_response(user_id, user_message):
    try:
        update_memory(user_id, user_message)

        # 🎯 Guide Mode Detection (FIXED)
        if "kaise banaye" in user_message.lower() or "steps" in user_message.lower():
            guide_mode = True
        else:
            guide_mode = False

        # 🧠 user init
        if user_id not in users:
            users[user_id] = {"name": "", "class": "", "interest": ""}

        user = users[user_id]

        # 💬 chat memory
        if user_id not in chat_memory:
            chat_memory[user_id] = []

        chat_memory[user_id].append({"role": "user", "content": user_message})

        msg = user_message.lower()

        # 🎯 CATEGORY
        category = None
        if "arduino" in msg:
            category = "arduino"
        elif "science" in msg:
            category = "science"
        elif "ai" in msg:
            category = "ai"

        # 🎯 CLASS → LEVEL
        level = "easy"
        if user["class"]:
            try:
                cls = int(user["class"])
                if cls <= 6:
                    level = "easy"
                elif cls <= 8:
                    level = "medium"
                else:
                    level = "hard"
            except:
                pass

        # 🎯 IDEA SYSTEM
        if "idea" in msg or category:

            if not category:
                category = random.choice(list(project_ideas.keys()))

            # 🧠 NO REPEAT
            if user_id not in used_ideas:
                used_ideas[user_id] = []

            available_ideas = [
                idea for idea in project_ideas[category]
                if idea.get("level", "easy") == level
                and idea["name"] not in used_ideas[user_id]
            ]

            if not available_ideas:
                used_ideas[user_id] = []
                available_ideas = project_ideas[category]

            idea = random.choice(available_ideas)
            used_ideas[user_id].append(idea["name"])

            # 🧠 SYSTEM PROMPT
            system_prompt = f"""
Tum AI Kaushal Guru ho 🤖

User Profile:
Name: {user['name']}
Class: {user['class']}
Interest: {user['interest']}

👉 Project Name: {idea['name']}

👉 Description:
{idea['desc']}

👉 Materials:
{idea['materials']}

👉 Working:
{idea['working']}
"""

            # 🔥 Guide Mode Apply (CORRECT PLACE)
            if guide_mode:
                system_prompt += """

👉 Steps to Build:
1. Step by step banana explain karo
2. Simple language use karo
3. Student ko guide karo

👉 Tips:
Easy hacks do

👉 Final Result:
Kya output milega
"""

           

        # 🤖 DEFAULT AI RESPONSE
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are AI Kaushal Guru. Speak simple Hinglish."}
            ] + chat_memory[user_id][-6:]
        )

        reply = response.choices[0].message.content
        chat_memory[user_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("ERROR:", e)
        return "⚠️ Server error aa gaya"

        # 🤖 AI RESPONSE (General Chat)
        system_prompt = f"""
Tum Ai Kaushal Guru ho 🤖

User:
Name: {user['name']}
Class: {user['class']}
Interest: {user['interest']}

Rules:
- Hinglish me baat karo
- Short aur clean reply do
- Friendly teacher tone 😄
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + chat_memory[user_id][-6:]
        )

        reply = response.choices[0].message.content

        chat_memory[user_id].append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("ERROR:", e)
        return "⚠️ Server error aa gaya"


# 🌐 Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    user_id = data.get("user_id", "default_user")

    return generate_response(user_id, user_message)


# ▶️ Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)