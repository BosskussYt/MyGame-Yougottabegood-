from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

DATA_FILE = "scores.json"

# --- Laden der Daten ---
def load_scores():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# --- Speichern der Daten ---
def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f)

scores = load_scores()

# -------------------------
# SCORE SENDEN
# -------------------------
@app.route("/score", methods=["POST"])
def add_score():
    data = request.json

    entry = {
        "score": data.get("score", 0),
        "name": data.get("name", "Player")
    }

    scores.append(entry)

    # nach Score sortieren (höchste zuerst)
    scores.sort(key=lambda x: x["score"], reverse=True)

    # nur Top 50 behalten
    del scores[50:]

    save_scores(scores)

    return {"status": "ok"}

# -------------------------
# LEADERBOARD HOLEN
# -------------------------
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(scores[:50])

# -------------------------
# START SERVER
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
