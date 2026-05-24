"""
Typing Tester Backend - Flask Application
==========================================
Clean API-only backend for Render deployment.
Frontend is handled separately by Vercel.
"""

from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import random
from datetime import datetime

# ── App Setup ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'typing_tester.db')

app = Flask(__name__)

# CORS (allow frontend from local and production)
_cors_origins = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:3000",
    os.getenv("FRONTEND_ORIGIN", "")
]
CORS(app, origins=list(filter(None, _cors_origins)))


# ── Database ────────────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                wpm REAL NOT NULL,
                accuracy REAL NOT NULL,
                errors INTEGER NOT NULL DEFAULT 0,
                duration INTEGER NOT NULL DEFAULT 60,
                difficulty TEXT NOT NULL DEFAULT 'medium',
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                difficulty TEXT NOT NULL DEFAULT 'medium'
            );
        """)
        conn.commit()
        _seed_texts(conn)
    finally:
        conn.close()


def _seed_texts(conn):
    count = conn.execute("SELECT COUNT(*) FROM texts").fetchone()[0]
    if count > 0:
        return

    texts = [
        ("A cat sat on the mat and looked outside the window.", "easy"),
        ("Technology is changing the world at a rapid pace every day.", "medium"),
        ("Quantum physics challenges our understanding of reality itself.", "hard"),
    ]

    conn.executemany(
        "INSERT INTO texts (content, difficulty) VALUES (?, ?)",
        texts
    )
    conn.commit()


# ── Config ────────────────────────────────────────────────
_VALID_DIFFICULTIES = ("easy", "medium", "hard")
_MAX_WPM = 300
_ALLOWED_DURATIONS = (15, 30, 60, 120)


# ── Routes ────────────────────────────────────────────────

# ✅ Serve Frontend HTML
@app.route("/")
def home():
    frontend_dir = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
    return send_from_directory(frontend_dir, 'index.html')


# ── Get Random Text ───────────────────────────────────────
@app.route("/api/text", methods=["GET"])
def get_text():
    difficulty = request.args.get("difficulty", "medium").lower()
    if difficulty not in _VALID_DIFFICULTIES:
        difficulty = "medium"

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM texts WHERE difficulty = ?",
        (difficulty,)
    ).fetchall()

    if not rows:
        return jsonify({"error": "No texts found"}), 404

    chosen = random.choice(rows)

    return jsonify({
        "id": chosen["id"],
        "content": chosen["content"],
        "difficulty": chosen["difficulty"]
    })


# ── Submit Result ───────────────────────────────────────
@app.route("/api/results", methods=["POST"])
def submit_result():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ["username", "wpm", "accuracy", "errors", "duration", "difficulty"]
    missing = [f for f in required if f not in data]

    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        username = str(data["username"])[:32].strip() or "Anonymous"
        wpm = float(data["wpm"])
        accuracy = float(data["accuracy"])
        errors = int(data["errors"])
        duration = int(data["duration"])
        difficulty = data["difficulty"]
    except:
        return jsonify({"error": "Invalid data types"}), 400

    if difficulty not in _VALID_DIFFICULTIES:
        difficulty = "medium"

    if not (0 <= wpm <= _MAX_WPM):
        return jsonify({"error": "Invalid WPM"}), 400

    if not (0 <= accuracy <= 100):
        return jsonify({"error": "Invalid accuracy"}), 400

    if duration not in _ALLOWED_DURATIONS:
        return jsonify({"error": "Invalid duration"}), 400

    timestamp = datetime.utcnow().isoformat()

    conn = get_db()
    cur = conn.execute("""
        INSERT INTO results (username, wpm, accuracy, errors, duration, difficulty, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, wpm, accuracy, errors, duration, difficulty, timestamp))

    conn.commit()

    return jsonify({
        "message": "Result saved",
        "id": cur.lastrowid
    }), 201


# ── Leaderboard ─────────────────────────────────────────
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    difficulty = request.args.get("difficulty", "all").lower()

    try:
        limit = min(int(request.args.get("limit", 10)), 50)
    except:
        return jsonify({"error": "Invalid limit"}), 400

    conn = get_db()

    if difficulty == "all":
        rows = conn.execute("""
            SELECT username, wpm, accuracy, errors, duration, difficulty, timestamp
            FROM results
            ORDER BY wpm DESC
            LIMIT ?
        """, (limit,)).fetchall()
    else:
        if difficulty not in _VALID_DIFFICULTIES:
            difficulty = "medium"

        rows = conn.execute("""
            SELECT username, wpm, accuracy, errors, duration, difficulty, timestamp
            FROM results
            WHERE difficulty = ?
            ORDER BY wpm DESC
            LIMIT ?
        """, (difficulty, limit)).fetchall()

    return jsonify([dict(r) for r in rows])


# ── Stats ───────────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db()

    row = conn.execute("""
        SELECT
            COUNT(*) as total_tests,
            ROUND(AVG(wpm), 1) as avg_wpm,
            MAX(wpm) as max_wpm,
            ROUND(AVG(accuracy), 1) as avg_accuracy
        FROM results
    """).fetchone()

    return jsonify(dict(row))


# ── Run Server ───────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("Typing Tester API running...")

    app.run(host="0.0.0.0", port=5000, debug=False)