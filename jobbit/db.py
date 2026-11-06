"""Jobbit database: jobs, saved answers, and resume paths (SQLite)."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "jobbit.db"

CATEGORIES = ("internship", "full_time", "part_time", "other")
STATUSES = ("unexplored", "applied")

# Only these have a saved default resume. 
# Part-time / other jobs make you choose a resume each time you apply.
RESUME_CATEGORIES = ("internship", "full_time")
_RESUME_SQL = ", ".join(f"'{c}'" for c in RESUME_CATEGORIES)

_CAT_SQL = ", ".join(f"'{c}'" for c in CATEGORIES)
_STATUS_SQL = ", ".join(f"'{s}'" for s in STATUSES)

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS jobs (
    id         INTEGER PRIMARY KEY,
    company    TEXT NOT NULL,
    title      TEXT NOT NULL,
    url        TEXT NOT NULL UNIQUE,
    location   TEXT,
    category   TEXT NOT NULL CHECK (category IN ({_CAT_SQL})),
    status     TEXT NOT NULL DEFAULT 'unexplored'
               CHECK (status IN ({_STATUS_SQL})),
    notes      TEXT,
    resume_used TEXT,
    found_at   TEXT NOT NULL,
    applied_at TEXT
);

CREATE TABLE IF NOT EXISTS answers (
    id         INTEGER PRIMARY KEY,
    question   TEXT NOT NULL UNIQUE,
    answer     TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resumes (
    category  TEXT PRIMARY KEY CHECK (category IN ({_RESUME_SQL})),
    file_path TEXT NOT NULL
);
"""


def _now():
    return datetime.now().isoformat(timespec="seconds")


def get_connection(db_path=DB_PATH):
    """Open the database, creating the data folder and tables if needed."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


# ---------- jobs ----------

def add_job(conn, company, title, url, category, location=None, notes=None):
    """Save a new job as 'unexplored'. Returns True if added, False if the URL already exists."""
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    cur = conn.execute(
        """INSERT OR IGNORE INTO jobs
           (company, title, url, location, category, notes, found_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (company, title, url, location, category, notes, _now()),
    )
    conn.commit()
    return cur.rowcount == 1


def list_jobs(conn, status=None, category=None):
    """List jobs, optionally filtered by status and/or category. Newest first."""
    query, params = "SELECT * FROM jobs WHERE 1=1", []
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY found_at DESC"
    return conn.execute(query, params).fetchall()


def mark_applied(conn, job_id, resume_used=None):
    """Move a job from 'unexplored' to 'applied', recording which resume was used."""
    conn.execute(
        """UPDATE jobs SET status = 'applied', applied_at = ?, resume_used = ?
           WHERE id = ?""",
        (_now(), resume_used, job_id),
    )
    conn.commit()


# ---------- saved answers ----------

def save_answer(conn, question, answer):
    """Store (or update) your answer to an application question."""
    conn.execute(
        """INSERT INTO answers (question, answer, created_at) VALUES (?, ?, ?)
           ON CONFLICT(question) DO UPDATE SET answer = excluded.answer""",
        (question.strip(), answer, _now()),
    )
    conn.commit()


def list_answers(conn):
    return conn.execute("SELECT * FROM answers ORDER BY question").fetchall()


# ---------- resumes ----------

def set_resume(conn, category, file_path):
    """Save the default resume for 'internship' or 'full_time'."""
    if category not in RESUME_CATEGORIES:
        raise ValueError(f"default resumes exist only for {RESUME_CATEGORIES}")
    conn.execute(
        """INSERT INTO resumes (category, file_path) VALUES (?, ?)
           ON CONFLICT(category) DO UPDATE SET file_path = excluded.file_path""",
        (category, str(file_path)),
    )
    conn.commit()


def get_resume(conn, category):
    """Return the saved resume path for a category, or None."""
    row = conn.execute(
        "SELECT file_path FROM resumes WHERE category = ?", (category,)
    ).fetchone()
    return row["file_path"] if row else None


def list_resumes(conn):
    """Return {category: path} for the saved default resumes."""
    rows = conn.execute("SELECT category, file_path FROM resumes").fetchall()
    return {r["category"]: r["file_path"] for r in rows}


def needs_resume_choice(category):
    """True for part_time / other: the user picks a resume for each application."""
    return category not in RESUME_CATEGORIES


def resume_for_job(conn, job):
    """Default resume path for a job, or None if the user must choose
    (part_time / other) or no default has been uploaded yet."""
    if needs_resume_choice(job["category"]):
        return None
    return get_resume(conn, job["category"])