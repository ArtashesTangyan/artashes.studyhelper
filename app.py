import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# OpenRouter client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.route("/")
def home():
    return "IB Project backend is running!"

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)

        if not data or "prompt" not in data:
            return jsonify({"error": "Missing prompt"}), 400

        prompt = data["prompt"]

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI study helper."},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )

        return jsonify({
            "result": response.choices[0].message.content
        })

    except Exception as e:
        # THIS IS THE MOST IMPORTANT LINE
        print("🔥 ERROR IN /generate:", str(e), flush=True)

        return jsonify({
            "error": "Server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
