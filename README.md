# NEET AI — Topic Explorer & Practice Sets

A small web app for NEET prep. Browse syllabus topics with short explanations,
then generate a fresh set of 20 MCQs on any topic and practise them in
practice mode or timed exam mode. Every attempt is scored, reviewed with
explanations, and saved to your progress history.

- **Backend:** Python + FastAPI, SQLite for storage, any OpenAI-compatible LLM
  for question generation.
- **Frontend:** plain HTML/CSS/JS — no build step, no npm.
- **Question bank:** grows as you use it. Generated questions are cached, so
  repeated practice accumulates a larger pool and reuses what it already has.

---

## Quick start (2 minutes)

```bash
cd neet-ai-app
python3 -m venv .venv && source .venv/bin/activate     # optional but recommended
pip install -r requirements.txt

cp .env.example .env        # then put your LLM API key in .env
cd backend
uvicorn app:app --reload --port 8000
```

Open <http://localhost:8000>.

**No API key? It still runs.** With an empty `LLM_API_KEY` the app starts in
*demo mode*: questions come from a small built-in sample bank (20 per subject)
so you can click through the whole flow. The header badge tells you which mode
you're in.

---

## Configuring the question generator

Questions are generated live by any **OpenAI-compatible** chat-completions
endpoint. Set these in `.env`:

| Variable        | Default                      | Notes                                  |
|-----------------|------------------------------|----------------------------------------|
| `LLM_API_KEY`   | *(empty → demo mode)*        | Your provider key.                     |
| `LLM_BASE_URL`  | `https://api.sarvam.ai/v1`   | Any OpenAI-compatible base URL.        |
| `LLM_MODEL`     | `sarvam-m`                   | Model name for that provider.          |
| `LLM_TIMEOUT`   | `90`                         | Seconds.                               |
| `NEET_DB`       | `backend/neet.db`            | SQLite file path.                      |

Examples:

```env
# Sarvam AI (default)
LLM_BASE_URL=https://api.sarvam.ai/v1
LLM_MODEL=sarvam-m

# OpenAI
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Groq
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

The generator asks the model for strict JSON, validates every question (exactly
four options, an in-range answer index), and drops malformed items. If a
generation call fails but cached questions exist, it serves those instead of
erroring.

---

## How it works

```
frontend/                 static UI (served by the backend at /)
  index.html
  styles.css
  app.js
backend/
  app.py                  FastAPI routes + static hosting
  llm.py                  OpenAI-compatible client + JSON parsing
  db.py                   SQLite: question bank + attempts
  topics.py               NEET topic catalogue with explanations
  demo_bank.py            built-in sample questions (demo mode)
  test_app.py             end-to-end smoke test
Dockerfile / docker-compose.yml
```

### API

| Method | Path                  | Purpose                                        |
|--------|-----------------------|------------------------------------------------|
| GET    | `/api/meta`           | demo mode?, model, bank size                   |
| GET    | `/api/subjects`       | subjects with topic counts                     |
| GET    | `/api/topics?subject=`| topic list                                     |
| GET    | `/api/topics/{id}`    | one topic with explanation + key points        |
| POST   | `/api/practice`       | build a set: `{topic_id, count, difficulty}`   |
| POST   | `/api/attempts`       | save a completed attempt                       |
| GET    | `/api/attempts`       | attempt history                                |
| GET    | `/api/stats`          | aggregate accuracy + bank size                 |

### Deep links

You can link straight into a topic or a running test:

```
/?topic=bio-genetics
/?topic=phy-kinematics&start=1&count=20&mode=exam
```

`mode` is `practice` or `exam`. Exam mode runs a countdown of one minute per
question and auto-submits at zero, mirroring NEET's timing.

---

## Tests

```bash
cd backend
python3 test_app.py
```

Runs the full flow in demo mode: subjects → topics → generate a 20-question
set → cache on the second call → save an attempt → read stats back.

---

## Deploying

### Docker (any host)

```bash
docker compose up --build          # then open http://localhost:8000
```

The SQLite file lives on the `neet_data` volume, so the question bank and
attempt history survive restarts. Put your key in `.env` before starting.

### Managed platforms

The app is a standard single-port web service, so it drops onto Render,
Railway, Fly.io, a VPS, or any container host:

- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn app:app --host 0.0.0.0 --port $PORT` (run from `backend/`)
- **Env:** set `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`
- **Storage:** point `NEET_DB` at a persistent volume, or swap SQLite for
  Postgres if you need multiple instances.

Because SQLite is a single file, run **one** instance unless you move to a
shared database.

---

## Extending it

- **Bigger bank:** the cache table `questions` is the bank. Import your own
  rows into it (same columns) or let generation accumulate them.
- **More topics:** add entries to `topics.py` — the UI and API pick them up
  automatically.
- **Harder/easier sets:** `difficulty` is passed to the model; expose it in the
  UI's practice row.
- **Accounts:** attempts are currently global. Add a `user_id` column to
  `attempts` and a login layer for multi-user use.

---

## One honest caveat

Questions produced by an LLM are **not** verified against an official source.
The app validates structure, not factual correctness. For real exam prep,
treat generated questions as a practice aid and cross-check anything that
looks off against NCERT or an authoritative question bank before relying on it.
The topic explanations are concise revision notes, not a substitute for the
textbook either.
