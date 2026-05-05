from flask import Flask, request, jsonify
import json
import os
import time
import secrets

app = Flask(__name__)

FILE = "users.json"

# -------------------------
# LOAD DATA
# -------------------------
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save():
    with open(FILE, "w") as f:
        json.dump(users, f)

def token():
    return secrets.token_hex(16)

def get_user(t):
    for u, d in users.items():
        if d.get("token") == t:
            return u
    return None

# -------------------------
# HOME (TEST)
# -------------------------
@app.route("/")
def home():
    return "Server läuft 🚀"

# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    u = data.get("username")
    p = data.get("password")

    if u in users:
        return {"error": "exists"}, 400

    users[u] = {
        "password": p,
        "token": token(),
        "best": 0,
        "last": 0
    }

    save()
    return {"token": users[u]["token"]}

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    u = data.get("username")
    p = data.get("password")

    if u not in users or users[u]["password"] != p:
        return {"error": "bad login"}, 401

    users[u]["token"] = token()
    save()

    return {"token": users[u]["token"]}

# -------------------------
# SCORE (ANTI CHEAT LIGHT)
# -------------------------
@app.route("/score", methods=["POST"])
def score():
    data = request.json
    t = data.get("token")
    s = int(data.get("score", 0))

    u = get_user(t)
    if not u:
        return {"error": "bad token"}, 403

    now = time.time()

    if now - users[u]["last"] < 2:
        return {"error": "too fast"}, 429

    users[u]["last"] = now

    if s > users[u]["best"]:
        users[u]["best"] = s

    save()

    return {"ok": True}

# -------------------------
# LEADERBOARD
# -------------------------
@app.route("/leaderboard")
def leaderboard():
    board = []

    for u, d in users.items():
        board.append({
            "name": u,
            "score": d.get("best", 0)
        })

    board.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(board[:50])

# -------------------------
# START
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
