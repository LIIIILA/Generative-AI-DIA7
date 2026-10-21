# DIA7 - DIA7-G2

Shared repository of sub-group **DIA7-G2** (class **DIA7**, sub-group 2) for the module *Trustworthy Generative AI* (Next-Generation AI), ESILV, Data & AI major, year 4. It is kept from TD 1 to TD 3.

## Sub-group

- **Class:** DIA7
- **Sub-group:** DIA7-G2

## Course pack and environment

| Item | Value |
|---|---|
| Course pack | `2026-10-18-students-1` (18 October 2026), kit `kit-td1` |
| Database | `data/boutique.sqlite` (seed 20260925): 5 products, 59 customers, 221 orders over 397 lines; hashes in `data/manifest.json` |
| Operating system | Windows, PowerShell |
| Language | Python 3 in a virtual environment (`.venv`); SQLite through Python's `sqlite3` module |
| Model access | Personal free accounts only: Groq Free plan and OpenRouter `:free` routes (`provider.max_price` at zero) |
| Models | Identifiers and parameters in [`modeles-autorises.json`](modeles-autorises.json) |

## Repository contents (TD 1)

| File | Content |
|---|---|
| [`reports/td1.md`](reports/td1.md) | TD 1 session report |
| [`reference-td1.csv`](reference-td1.csv) | 20 reference queries and their values (`revenue_cents`) |
| [`ref_all.py`](ref_all.py) | Builds and runs the 20 queries, then recomputes each value from the CSV files without SQL |
| [`check_ref.py`](check_ref.py) | Re-runs each query recorded in `reference-td1.csv` and compares it with the recorded value |
| [`prompt-td1.md`](prompt-td1.md) | Prompt as used: system message and user template, identical for all models |
| `traces-A.csv` … `traces-E.csv` | Raw traces of each operator, all attempts |
| `state-A.jsonl` … `state-E.jsonl` | State files of each operator (limit of one retry per cell) |
| [`traces-td1.csv`](traces-td1.csv) | All raw traces merged under one header (102 lines) |
| [`model-question-comparison-en.csv`](model-question-comparison-en.csv) | One final row per model and question (100 rows) with the cause of each failure |
| [`pivot-td1.csv`](pivot-td1.csv) | Models x questions view of the comparison file |
| [`five-model-summary-en.csv`](five-model-summary-en.csv) | Public index, prices, access used and results by question family for the five models |
| [`build_step3.py`](build_step3.py), [`fill_summary.py`](fill_summary.py) | Consolidation scripts |

## Reproducing TD 1

Run every command from the repository root, in PowerShell.

### 1. Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python check_access.py --no-network   # local integrity check, no model call
```

### 2. References

```powershell
python ref_all.py     # runs the 20 queries and prints SQL value vs independent CSV value
python check_ref.py   # re-runs every query stored in reference-td1.csv
```

### 3. Model calls

API keys are set in the terminal only, never written to a file (variable names: environment guide of the kit).

```powershell
$env:GROQ_API_KEY = "..."
$env:OPENROUTER_API_KEY = "..."
```

One batch of 20 questions per model, one operator at a time:

```powershell
$cases = "C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20"
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases $cases --state state-A.jsonl --out traces-A.csv
python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases $cases --state state-B.jsonl --out traces-B.csv
python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases $cases --state state-C.jsonl --out traces-C.csv
python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --cases $cases --state state-D.jsonl --out traces-D.csv
python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --cases $cases --state state-E.jsonl --out traces-E.csv
```

A new run calls the models again and consumes account allowance: it is a separate experiment and must use new `--state` and `--out` names. The committed traces are the evidence of this session.

### 4. Consolidation

```powershell
python build_step3.py    # merges traces-*.csv into traces-td1.csv and builds the comparison skeleton
python fill_summary.py   # fills index, price and limit columns of the five-model summary
```

`build_step3.py` writes `TODO` in place of each failure cause. The committed `model-question-comparison-en.csv` holds the causes written by the sub-group from the SQL and error fields: do not re-run `build_step3.py` over it.

## AI-assisted coding

An AI assistant helped draft the reference queries, the independent check and the consolidation scripts. The sub-group ran and checked every line and remains responsible for it; no model amount was ever used as a reference. See [`reports/td1.md`](reports/td1.md).

## Security

API keys, passwords and local environment files stay outside this repository and its history. The kit's `.gitignore` is kept at the root, and files are checked before each push.
