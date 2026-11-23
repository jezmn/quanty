# Quanty

Compare your intuition against the math. Eight rounds of counter-intuitive
probability and statistics questions: you guess first, then the app shows the
exact formula and runs a Monte Carlo simulation to prove it.

Note: educational project.

## Rounds

1. **Birthday paradox**: how many people until two share a birthday?
2. **Monty Hall**: stay or switch?
3. **Medical test**: positive result, but how likely are you actually sick?
4. **Gambler's fallacy**: does the coin "owe" you a tails?
5. **Central Limit Theorem**: sample means turn gaussian, watch it happen.
6. **Frequency tables**: grouped data with Sturges' rule, full stats.
7. **Regression**: linear vs. quadratic, model selection by PRESS.
8. **Confidence intervals**: what "95 % confidence" actually means.

**Scoring**: guesses on rounds 1, 3, 4 and 8 are compared against the theoretical
value; the score is 100 minus your average error in percentage points.

Every round has a preset dataset button and per-round theory in `ROUNDS.md`.

## Stack

- **Backend:** Python / FastAPI (numpy for the math, all simulations server-side)
- **Frontend:** plain HTML with Alpine.js, Tailwind and Chart.js (vendored locally, no CDNs)
- **Tests:** 53 tests with pytest, including hand-computed cross-checks per round

## Quick start

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app
# open http://localhost:8000
```

With live reload during development:

```bash
uvicorn backend.main:app --reload
```

Run the tests:

```bash
pytest
```

## API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/birthday` | Birthday paradox simulation |
| POST | `/api/monty-hall` | Stay vs. switch simulation |
| POST | `/api/bayes` | Bayes' theorem with simulated population |
| POST | `/api/gambler` | Streak tracking simulation |
| POST | `/api/clt` | Sample means distribution |
| POST | `/api/frequencies` | Grouped frequency table |
| POST | `/api/regression` | Linear/quadratic fit with PRESS |
| POST | `/api/confidence` | Interval + coverage simulation |
| GET | `/api/health` | Health check |

## Project structure

```
backend/
  main.py          # FastAPI app and static serving
  models.py        # input validation (pydantic)
  ratelimit.py     # per-IP rate limit on /api/*
  renderer.py      # injects section partials into index.html
  simulations/     # one module per round
frontend/
  index.html       # shell
  sections/        # one partial per theme
  js/              # app state, chart helpers, round logic
  css/             # styles
  vendor/          # Alpine, Tailwind, Chart.js and fonts, served locally
tests/
```
