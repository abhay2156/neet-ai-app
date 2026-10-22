"""
LLM client for generating NEET MCQs.

Works with any OpenAI-compatible /chat/completions endpoint. Configure via
environment variables (see .env.example):

    LLM_API_KEY    - your API key (required to leave demo mode)
    LLM_BASE_URL   - default: https://api.sarvam.ai/v1
    LLM_MODEL      - default: sarvam-m
    LLM_TIMEOUT    - seconds, default 90

The client asks the model for a strict JSON payload and parses it defensively,
because models sometimes wrap JSON in prose or code fences.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx

try:
    from dotenv import load_dotenv

    # Load .env from the project root (parent of backend/) if present.
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
except Exception:  # noqa: BLE001 - dotenv is optional
    pass

DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.sarvam.ai/v1")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "sarvam-m")
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "90"))


def api_key() -> str | None:
    return os.getenv("LLM_API_KEY") or None


def is_live() -> bool:
    """True when a real API key is configured (i.e. not demo mode)."""
    return bool(api_key())


SYSTEM_PROMPT = (
    "You are an expert NEET (Indian medical entrance) question setter. "
    "You write accurate, NCERT-aligned multiple-choice questions with exactly "
    "four options and one unambiguous correct answer. You always reply with "
    "valid JSON only, no prose, no markdown fences."
)


def _build_user_prompt(topic: dict[str, Any], count: int, difficulty: str) -> str:
    key_points = "\n".join(f"- {k}" for k in topic.get("key_points", []))
    return (
        f"Create {count} unique NEET-style multiple-choice questions on the topic "
        f"\"{topic['title']}\" (subject: {topic['subject']}, unit: {topic['unit']}).\n"
        f"Difficulty: {difficulty}.\n\n"
        f"Topic summary for grounding:\n{topic.get('summary','')}\n\n"
        f"Key points to cover:\n{key_points}\n\n"
        "Rules:\n"
        "- Exactly 4 options per question, only one correct.\n"
        "- Cover a spread of sub-concepts, not the same fact repeatedly.\n"
        "- Include a short explanation (1-2 sentences) for the correct answer.\n"
        "- Do not number the options inside the text.\n\n"
        "Return JSON exactly in this shape:\n"
        '{"questions": [{"question": "...", "options": ["...", "...", "...", "..."], '
        '"answer": 0, "explanation": "..."}]}\n'
        "where \"answer\" is the 0-based index of the correct option."
    )


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model reply, tolerating fences/prose."""
    text = text.strip()
    # Strip markdown code fences if present.
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fall back to the outermost {...} span.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise ValueError("Model did not return parseable JSON")


def _normalise(questions: list[dict]) -> list[dict]:
    """Validate and clean a list of raw question dicts."""
    clean = []
    for q in questions:
        opts = q.get("options") or []
        if not isinstance(opts, list) or len(opts) != 4:
            continue
        try:
            ans = int(q.get("answer"))
        except (TypeError, ValueError):
            continue
        if ans < 0 or ans > 3:
            continue
        text = str(q.get("question", "")).strip()
        if not text:
            continue
        clean.append(
            {
                "question": text,
                "options": [str(o).strip() for o in opts],
                "answer": ans,
                "explanation": str(q.get("explanation", "")).strip(),
            }
        )
    return clean


async def generate_questions(
    topic: dict[str, Any], count: int = 20, difficulty: str = "NEET standard"
) -> list[dict]:
    """Ask the LLM for `count` MCQs on `topic`. Raises on failure."""
    key = api_key()
    if not key:
        raise RuntimeError("No LLM_API_KEY configured")

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(topic, count, difficulty)},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    url = DEFAULT_BASE_URL.rstrip("/") + "/chat/completions"

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code >= 400:
            # Some providers reject response_format; retry once without it.
            payload.pop("response_format", None)
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content)
    questions = _normalise(parsed.get("questions", []))
    if not questions:
        raise ValueError("Model returned no usable questions")
    return questions
