"""
Cavius Live Demo - SRIT Anantapur, 28 Aug 2026
"From Classroom to Cloud: Building and Deploying AI-Powered SaaS Products"

A minimal FastAPI app with one AI-powered endpoint, built for a live
deploy-on-stage demo to DigitalOcean App Platform.

Routes:
  GET  /        -> the demo UI (single HTML page, no build step)
  GET  /health  -> JSON status, including whether the API key is configured
  POST /ask     -> takes a question, returns a Claude-generated answer

DEMO TIP: change DEMO_LABEL below during the live session, commit, and
push. DigitalOcean App Platform auto-redeploys in ~2 min. Reload "/" on
stage to show the change go live.
"""

import os
from pathlib import Path

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Cavius Live Demo")

# Change this line live during the demo to show an auto-redeploy.
DEMO_LABEL = "Live from SRIT Anantapur"

MODEL = "claude-opus-5"

# The key comes from the environment. On DigitalOcean it is set as an
# encrypted (SECRET) env var. Never hard-code a key in source.
# .strip() matters: a trailing newline pasted into a dashboard field is a
# real and very annoying way to lose an afternoon.
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None


# Read the page once at startup rather than on every request.
INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text()


class Question(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX_HTML


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": f"Cavius live demo is running on DigitalOcean App Platform - {DEMO_LABEL}",
        "demo_label": DEMO_LABEL,
        "model": MODEL,
        # Lets you confirm the secret is wired without spending a token.
        "claude_key_configured": client is not None,
    }


@app.post("/ask")
def ask(payload: Question):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    if client is None:
        # Deliberately 500, not 503. App Platform's edge intercepts 502, 503
        # and 504 from the app and replaces the body with its own error page,
        # so the JSON detail never reaches the caller.
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is not set on this deployment",
        )

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            # "low" effort keeps the on-stage response fast.
            output_config={"effort": "low"},
            system="Answer in at most three short sentences. Be concrete.",
            messages=[{"role": "user", "content": payload.question}],
        )
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY is missing or invalid")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limited by the Claude API, try again")
    except anthropic.APIStatusError as e:
        # Surface the API's own message. This is a teaching demo, not a
        # hardened product: a readable error on screen beats a mystery.
        print(f"Claude API error {e.status_code}: {e.message}", flush=True)
        raise HTTPException(
            status_code=500,
            detail=f"Claude API error {e.status_code}: {e.message}",
        )
    except anthropic.APIConnectionError:
        raise HTTPException(status_code=500, detail="Could not reach the Claude API")

    answer = "".join(block.text for block in response.content if block.type == "text")
    return {
        "question": payload.question,
        "answer": answer,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
