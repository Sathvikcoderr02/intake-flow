# Intake Workflow (Gemini)

Small web app that runs a structured **intake workflow** on pasted business requests. **Classification** and **information extraction** use the **Google Gemini** API; completeness checks, risk/priority, and next-action recommendations are **rule-based**.

## Prerequisites

- Python 3.11+ recommended
- A [Google AI Studio](https://aistudio.google.com/apikey) API key (`GEMINI_API_KEY`)

## Setup

```bash
cd palni
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=...
```

Optional: set `GEMINI_MODEL` (default `gemini-2.5-flash`). If a model is unavailable in your region/account, pick another from the [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini) list.

## Run

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Open `http://127.0.0.1:8000` — paste a request, click **Run workflow**, review type, extracted fields, validation, risk/priority, recommendation, and trace.

The app loads `.env` from the project root with **`override=True`**, so values in `.env` win over conflicting variables already set in your shell.

## API

`POST /api/process`

```json
{ "request_text": "…" }
```

Returns JSON aligned with `workflow/schemas.py` (`IntakeResponse`).

## Project layout

- `main.py` — FastAPI app and static UI
- `workflow/pipeline.py` — orchestrates steps + trace
- `workflow/classify.py`, `workflow/extract.py` — **Gemini** (JSON mode + Pydantic validation)
- `workflow/validate_completeness.py`, `workflow/risk_priority.py`, `workflow/recommend.py` — rules
- `workflow/llm.py` — Gemini client configuration

## Security

Do **not** commit `.env` or real API keys. Only `.env.example` is tracked.

## Submission checklist (coding test)

1. Push to a **public** GitHub repo (no secrets in history).
2. README with setup/run (this file).
3. Share the repo link as instructed by the test organizer.
