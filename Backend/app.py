"""
Typing Tester Backend - Flask Application
==========================================
Main entry point for the backend API server.
Handles routes for texts, results, and leaderboard.
"""

from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS
import sqlite3
import os
import random
from datetime import datetime

# ── App Setup ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DB_PATH = os.path.join(BASE_DIR, 'typing_tester.db')

app = Flask(__name__, static_folder=FRONTEND_DIR)

# FIX (security): Restrict CORS to your frontend origin in production.
# Set the FRONTEND_ORIGIN env var (e.g. "https://mydomain.com").
# Falls back to localhost for local development.
_cors_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
CORS(app, origins=[_cors_origin])


# ── Database ───────────────────────────────────────────────────────────────────

def get_db():
    """
    Return a per-request database connection stored on Flask's g object.
    The connection is automatically closed at the end of each request via
    close_db() registered below — no more file-handle leaks.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """FIX (bug): Close the DB connection at the end of every request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and indexes if they don't exist."""
    # init_db() is called outside a request context, so we open directly here.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS results (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    NOT NULL,
                wpm       REAL    NOT NULL,
                accuracy  REAL    NOT NULL,
                errors    INTEGER NOT NULL DEFAULT 0,
                duration  INTEGER NOT NULL DEFAULT 60,
                difficulty TEXT   NOT NULL DEFAULT 'medium',
                timestamp TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS texts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT    NOT NULL,
                difficulty TEXT    NOT NULL DEFAULT 'medium'
            );

            -- FIX (improvement): Index for fast leaderboard queries.
            CREATE INDEX IF NOT EXISTS idx_results_diff_wpm
                ON results (difficulty, wpm DESC);
        """)
        conn.commit()
        _seed_texts(conn)
    finally:
        conn.close()


def _seed_texts(conn):
    """Insert sample texts if the table is empty."""
    count = conn.execute("SELECT COUNT(*) FROM texts").fetchone()[0]
    if count > 0:
        return

    texts = [
        # ── Easy ─────────────────────────────────────────────────────────────
        # FIX (improvement): Removed personalised name from seed text.
        ("Love Sokunmaltey pinh besdong "
         "and pink. Birds began to sing their morning songs as the world slowly "
         "woke up.", "easy"),

        ("A cat sat on the mat and looked out the window. The rain fell softly on the "
         "street below while she watched the drops race down the glass.", "easy"),

        ("She picked up the book and opened it to the first page. The story began on "
         "a cold winter morning in a small town by the sea.", "easy"),

        ("The dog ran across the field chasing a bright red ball. His tail wagged "
         "with joy as he leapt through the tall green grass.", "easy"),

        ("Every morning he made a cup of tea and sat by the window to read the news. "
         "It was a simple routine that brought him great comfort.", "easy"),

        # ── Medium ───────────────────────────────────────────────────────────
        ("The quick brown fox jumps over the lazy dog near the river bank. "
         "Autumn leaves drifted gently through the crisp afternoon air, settling "
         "silently on the cobblestone path below the old oak tree.", "medium"),

        ("Technology has transformed the way we communicate, learn, and work. "
         "From smartphones to artificial intelligence, innovation continues to "
         "reshape society at an unprecedented pace, raising important questions "
         "about privacy, equity, and the future of human connection.", "medium"),

        ("The explorer navigated through dense jungle terrain, guided only by "
         "a compass and the faint sound of rushing water ahead. Every step "
         "required careful thought as roots and vines obscured the narrow trail.", "medium"),

        ("Music has the remarkable power to evoke deep emotions and transport "
         "listeners to distant memories. A single melody can capture the essence "
         "of an entire era, binding people together across generations and cultures.", "medium"),

        ("The scientist carefully recorded each observation in her notebook, "
         "knowing that even the smallest detail could hold the key to unlocking "
         "a breakthrough discovery that had eluded researchers for decades.", "medium"),

        # ── Hard ─────────────────────────────────────────────────────────────
        ("Quantum entanglement — the phenomenon whereby two particles remain "
         "instantaneously connected regardless of the distance separating them — "
         "fundamentally challenges our classical understanding of causality, "
         "locality, and the very fabric of spacetime itself.", "hard"),

        ("The juxtaposition of Byzantine mosaics against Baroque architecture "
         "in the cathedral's nave created a visually arresting palimpsest of "
         "ecclesiastical history; each epoch's aesthetic philosophy competing "
         "yet simultaneously complementing its predecessor's grand ambitions.", "hard"),

        ("Cryptographic hash functions exhibit deterministic one-way transformations: "
         "arbitrary-length input data maps to fixed-size digest outputs with "
         "avalanche sensitivity, pre-image resistance, and collision improbability — "
         "properties underpinning blockchain immutability and zero-knowledge proofs.", "hard"),

        ("The epistemological distinction between a priori and a posteriori "
         "knowledge — whether justified independently of or through empirical "
         "experience — remains a cornerstone of analytic philosophy, influencing "
         "debates on rationalism, empiricism, and the synthetic-analytic dichotomy.", "hard"),

        ("Mitochondrial dysfunction, characterized by impaired oxidative "
         "phosphorylation and dysregulated reactive oxygen species production, "
         "has been implicated in neurodegenerative pathologies including "
         "Alzheimer's, Parkinson's, and amyotrophic lateral sclerosis.", "hard"),
    ]

    conn.executemany(
        "INSERT INTO texts (content, difficulty) VALUES (?, ?)", texts
    )
    conn.commit()


# ── Helpers ────────────────────────────────────────────────────────────────────

# FIX (improvement): Sanity limits for submitted results.
_VALID_DIFFICULTIES = ('easy', 'medium', 'hard')
_ALLOWED_DURATIONS  = (15, 30, 60, 120)   # seconds — extend as needed
_MAX_WPM            = 300                  # world record is ~216; 300 gives headroom


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the frontend HTML."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/api/text', methods=['GET'])
def get_text():
    """
    Return a random typing text.
    Query params:
        difficulty: easy | medium | hard  (default: medium)
    """
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in _VALID_DIFFICULTIES:
        difficulty = 'medium'

    conn = get_db()
    rows = conn.execute(
        "SELECT id, content, difficulty FROM texts WHERE difficulty = ?",
        (difficulty,)
    ).fetchall()

    if not rows:
        return jsonify({"error": "No texts found"}), 404

    chosen = random.choice(rows)
    return jsonify({
        "id": chosen["id"],
        "content": chosen["content"],
        "difficulty": chosen["difficulty"],
    })


@app.route('/api/results', methods=['POST'])
def submit_result():
    """
    Accept and store a completed typing test result.
    Expected JSON body:
        username, wpm, accuracy, errors, duration, difficulty
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ('username', 'wpm', 'accuracy', 'errors', 'duration', 'difficulty')
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Sanitise / clamp values
    username   = str(data['username'])[:32].strip() or "Anonymous"
    difficulty = data['difficulty'] if data['difficulty'] in _VALID_DIFFICULTIES else 'medium'
    timestamp  = datetime.utcnow().isoformat()

    try:
        wpm      = float(data['wpm'])
        accuracy = float(data['accuracy'])
        errors   = int(data['errors'])
        duration = int(data['duration'])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid numeric fields"}), 400

    # FIX (improvement): Validate numeric ranges.
    if not (0 <= wpm <= _MAX_WPM):
        return jsonify({"error": f"WPM must be between 0 and {_MAX_WPM}"}), 400
    if not (0 <= accuracy <= 100):
        return jsonify({"error": "Accuracy must be between 0 and 100"}), 400
    if errors < 0:
        return jsonify({"error": "Errors cannot be negative"}), 400
    if duration not in _ALLOWED_DURATIONS:
        return jsonify({"error": f"Duration must be one of {_ALLOWED_DURATIONS}"}), 400

    conn = get_db()
    cur = conn.execute(
        """INSERT INTO results (username, wpm, accuracy, errors, duration, difficulty, timestamp)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (username, wpm, accuracy, errors, duration, difficulty, timestamp)
    )
    conn.commit()

    return jsonify({"id": cur.lastrowid, "message": "Result saved successfully"}), 201


@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    """
    Return top scores.
    Query params:
        difficulty: easy | medium | hard | all  (default: all)
        limit: int (default 10, max 50)
    """
    difficulty = request.args.get('difficulty', 'all').lower()

    # FIX (bug): Safe integer parse — returns 400 instead of crashing.
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
    except (ValueError, TypeError):
        return jsonify({"error": "limit must be an integer"}), 400

    conn = get_db()
    if difficulty == 'all':
        rows = conn.execute(
            """SELECT username, wpm, accuracy, errors, duration, difficulty, timestamp
               FROM results
               ORDER BY wpm DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
    else:
        if difficulty not in _VALID_DIFFICULTIES:
            difficulty = 'medium'
        rows = conn.execute(
            """SELECT username, wpm, accuracy, errors, duration, difficulty, timestamp
               FROM results
               WHERE difficulty = ?
               ORDER BY wpm DESC
               LIMIT ?""",
            (difficulty, limit)
        ).fetchall()

    return jsonify([dict(r) for r in rows])


@app.route('/api/stats', methods=['GET'])
def global_stats():
    """Return aggregate statistics for fun display."""
    conn = get_db()
    row = conn.execute(
        """SELECT COUNT(*) as total_tests,
                  ROUND(COALESCE(AVG(wpm), 0), 1)      as avg_wpm,
                  COALESCE(MAX(wpm), 0)                 as max_wpm,
                  ROUND(COALESCE(AVG(accuracy), 0), 1)  as avg_accuracy
           FROM results"""
    ).fetchone()

    # FIX (improvement): COALESCE above ensures no null values reach the client.
    return jsonify(dict(row))


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("  Database initialised")
    print("  Starting Typing Tester API on http://localhost:5000")

    # FIX (security): Debug mode controlled by env var — never hardcoded True.
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=False)