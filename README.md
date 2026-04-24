# TypeRacer — Typing Speed Test

Hey there! This is a cool typing speed test app I built. It's got a full-stack setup with real-time feedback, a leaderboard to see how you stack up, and different difficulty levels to challenge yourself.

---

## What's in the Box

```
TypingTester/
├── Backend/
│   ├── app.py               # The main Flask app handling all the API stuff
│   ├── requirements.txt     # Just Flask and Flask-CORS, that's it
│   └── typing_tester.db     # SQLite database that gets created automatically
│
├── Frontend/
│   └── index.html           # Everything frontend in one file - HTML, CSS, JS
│
├── LICENSE                  # Project license
├── README.md                # This file you're reading
├── .git/                    # Git version control
└── .gitignore               # Git ignore rules
```

### Quick File Breakdown

| File                       | What it does                                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `backend/app.py`           | The heart of the backend. Sets up the database, adds some sample texts, and provides 4 API endpoints.       |
| `backend/requirements.txt` | Only needs `flask` and `flask-cors`. Super lightweight.                                                     |
| `frontend/index.html`      | The whole frontend packed into one file. Can run offline for demo, or connect to backend for saving scores. |

---

## Getting Started

### What You Need

- Python 3.9 or newer
- pip (comes with Python)

### Step 1: Get the Code

```bash
# If you're using git:
git clone <repo-url> typing-tester
cd typing-tester
```

### Step 2: Set Up the Backend

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Fire Up the Backend

```bash
python app.py
```

You should see something like:

```
Database initialised
Starting Typing Tester API on http://localhost:5000
```

The database file `typing_tester.db` will be created on first run, and it'll come pre-loaded with 15 sample texts (5 for each difficulty level).

### Step 4: Launch the Frontend

Just open `frontend/index.html` in your favorite browser.

**Easy way:**  
Right-click the file and open it directly.

**Better way (avoids some browser quirks):**  
Since Flask serves the frontend too, just go to `http://localhost:5000` in your browser.

---

## API Stuff

Here's what the backend can do:

| Method | Endpoint                                   | What it does                        |
| ------ | ------------------------------------------ | ----------------------------------- |
| `GET`  | `/api/text?difficulty=medium`              | Grabs a random paragraph for typing |
| `POST` | `/api/results`                             | Saves your test results             |
| `GET`  | `/api/leaderboard?difficulty=all&limit=10` | Shows the top scores                |
| `GET`  | `/api/stats`                               | Gives you overall stats             |

### For the POST `/api/results`

Send JSON like this:

"difficulty": "medium"
}

````

---

## Database Schema

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
````

---

## Features

- **Three difficulty levels** — Easy, Medium, Hard with different vocab and complexity
- **Three timer modes** — 15s, 30s, 60s
- **Real-time feedback** — letters turn blue if correct, red if wrong as you type
- **Live WPM** — updates with every keystroke using the 5-chars-per-word rule
- **Accuracy tracking** — shows how many keystrokes were right
- **Backspace support** — fix mistakes while testing
- **Animated countdown ring** — goes red in the last 5 seconds
- **Result modal** — gets a fun title based on your speed
- **Leaderboard** — top 15 scores, can filter by difficulty
- **Offline/demo mode** — works without backend, but scores don't save
- **Dark theme** with lime accents and a cool grid background
- **Caps-lock warning** — tells you if CAPS LOCK is on
- **i18n support** — can handle non-English texts

---

## Ideas for the Future

1. **User accounts** — Add login so people can track their own progress
2. **Progress charts** — Show WPM trends over time with graphs
3. **Custom texts** — Let users add their own paragraphs to type
4. **Multiplayer mode** — Race against others in real-time
5. **Code typing mode** — Practice typing code snippets
6. **Sound effects** — Add typing sounds and completion fanfare
7. **Mobile friendly** — Better support for phone keyboards
8. **Better database** — Switch to PostgreSQL for bigger setups
9. **More languages** — Support for different languages
