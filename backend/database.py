import sqlite3
import hashlib
import os
from datetime import datetime

DB_NAME = "dsa_analyzer.db"


def _hash_password(password: str, salt: str) -> str:
    """PBKDF2 hashing — no external dependencies needed, reasonably secure for a learning project."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def init_db():
    """Creates tables if they don't exist. Safe to call every time the app starts."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            problem TEXT,
            code TEXT,
            language TEXT,
            approach TEXT,
            pattern TEXT,
            time_complexity TEXT,
            space_complexity TEXT,
            optimization TEXT,
            explanation TEXT,
            created_at TEXT
        )
    """)

    # If the analyses table already existed from before Day 10 (no user_id
    # column), add it now without losing existing data.
    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        pass  # column already exists — safe to ignore

    conn.commit()
    conn.close()


def create_user(username: str, password: str):
    """Returns the new user's id, or None if the username is already taken."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    salt = os.urandom(16).hex()
    password_hash = _hash_password(password, salt)

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt, datetime.now().isoformat(timespec="seconds")))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None  # username already taken
    finally:
        conn.close()


def verify_user(username: str, password: str):
    """Returns the user's id if the password is correct, else None."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    if _hash_password(password, row["salt"]) == row["password_hash"]:
        return row["id"]
    return None


def save_analysis(problem: str, code: str, language: str, result: dict, user_id=None):
    """Saves one analysis result to the database, optionally linked to a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analyses
        (user_id, problem, code, language, approach, pattern, time_complexity, space_complexity, optimization, explanation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        problem,
        code,
        language,
        result.get("approach"),
        result.get("pattern"),
        result.get("time_complexity"),
        result.get("space_complexity"),
        result.get("optimization"),
        result.get("explanation"),
        datetime.now().isoformat(timespec="seconds"),
    ))
    conn.commit()
    conn.close()


def get_stats(user_id=None):
    """
    Returns aggregate stats for the dashboard:
    - total: total number of analyses
    - by_pattern: {pattern_name: count}
    - by_language: {language: count}
    - last_7_days: [{date: "YYYY-MM-DD", count: n}, ...] oldest to newest
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    where_clause = "WHERE user_id = ?" if user_id is not None else ""
    params = (user_id,) if user_id is not None else ()

    cursor.execute(f"SELECT pattern, COUNT(*) as cnt FROM analyses {where_clause} GROUP BY pattern", params)
    by_pattern = {row["pattern"]: row["cnt"] for row in cursor.fetchall()}

    cursor.execute(f"SELECT language, COUNT(*) as cnt FROM analyses {where_clause} GROUP BY language", params)
    by_language = {row["language"]: row["cnt"] for row in cursor.fetchall()}

    # Last 7 days trend (including today), filling in 0 for days with no activity
    day_where = "WHERE user_id = ? AND" if user_id is not None else "WHERE"
    cursor.execute(f"""
        SELECT date(created_at) as day, COUNT(*) as cnt
        FROM analyses
        {day_where} date(created_at) >= date('now', '-6 days')
        GROUP BY day
    """, params)
    counts_by_day = {row["day"]: row["cnt"] for row in cursor.fetchall()}

    from datetime import timedelta
    today = datetime.now().date()
    last_7_days = []
    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).isoformat()
        last_7_days.append({"date": day, "count": counts_by_day.get(day, 0)})

    conn.close()

    total = sum(by_pattern.values())
    return {
        "total": total,
        "by_pattern": by_pattern,
        "by_language": by_language,
        "last_7_days": last_7_days,
    }


def get_history(user_id=None, limit: int = 20, pattern=None):
    """Returns the most recent analyses, newest first. Optionally filtered by user_id and/or pattern."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    params = []
    if user_id is not None:
        conditions.append("user_id = ?")
        params.append(user_id)
    if pattern is not None:
        conditions.append("pattern = ?")
        params.append(pattern)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(limit)

    cursor.execute(f"""
        SELECT id, problem, language, pattern, time_complexity, space_complexity, created_at
        FROM analyses
        {where_clause}
        ORDER BY id DESC
        LIMIT ?
    """, params)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]