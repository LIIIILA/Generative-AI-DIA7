# DIA7 - DIA7-G2

**Class:** DIA7 · **Sub-group:** DIA7-G2 (sub-group 2)

Module *Trustworthy Generative AI* (Next-Generation AI), ESILV, Data & AI major, year 4. One shared repository for TD 1 to TD 3.

## Course pack and environment

- **Course pack:** `2026-10-18-students-1` (18 October 2026), kit `kit-td1`.
- **Database:** `data/boutique.sqlite` (seed 20260925), integrity checked against `data/manifest.json`.
- **Environment:** Python 3 in a virtual environment (`.venv`), Windows PowerShell; SQLite through Python's `sqlite3` module (no `sqlite3` command-line tool needed).
- **Model access:** personal free accounts only — Groq Free plan and OpenRouter `:free` routes (`provider.max_price` at zero). Exact identifiers and parameters in [`modeles-autorises.json`](modeles-autorises.json).

## TD 1 contents

| File | What it holds |
|---|---|
| [`reference-td1.csv`](reference-td1.csv) | The 20 reference queries and their values (`revenue_cents`) |
| [`ref_all.py`](ref_all.py) | Builds the 20 queries, runs them and recomputes every value independently from the CSV files |
| [`check_ref.py`](check_ref.py) | Re-runs each query stored in `reference-td1.csv` and compares it with the recorded value |
| [`traces-td1.csv`](traces-td1.csv) | All raw calls merged under one header (102 lines, all attempts, nature `real`) |
| `traces-A.csv` … `traces-E.csv`, `state-A.jsonl` … `state-E.jsonl` | Source traces and state files of each operator, kept unchanged |
| [`model-question-comparison-en.csv`](model-question-comparison-en.csv) | One final row per model/question (100 rows) with the cause of each failure |
| [`pivot-td1.csv`](pivot-td1.csv) | Models x questions view of the comparison file (a view, not a second entry) |
| [`five-model-summary-en.csv`](five-model-summary-en.csv) | Public index, prices, access and results by question family for the five models |
| [`prompt-td1.md`](prompt-td1.md) | The prompt as used: system message and user template, identical for all models |
| [`build_step3.py`](build_step3.py), [`fill_summary.py`](fill_summary.py) | Consolidation scripts (trace merge, comparison skeleton, summary columns) |

## Reproducing TD 1

Run every command from the repository root.

```powershell
# 1. Virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Local integrity check (no network call)
python check_access.py --no-network

# 3. References: build, run and independently check the 20 queries
python ref_all.py        # writes reference-td1-complet.csv and prints SQL vs CSV for each question
python check_ref.py      # re-runs each query recorded in reference-td1.csv

# 4. API keys: set in the terminal only, never in a file (variable names: environment guide)
$env:GROQ_API_KEY = "..."
$env:OPENROUTER_API_KEY = "..."

# 5. The five batches (one operator at a time; keep the state files)
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-A.jsonl --out traces-A.csv
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-B.jsonl --out traces-B.csv
python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-C.jsonl --out traces-C.csv
python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-D.jsonl --out traces-D.csv
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-E.jsonl --out traces-E.csv
```

A new run calls the models again and consumes account allowance: it is a new experiment, so use new `--state` and `--out` names and keep the files committed here. Without network access, the committed traces are the evidence.

Step 3: `build_step3.py` merges the `traces-*.csv` files into `traces-td1.csv` and generates the comparison skeleton, with `TODO` in place of each failure cause. The committed `model-question-comparison-en.csv` contains the causes written by the sub-group from the SQL and error fields, so **do not re-run `build_step3.py` over it**.

## AI-assisted coding

An AI assistant was used to draft the reference queries, the independent check and the consolidation scripts. The sub-group ran, checked and remains responsible for every line; no model amount was ever used as a reference. Decisions and verifications are described in [`reports/td1.md`](reports/td1.md).

## Security

API keys, passwords and local environment files stay outside this repository and its history. The kit's `.gitignore` is kept at the root; files are checked before each push.
