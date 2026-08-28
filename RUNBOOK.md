# Live Demo Runbook

**Session:** From Classroom to Cloud: Building and Deploying AI-Powered SaaS Products
**Where:** SRIT Anantapur, Ground Floor, APJ Abdul Kalam Block
**When:** 28 Aug 2026, 10:00 AM - 12:30 PM IST
**Demo slot:** roughly 60-75 minutes in, after the architecture section

---

## Facts you need on stage

| Thing | Value |
| ----- | ----- |
| Live URL (UI) | https://cavius-live-demo-2s5qa.ondigitalocean.app |
| Status JSON | https://cavius-live-demo-2s5qa.ondigitalocean.app/health |
| GitHub repo | https://github.com/koushikchaganti/cavius-live-demo |
| DO app ID | `2a683432-79e7-4f41-a01f-86a451d1aed9` |
| DO account | Cavius Technologies (`doctl` context `default`) |
| Region | Bangalore (`blr`) - closest DC to Anantapur |
| Instance | Shared 1 vCPU / 512 MB, $5/month |
| First build time | 1m 42s (measured, not estimated) |

Every `doctl` command below needs `--context default`. The other context
(`blink`) is a different DigitalOcean team and does not have this app.

---

## Pre-session checklist

Do all of this **before** you walk in, not on stage.

- [ ] `curl https://cavius-live-demo-2s5qa.ondigitalocean.app/health` returns
      `"claude_key_configured": true`. This one field is your whole preflight
      for the AI endpoint and costs nothing to check.
- [ ] Open the live URL in a browser. The key chip reads "Claude key
      configured" in teal, and the **Ask Claude** button is enabled. If the
      key is missing the button is deliberately disabled, so you cannot walk
      into a failed request in front of the room.
- [ ] Ask one question through the UI and confirm you get an answer plus the
      token and cost metrics
- [ ] Browser tabs open, in this order, left to right:
      1. GitHub repo, `main.py` open, ready to click Edit
      2. DigitalOcean app dashboard, Activity tab
      3. The live URL
      4. A terminal, large font, in this repo directory
- [ ] Terminal font bumped to at least 18pt. Back row cannot read 12pt.
- [ ] Screen recording of a successful full run saved locally (see "Fallback")
- [ ] Phone hotspot on and tested, in case venue wifi dies

---

## Set the key (one time, before the session)

The app is deployed and healthy, but `/ask` returns 500 until the Claude API
key is set as an encrypted env var. Two ways:

**CLI (fastest).** With `ANTHROPIC_API_KEY` exported in your shell:

```bash
bash /tmp/set-cavius-key.sh
```

That updates the app spec with the key as a `SECRET`, waits for the redeploy,
and then calls `/ask` to prove it works.

**Dashboard (if you would rather click).** DigitalOcean -> Apps ->
`cavius-live-demo` -> Settings -> `api` component -> Environment Variables ->
Edit -> add `ANTHROPIC_API_KEY`, tick **Encrypt**, Save. The app redeploys
automatically.

Either way, verify:

```bash
curl -X POST https://cavius-live-demo-2s5qa.ondigitalocean.app/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is agentic AI in one sentence?"}'
```

---

## Optional: turn on true push-to-deploy

Right now the app pulls from the **public git clone URL**, because
DigitalOcean does not yet have GitHub authorized on the Cavius account. That
means a push does **not** auto-trigger a build; you trigger it yourself with
one command (which is honestly a cleaner thing to narrate on stage anyway).

If you want the real auto-deploy-on-push behaviour, do this before the session:

1. DigitalOcean -> Apps -> Create App -> GitHub -> **Authorize DigitalOcean**,
   grant access to `koushikchaganti/cavius-live-demo`. Then cancel out of the
   create flow - you only needed the authorization.
2. Then apply the GitHub-source spec:

```bash
doctl apps update 2a683432-79e7-4f41-a01f-86a451d1aed9 \
  --context default --spec .do/app.yaml --wait
```

`.do/app.yaml` has `deploy_on_push: true`. Note it does **not** carry the key
value, so re-run the key step afterwards, or add `value:` under the
`ANTHROPIC_API_KEY` entry in a local (uncommitted) copy of the spec.

If step 2 errors, stop. Do not debug this on stage - the manual trigger below
works fine and the audience cannot tell the difference.

---

## The live demo, minute by minute

**0:00 - Show the running product first.** Open the live URL. It is a real
page, not a JSON blob. "This is running in a Bangalore data centre, about
200 km from this room. Seventy lines of Python and one HTML file."

**0:01 - Show the code.** Terminal: `cat main.py`. Walk them through exactly
three things and resist the urge to add a fourth:
- `@app.get("/")` and `@app.post("/ask")` - a route is just a function
- `client.messages.create(...)` - the AI part is one function call
- `anthropic.Anthropic()` reads the key from the **environment**, never from
  the source file. Say the sentence: "The moment you hard-code a key, you
  have shipped it to everyone who can read your repo."

**0:03 - Call the AI endpoint.** Take a question shouted from the room, type
it into the box, and hit **Ask Claude** (or Cmd/Ctrl+Enter). While it thinks,
say what is happening: the browser posts to your API, your API calls Claude,
the answer comes back.

When it lands, point at the four metrics under the answer. "Input tokens,
output tokens, round trip, and the actual dollar cost of the question you
just asked. That is your unit economics. Every AI product you will ever
build is this number multiplied by your user count."

If you would rather show the raw API too, the same call from a terminal:

```bash
curl -s -X POST https://cavius-live-demo-2s5qa.ondigitalocean.app/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "THEIR QUESTION HERE"}' | python3 -m json.tool
```

Worth saying: the UI and the curl hit the *same* endpoint. The browser is
just one client.

**0:06 - Now change it live.** Open `main.py` on GitHub, click the pencil, and
change:

```python
DEMO_LABEL = "Live from SRIT Anantapur"
```

to something the room chooses, e.g.

```python
DEMO_LABEL = "Changed live in front of CSE 2nd year, 28 Aug 2026"
```

Commit straight to `main` with the message `change demo label live on stage`.

**0:08 - Ship it.** In the terminal:

```bash
doctl apps create-deployment 2a683432-79e7-4f41-a01f-86a451d1aed9 \
  --context default
```

(If you enabled push-to-deploy above, skip this - the push already triggered
it. Just switch to the Activity tab.)

Switch to the DigitalOcean Activity tab. Narrate what is actually happening
while it builds: pull the repo, detect Python, install `requirements.txt`,
build a container image, health-check `/`, then swap traffic to the new
container with no downtime. "Nobody SSH'd into a server. Nobody copied a
file. This is what deployment looks like in 2026."

**0:10 - The payoff.** Build finishes in under two minutes. Reload the live
URL. The new label is there, in large type at the top of the page. Let the
room react.

**0:11 - Land the point.** "Between classroom and cloud there is no wall.
There is a repo, a build, and a URL. Everything else you will learn - RLS,
queues, Kubernetes, observability - is about doing this safely at scale for
paying customers."

---

## Fallback plans

**Record a backup now.** Before the session, do one full successful run
(edit -> deploy -> refresh) with QuickTime screen recording on. If anything
fails live, play the recording and narrate over it. Nobody minds. A speaker
frozen at a terminal for four minutes is the only real failure mode.

**If the venue wifi dies mid-demo:**
Say: "This is the part of the job nobody puts on a slide. The deploy is
already running in Bangalore whether or not this room has internet. Let me
show you the recording, and we will refresh the live URL on my phone hotspot
at the end." Switch to the recording. Do not spend more than 30 seconds
troubleshooting the network in front of 100 students.

**If the build fails on stage:** Click into the failed deployment, put the
build log on screen, and read the error out loud. Then say: "This is the
actual skill. Not avoiding errors, reading them." Then either fix it if the
error is obvious in ten seconds, or roll back:

```bash
doctl apps list-deployments 2a683432-79e7-4f41-a01f-86a451d1aed9 \
  --context default
```

and redeploy the last ACTIVE deployment from the dashboard.

**If `/ask` fails on stage:** The key is missing or the API is rate-limiting.
The error appears in the answer area in red with the reason. Do not debug it
live. The redeploy half of the demo does not touch the Claude API at all, so
run that instead and show the answer from your recording.

**A note on status codes**, in case you are asked or something looks odd:
App Platform's edge intercepts 502, 503 and 504 responses from the app and
replaces them with a generic DigitalOcean error page, so the JSON reason
never reaches the browser. Every server-side error in this app therefore
returns 500 with a readable `detail`. This is a genuinely good five-second
aside about the difference between your app's errors and your platform's.

---

## After the session

The app costs $5/month. Either keep it as a reference for students who ask
for the repo, or tear it down:

```bash
doctl apps delete 2a683432-79e7-4f41-a01f-86a451d1aed9 --context default
```

If you keep it, rotate the Claude API key afterwards - the repo is public and
students will fork it.
