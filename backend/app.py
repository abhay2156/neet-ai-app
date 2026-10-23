"""
NEET AI — FastAPI backend.

Run:
    uvicorn app:app --reload --port 8000

Endpoints:
    GET  /api/meta                 runtime info (demo mode?, model, bank size)
    GET  /api/subjects             subjects with topic counts
    GET  /api/topics?subject=      topic list (optionally filtered)
    GET  /api/topics/{topic_id}    one topic with its explanation
    POST /api/practice             build a practice set for a topic
    POST /api/attempts             save a completed attempt
    GET  /api/attempts             attempt history
    GET  /api/stats                aggregate progress
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import db
import llm
import topics as topics_mod
from demo_bank import DEMO_BANK

app = FastAPI(title="NEET AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Create tables on import — idempotent, and works whether the app is started by
# uvicorn or driven directly by a test client.
db.init_db()


# ---------------------------------------------------------------- request models

class PracticeRequest(BaseModel):
    topic_id: str
    count: int = Field(default=20, ge=1, le=50)
    difficulty: str = "NEET standard"


class AttemptRequest(BaseModel):
    topic_id: str
    subject: str
    mode: str = "practice"
    score: int
    total: int
    duration: int = 0
    detail: list[dict[str, Any]] = []


# ---------------------------------------------------------------- meta / topics

@app.get("/api/meta")
def meta():
    return {
        "demo_mode": not llm.is_live(),
        "model": llm.DEFAULT_MODEL,
        "questions_in_bank": db.count_questions(),
    }


@app.get("/api/subjects")
def subjects():
    out = []
    for sid, meta in topics_mod.SUBJECTS.items():
        out.append(
            {
                "id": sid,
                "name": meta["name"],
                "color": meta["color"],
                "topic_count": len(topics_mod.TOPICS.get(sid, [])),
            }
        )
    return out


@app.get("/api/topics")
def list_topics(subject: str | None = None):
    items = topics_mod.all_topics()
    if subject:
        items = [t for t in items if t["subject"] == subject]
    # Light payload for listing.
    return [
        {
            "id": t["id"],
            "title": t["title"],
            "unit": t["unit"],
            "weightage": t["weightage"],
            "subject": t["subject"],
            "summary": t["summary"],
            "in_bank": db.count_questions(t["id"]),
        }
        for t in items
    ]


@app.get("/api/topics/{topic_id}")
def get_topic(topic_id: str):
    t = topics_mod.get_topic(topic_id)
    if not t:
        raise HTTPException(404, "Unknown topic")
    return {**t, "in_bank": db.count_questions(topic_id)}


# ---------------------------------------------------------------- practice

def _seed_demo(topic: dict) -> int:
    """Seed the generic demo bank under a topic (demo mode only)."""
    pool = DEMO_BANK.get(topic["subject"], [])
    return db.save_questions(topic["id"], topic["subject"], pool, source="demo")


@app.post("/api/practice")
async def practice(req: PracticeRequest):
    topic = topics_mod.get_topic(req.topic_id)
    if not topic:
        raise HTTPException(404, "Unknown topic")

    have = db.count_questions(req.topic_id)
    source = "cache"

    if have < req.count:
        if llm.is_live():
            need = req.count - have
            try:
                fresh = await llm.generate_questions(topic, count=need + 5, difficulty=req.difficulty)
                added = db.save_questions(req.topic_id, topic["subject"], fresh, source="llm")
                source = "llm" if added else "cache"
            except Exception as exc:  # noqa: BLE001 - surface as 502 to client
                logging.exception("Question generation failed for topic %s", req.topic_id)
                # If generation fails but we have some cache, still serve it.
                if have == 0:
                    raise HTTPException(502, f"Question generation failed: {exc}")
                source = "cache"
        else:
            added = _seed_demo(topic)
            source = "demo" if added else "cache"

    questions = db.sample_questions(req.topic_id, req.count)
    if not questions:
        raise HTTPException(502, "No questions available for this topic")

    return {
        "topic": {"id": topic["id"], "title": topic["title"], "subject": topic["subject"]},
        "source": source,
        "count": len(questions),
        "questions": questions,
    }


# ---------------------------------------------------------------- attempts

@app.post("/api/attempts")
def create_attempt(req: AttemptRequest):
    aid = db.save_attempt(req.model_dump())
    return {"id": aid, "saved": True}


@app.get("/api/attempts")
def get_attempts(limit: int = 50):
    return db.list_attempts(limit)


@app.get("/api/stats")
def get_stats():
    return db.stats()


# ---------------------------------------------------------------- static frontend

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
