# Support Copilot

Internal AI tooling for **Technical Support** (ticket triage) and **Technical Account Management** (account health briefs). Built with the official synthetic dataset only: 500 tickets, 50 accounts, and a 9-doc product knowledge base.

Design decisions (failure modes, latency, PII, 10× scale) are in [DESIGN_NOTE.md](DESIGN_NOTE.md).

## Live demo

After you deploy on Streamlit Community Cloud, put the public URL here and in your email to Zycus.

Main file path for deploy: `ui/app.py`

## Setup

Python 3.10+. From the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

On macOS/Linux: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env`

Put your OpenAI key in `.env`. Never commit `.env`.

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
DATASET_AS_OF=2026-05-22
```

`DATASET_AS_OF` is the frozen “today” for last-90-days ticket windows. The mock tickets end on 2026-05-22; using the wall clock would return none.

## Run

Single entry point: `python -m support_copilot <command>`

**Task 1 — triage a ticket**

```powershell
python -m support_copilot triage --text "DataBridge Pro pipeline failed with ERR_CONNECTION_TIMEOUT in production."
python -m support_copilot triage --stream --text "DataBridge Pro pipeline failed with ERR_CONNECTION_TIMEOUT in production."
```

Or `--subject` and `--body`. Output includes product, category, P1–P4 urgency, reasoning, responder team, draft first response, and knowledge-base matches.

**Task 2 — TAM account brief**

```powershell
python -m support_copilot brief ACC-2944
```

`ACC-2944` is a churning account. Output is an executive summary, quote-backed risks, and talking points.

**Task 3 — eval harness**

```powershell
python -m support_copilot eval
```

Writes `reports/eval_report.json` and `reports/eval_report.md`. Latest checked-in run: **10/10**, quality **1.0**. Needs an OpenAI key.

**Local / CI smoke checks (no API key)**

```powershell
python -m support_copilot smoke
```

GitHub Actions runs this on every push.

**UI**

```powershell
python -m support_copilot ui
```

Streamlit app with a triage form and an account-brief picker.

## Dataset notes

- Ticket `account_id` values rarely match `accounts.json`. Briefs join by **company name** first, then id.
- Gold labels on tickets (`product`, `category`, `urgency`) are not passed into the live triage prompt. They exist only in the dataset file.

## Prompts

Current versions: `triage_v1`, `brief_v1` in `prompts/`. Changes are recorded in `prompts/CHANGELOG.md`.


Deployed link: https://4fyi8rnstr9kcgiaanpny4.streamlit.app/
