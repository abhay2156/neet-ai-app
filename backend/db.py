"""
SQLite persistence: the growing question bank and saved attempts.

The bank grows every time the LLM generates a fresh set, so repeated practice
accumulates a larger pool and serves questions from cache before generating new
ones. Attempts are stored so the progress view has real history.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Any

DB_PATH = os.getenv("NEET_DB", os.path.join(os.path.dirname(__file__), "neet.db"))


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id    TEXT NOT NULL,
                subject     TEXT NOT NULL,
                question    TEXT NOT NULL,
                options     TEXT NOT NULL,
                answer      INTEGER NOT NULL,
                explanation TEXT,
                source      TEXT,
                created_at  REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_q_topic ON questions(topic_id);

            CREATE TABLE IF NOT EXISTS attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id    TEXT NOT NULL,
                subject     TEXT NOT NULL,
                mode        TEXT NOT NULL,
                score       INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                duration    INTEGER NOT NULL,
                detail      TEXT,
                created_at  REAL NOT NULL
            );
            """
        )


def _row_to_question(r: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": r["id"],
        "topic_id": r["topic_id"],
        "subject": r["subject"],
        "question": r["question"],
        "options": json.loads(r["options"]),
        "answer": r["answer"],
        "explanation": r["explanation"] or "",
        "source": r["source"] or "unknown",
    }


def save_questions(topic_id: str, subject: str, questions: list[dict], source: str) -> int:
    """Insert questions, skipping exact duplicates within the same topic."""
    if not questions:
        return 0
    now = time.time()
    inserted = 0
    with _conn() as conn:
        existing = {
            r["question"].strip().lower()
            for r in conn.execute(
                "SELECT question FROM questions WHERE topic_id = ?", (topic_id,)
            )
        }
        for q in questions:
            key = q["question"].strip().lower()
            if key in existing:
                continue
            conn.execute(
                "INSERT INTO questions (topic_id, subject, question, options, answer, "
                "explanation, source, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (
                    topic_id,
                    subject,
                    q["question"],
                    json.dumps(q["options"]),
                    q["answer"],
                    q.get("explanation", ""),
                    source,
                    now,
                ),
            )
            existing.add(key)
            inserted += 1
    return inserted


def count_questions(topic_id: str | None = None) -> int:
    with _conn() as conn:
        if topic_id:
            return conn.execute(
                "SELECT COUNT(*) c FROM questions WHERE topic_id = ?", (topic_id,)
            ).fetchone()["c"]
        return conn.execute("SELECT COUNT(*) c FROM questions").fetchone()["c"]


def sample_questions(topic_id: str, limit: int) -> list[dict]:
    """Randomly sample up to `limit` cached questions for a topic."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM questions WHERE topic_id = ? ORDER BY RANDOM() LIMIT ?",
            (topic_id, limit),
        ).fetchall()
    return [_row_to_question(r) for r in rows]


def save_attempt(attempt: dict) -> int:
    with _conn() as conn:
        cur = conn.execute(
            "INSERT INTO attempts (topic_id, subject, mode, score, total, duration, "
            "detail, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                attempt["topic_id"],
                attempt["subject"],
                attempt["mode"],
                attempt["score"],
                attempt["total"],
                attempt["duration"],
                json.dumps(attempt.get("detail", [])),
                time.time(),
            ),
        )
        return cur.lastrowid


def list_attempts(limit: int = 50) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, topic_id, subject, mode, score, total, duration, created_at "
            "FROM attempts ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def stats() -> dict:
    with _conn() as conn:
        total_q = conn.execute("SELECT COUNT(*) c FROM questions").fetchone()["c"]
        total_a = conn.execute("SELECT COUNT(*) c FROM attempts").fetchone()["c"]
        agg = conn.execute(
            "SELECT COALESCE(SUM(score),0) s, COALESCE(SUM(total),0) t FROM attempts"
        ).fetchone()
        per_subject = [
            dict(r)
            for r in conn.execute(
                "SELECT subject, COUNT(*) attempts, COALESCE(SUM(score),0) score, "
                "COALESCE(SUM(total),0) total FROM attempts GROUP BY subject"
            )
        ]
    accuracy = round(100 * agg["s"] / agg["t"], 1) if agg["t"] else 0.0
    return {
        "questions_in_bank": total_q,
        "attempts": total_a,
        "accuracy": accuracy,
        "per_subject": per_subject,
    }
