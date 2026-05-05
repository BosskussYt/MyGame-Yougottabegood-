# =========================
# FULL ONLINE GAME BACKEND
# LOGIN + LEADERBOARD + BASIC ANTI CHEAT
# =========================

from flask import Flask, request, jsonify
import os
import json
import time
import secrets

app = Flask(__name__)

# -------------------------
# DATA FILES
# -------------------------
USERS_FILE = "users.json"

# username -> {password, token, best_score, last_submit}
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# -------------------------
# HELPERS
# -------------------------
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)


def generate_token():
    return secrets.token_hex(16)


def get_user_by_token(token):
    for username, data in users.items():
        if data.get("token") == token:
            return username
    return None

# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"error": "missing fields"}, 400

    if username in users:
        return {"error": "user exists"}, 400

    token = generate_token()

    users[username] = {
        "password": password,
        "token": token,
        "best_score": 0,
        "last_submit": 0
    }

    save_users()

    return {"token": token}

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users.get(username)

    if not user or user["password"] != password:
        return {"error": "invalid login"}, 401

    # new token each login
    token = generate_token()
    user["token"] = token

    save_users()

    return {"token": token}

# -------------------------
# SUBMIT SCORE (ANTI CHEAT)
# -------------------------
@app.route("/score", methods=["POST"])
def score():
    data = request.json
    token = data.get("token")
    score = int(data.get("score", 0))

    username = get_user_by_token(token)
    if not username:
        return {"error": "invalid token"}, 403

    user = users[username]

    now = time.time()

    # anti spam (1 submission per 3 sec)
    if now - user["last_submit"] < 3:
        return {"error": "too fast"}, 429

    user["last_submit"] = now

    # only accept higher scores
    if score > user["best_score"]:
        user["best_score"] = score

    save_users()

    return {"status": "ok", "best": user["best_score"]}

# -------------------------
# LEADERBOARD
# -------------------------
@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    board = []

    for username, data in users.items():
        board.append({
            "name": username,
            "score": data.get("best_score", 0)
        })

    board.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(board[:50])

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return "Game Server Running 🚀"

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
