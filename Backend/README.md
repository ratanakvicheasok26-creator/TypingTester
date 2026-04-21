# ⌨️ TypeRacer — Typing Speed Test

A modern, full-stack typing speed test application with real-time feedback,
a leaderboard, and multiple difficulty levels.

---

## 📁 Project Structure

```
typing-tester/
├── backend/
│   ├── app.py               # Flask application — all API routes
│   ├── requirements.txt     # Python dependencies
│   └── typing_tester.db     # SQLite database (auto-created on first run)
│
├── frontend/
│   └── index.html           # Complete single-file frontend (HTML + CSS + JS)
│
└── README.md
```

### File Descriptions

| File | Purpose |
|------|---------|
| `backend/app.py` | Main Flask server. Initialises the SQLite DB, seeds typing texts, and exposes 4 REST endpoints. |
| `backend/requirements.txt` | `flask` and `flask-cors` — the only two dependencies. |
| `frontend/index.html` | Fully self-contained frontend. Works offline (demo mode) and connects to the backend for real scores. |

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.9+  
- pip

### 1. Clone / Download

```bash
# If using git:
git clone <repo-url> typing-tester
cd typing-tester
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the Backend

```bash
python app.py
```

You should see:
```
✅  Database initialised
🚀  Starting Typing Tester API on http://localhost:5000
```

The database (`typing_tester.db`) is automatically created and seeded with
15 sample texts (5 per difficulty) on the first run.

### 4. Open the Frontend

Open `frontend/index.html` in any modern browser.

**Option A — Direct file open (simplest):**
```
File → Open → typing-tester/frontend/index.html
```

**Option B — Serve via Flask (recommended, avoids CORS edge cases):**

Flask already serves the frontend at `http://localhost:5000` — just visit that URL.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/text?difficulty=medium` | Fetch a random typing paragraph |
| `POST` | `/api/results` | Submit a completed test result |
| `GET`  | `/api/leaderboard?difficulty=all&limit=10` | Retrieve top scores |
| `GET`  | `/api/stats` | Global aggregate statistics |

### POST `/api/results` body
```json
{
  "username": "Alice",
  "wpm": 72.5,
  "accuracy": 96.3,
  "errors": 4,
  "duration": 30,
  "difficulty": "medium"
}
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE results (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL,
    wpm        REAL    NOT NULL,
    accuracy   REAL    NOT NULL,
    errors     INTEGER NOT NULL DEFAULT 0,
    duration   INTEGER NOT NULL DEFAULT 60,
    difficulty TEXT    NOT NULL DEFAULT 'medium',
    timestamp  TEXT    NOT NULL
);

CREATE TABLE texts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT    NOT NULL,
    difficulty TEXT    NOT NULL DEFAULT 'medium'
);
```

---

## 🎮 Features

- **Three difficulty levels** — Easy / Medium / Hard with distinct vocabulary and complexity
- **Three timer modes** — 15s / 30s / 60s
- **Real-time feedback** — characters highlight blue (correct) or red (incorrect) as you type
- **Live WPM** — updates every keystroke using the standard 5-chars-per-word formula
- **Accuracy tracking** — percentage of correct keystrokes
- **Backspace support** — undo mistakes mid-test
- **Animated countdown ring** — turns red in the last 5 seconds
- **Result modal** — personalised title based on your WPM score
- **Leaderboard** — top 15 scores, filterable by difficulty
- **Offline/demo mode** — app works fully without the backend (scores just won't persist)
- **Dark theme** with electric lime accent and subtle grid background

---

## 🔮 Suggested Improvements

1. **User accounts** — JWT auth so players own their history
2. **Historical graphs** — Chart.js line graph of WPM over time
3. **Custom texts** — Let users paste their own paragraphs
4. **Multiplayer** — WebSocket race mode (Socket.IO)
5. **Code snippets mode** — Typing mode for programming languages
6. **Sound effects** — Click sounds per keystroke, fanfare on completion
7. **Mobile keyboard support** — Optimise for on-screen keyboards
8. **PostgreSQL migration** — For production deployments
9. **Caps-lock warning** — Detect and alert when CAPS LOCK is on
10. **i18n** — Support non-English typing tests