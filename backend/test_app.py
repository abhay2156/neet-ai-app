"""Smoke tests for the NEET AI backend (run in demo mode)."""

import os
import tempfile

os.environ["NEET_DB"] = os.path.join(tempfile.gettempdir(), "neet_test.db")
if os.path.exists(os.environ["NEET_DB"]):
    os.remove(os.environ["NEET_DB"])

from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402

client = TestClient(app)


def test_flow():
    meta = client.get("/api/meta").json()
    assert meta["demo_mode"] is True, meta

    subjects = client.get("/api/subjects").json()
    assert len(subjects) == 3, subjects

    topics = client.get("/api/topics?subject=biology").json()
    assert len(topics) >= 5, len(topics)

    topic = client.get("/api/topics/bio-genetics").json()
    assert topic["title"] and topic["summary"], topic

    practice = client.post(
        "/api/practice", json={"topic_id": "bio-genetics", "count": 20}
    ).json()
    assert practice["count"] >= 1
    assert practice["source"] == "demo"
    q = practice["questions"][0]
    assert len(q["options"]) == 4
    assert 0 <= q["answer"] <= 3

    # Second call should serve from cache and not duplicate.
    again = client.post("/api/practice", json={"topic_id": "bio-genetics", "count": 20}).json()
    assert again["source"] == "cache", again["source"]

    # Save an attempt and read stats back.
    att = client.post(
        "/api/attempts",
        json={
            "topic_id": "bio-genetics",
            "subject": "biology",
            "mode": "practice",
            "score": 8,
            "total": 10,
            "duration": 300,
            "detail": [],
        },
    ).json()
    assert att["saved"] is True

    stats = client.get("/api/stats").json()
    assert stats["attempts"] == 1, stats
    assert stats["accuracy"] == 80.0, stats

    # Index page is served.
    idx = client.get("/")
    assert idx.status_code == 200 and "NEET AI" in idx.text

    print("ALL TESTS PASSED")
    print("meta:", meta)
    print("practice count:", practice["count"], "source:", practice["source"])
    print("stats:", stats)


if __name__ == "__main__":
    test_flow()
