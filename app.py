import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

MODEL = "tngtech/deepseek-r1t2-chimera:free"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OpenRouter API key not set"}), 500

    data = request.json
    topic = data.get("topic")
    action = data.get("action")

    if not topic or not action:
        return jsonify({"error": "Missing topic or action"}), 400

    if action == "explanation":
        prompt = f"Explain this topic in simple language: {topic}"
    elif action == "quiz":
        prompt = (
            f"Create a 5-question multiple-choice quiz about: {topic}.\n"
            f"Each question must have A, B, C, D options and show the correct answer."
        )
    else:
        return jsonify({"error": "Invalid action"}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        # 🔴 IMPORTANT: must be your real deployed site
        "HTTP-Referer": "https://ib-personal-project.onrender.com",
        "X-Title": "AI Study Helper",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print("OpenRouter error:", response.text)
            return jsonify({"error": "AI service error"}), 500

        result = response.json()
        text = result["choices"][0]["message"]["content"]

        return jsonify({"result": text})

    except Exception as e:
        print("Backend exception:", str(e))
        return jsonify({"error": "Server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

