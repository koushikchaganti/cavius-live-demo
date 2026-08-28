# Cavius Live Demo

A minimal FastAPI app with one Claude-powered endpoint, built for the
"From Classroom to Cloud: Building and Deploying AI-Powered SaaS Products"
seminar at SRIT Anantapur (28 Aug 2026).

Two endpoints, about 70 lines of Python:

| Method | Path   | What it does                                  |
| ------ | ------ | --------------------------------------------- |
| GET    | `/`    | Health check. Shows the current `DEMO_LABEL`. |
| POST   | `/ask` | Sends a question to Claude, returns an answer.|

## Run locally

Needs Python 3.10 or newer (the `anthropic` 1.x SDK requires it).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # paste your real key into .env
export $(grep -v '^#' .env | xargs)
uvicorn main:app --reload
```

Test it:

```bash
curl http://localhost:8000/
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is agentic AI in one sentence?"}'
```

## Deploy to DigitalOcean App Platform

The full spec is in `.do/app.yaml`. See `RUNBOOK.md` for the minute-by-minute
live session script and the fallback plan.

With `doctl`:

```bash
doctl apps create --spec .do/app.yaml
doctl apps list
```

Then set `ANTHROPIC_API_KEY` as an **encrypted (SECRET)** env var, either in the
DO dashboard under Settings, or by passing a spec copy that includes the value.

Via the dashboard instead: **Apps -> Create App -> GitHub -> select this repo**.
App Platform auto-detects `requirements.txt` and Python; set the run command to
`uvicorn main:app --host 0.0.0.0 --port 8080`.

## The live demo moment

`deploy_on_push: true` in the spec means App Platform rebuilds on every push to
`main`. On stage: edit `DEMO_LABEL` in `main.py`, commit, push, and reload `/`
about two minutes later to watch the change go live.
