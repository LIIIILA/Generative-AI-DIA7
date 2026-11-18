# TD 1 report - Comparing models on the same questions

**Session:** 21 October 2026 · **Class:** DIA7 · **Sub-group:** DIA7-G2 · **Course pack:** 2026-10-18-students-1

**Nature of the evidence:** all 102 trace lines are **real** calls. This report uses **no replayed or synthetic example**; the refused-access case (Qwen, C20) is a real call from our batch.

---

## 1. What we attempted and what we completed

| Step | Attempted | Completed |
|---|---|---|
| 1. Reference | 20 SQLite queries returning `revenue_cents`, each checked independently | 20/20 queries and values, independent check agreeing on 20/20 |
| 2. Model calls | 5 free models x 20 questions with the same prompt, SQL run in the read-only sandbox | 100 first attempts + 1 retry; 99 cells executed, 1 refused by the provider |
| 3. Reading the traces | One final row per model and question, with a cause for each failure | 100 rows, 21 failures each explained from the SQL or the HTTP status |
| 3. Summary | Five-model sheet: index, prices, access, results by family | 5 rows completed, undocumented values set to N/A with the reason |
| 4. Plenary | Comparison with the other sub-groups | [to complete after the plenary] |

## 2. What worked

### Reference

- File: [`reference-td1.csv`](../reference-td1.csv), 20 rows, one query and one value each.
- Conventions applied (protocol, section 1):
  - **period** closed on the left and open on the right: `date >= start AND date < end`;
  - **completed age** to the month and day, on the reference date written in the question, or on the order date for C10 and C18;
  - **amount** `SUM(quantity_product * price)`, `price` being in euro cents excluding VAT;
  - **0 instead of NULL** when nothing matches, through `COALESCE` (C06, C14).
- Independent check: [`ref_all.py`](../ref_all.py) recomputes every value in Python from the three CSV files, with real date objects and a separate age function, without SQL; 20/20 agreement. [`check_ref.py`](../check_ref.py) re-runs every query recorded in the file.
- Check by the instructor: [result to complete: all values equal to the answer key / questions corrected].

### Model calls and traces

- Merged traces: [`traces-td1.csv`](../traces-td1.csv), 102 lines (100 first attempts and 2 attempts on Qwen C20), all of nature `real`, written by the skeleton only.
- Source files kept: `traces-A.csv` … `traces-E.csv` and `state-A.jsonl` … `state-E.jsonl`.
- Each question has the same `prompt_sha256` fingerprint on all its lines: the five models received exactly the same prompt ([`prompt-td1.md`](../prompt-td1.md)).

### Results

Final results: [`model-question-comparison-en.csv`](../model-question-comparison-en.csv), pivot view [`pivot-td1.csv`](../pivot-td1.csv), summary [`five-model-summary-en.csv`](../five-model-summary-en.csv).

| Model | Access | Period (6) | Age (5) | Product (4) | Combined (5) | Total |
|---|---|---|---|---|---|---|
| openai/gpt-oss-120b | Groq Free | 6 | 5 | 4 | 5 | **20/20** |
| openai/gpt-oss-20b | Groq Free | 6 | 3 | 4 | 5 | 18/20 |
| qwen/qwen3.8-27b | Groq Free | 5 | 4 | 4 | 1 | 14/20 |
| cohere/north-mini-code:free | OpenRouter :free | 6 | 0 | 4 | 4 | 14/20 |
| dots-studio/dots-3-note-preview:free | OpenRouter :free | 6 | 1 | 4 | 2 | 13/20 |

**Period and product-list questions were answered correctly by every model that was reached.**

## 3. What failed or remains incomplete

### 3.1 Observations (evidence from the traces)

21 cells out of 100 are not correct: **19 wrong values, 1 invalid SQL, 1 refused access**. Each line below is read from the SQL returned by the model or from the HTTP status; the full explanation is in the `explanation` column of the comparison file.

| Model | Cell | Value / reference | What the trace shows |
|---|---|---|---|
| gpt-oss-20b | C02 | 0 / 590320 | Birth-date window taken from the reference year, not shifted back 25 years |
| gpt-oss-20b | C11 | 322160 / 446690 | Birth-date window five years wide, selecting customers aged 20 to 24 |
| north-mini-code | C02 | 0 / 590320 | Birth year compared directly to 25; no year difference computed |
| north-mini-code | C08 | 1188090 / 605580 | Lower bound missing: keeps everyone under 26 |
| north-mini-code | C09 | 0 / 487980 | Subtraction reversed, plus an equality forcing the birthday onto 09-26 |
| north-mini-code | C10 | 0 / 558980 | Birth year compared directly to 25 |
| north-mini-code | C11 | 0 / 446690 | Malformed `date()` modifier returns NULL and excludes every row |
| north-mini-code | C17 | 371990 / 258180 | No upper bound: keeps everyone under 26 |
| qwen3.8-27b | C09 | 0 / 487980 | Age computed on the order date instead of 2026-09-26, and contradictory month-day bounds |
| qwen3.8-27b | C15 | 0 / 168680 | Contradictory month-day bounds and no year filter |
| qwen3.8-27b | C16 | 367050 / 376740 | Strict inequality on the anniversary: excludes C001, includes C004 |
| qwen3.8-27b | C17 | 248490 / 258180 | Same anniversary fault as C16 |
| qwen3.8-27b | C19 | 83580 / 1990 | Year compared to a full date string: the age filter is always true |
| qwen3.8-27b | C20 | not executed | **HTTP 429 on both attempts**, Groq output-tokens-per-minute limit |
| dots-3-note | C02 | 0 / 590320 | Self-contradictory bounds on one date |
| dots-3-note | C08 | 0 / 605580 | Self-contradictory month-day bounds |
| dots-3-note | C09 | 369240 / 487980 | Only one branch of the completed-age rule |
| dots-3-note | C11 | 2504090 / 446690 | No upper bound: keeps everyone aged 25 or more |
| dots-3-note | C15 | 138920 / 168680 | Only one branch of the completed-age rule |
| dots-3-note | C17 | empty / 258180 | **Invalid SQL**: malformed `CAST`, sandbox `syntax_error` |
| dots-3-note | C18 | 39580 / 62480 | Only one branch of the completed-age rule |

Further observations:

- **The questions most models miss are C02, C09, C11 and C17** (3 models out of 5 each), then C08 and C15 (2 out of 5). All of them involve the completed-age convention.
- **Wrong consensus:** on C02, three models (gpt-oss-20b, north-mini-code, dots-3-note) return the **same wrong value, 0**, for three different reasons; on C09, two models also return 0.
- **Invalid SQL, not a truncated output:** dots-3-note on C17 used 297 completion tokens against a cap of 1024.
- **Refused access, not a wrong answer:** on Qwen C20 the model never received an answerable call. Value, SQL and token fields stay empty; an empty field differs from a value of 0, which is a real result on C06 and C14.

### 3.2 Explanation of the causes (hypotheses)

- **Completed age is the convention models apply least reliably.** It needs two branches (birthday already passed or not) and an inclusive bound on the anniversary day. The failed queries each break one of these elements: one branch only, a strict bound, a window not shifted by 25 years, or no year difference at all. One run per cell does not show whether these errors are stable.
- **The public index does not predict success on our questions.** Qwen 3.8 27B has the highest index of the five (33.7) but 1/5 on combined questions; gpt-oss-120b (index 11.6) answers all 20.
- **The 429 on Qwen comes from the provider's rate limit, not from the model**: the output-token budget per minute was nearly used when the call was made.

### 3.3 Remaining incomplete

- Qwen C20 has no answer: the single retry allowed by the protocol was used.
- [Plenary comparison with the other sub-groups: to complete.]

## 4. Decisions, limits and remaining uncertainty

### Decisions

- **Model C:** the template row listed `inclusionai/ling-3.0-flash-sante:free`; the sub-group ran `cohere/north-mini-code:free`, as given in the TD 1 assignment. The summary row was replaced and the change documented in its `limits` column.
- **Retry:** Qwen C20 was retried once, as allowed; after the second 429 the cell was left `not_executed` instead of being called again.
- **Final verdict:** taken from the last attempt of each cell; every attempt is kept in the raw traces.
- **Missing prices and indexes:** set to N/A with the reason when no paid route of the exact same model, or no index, is documented. A model of the same family (for example qwen3.8-max for qwen3.8-27b) was not counted as the same model.

### Limits

- One run per cell at temperature 0: the variability of each model is not measured.
- Results hold for this base (59 customers, 221 orders) and these 20 questions only; they support a routing hypothesis, not a general ranking.
- Only gpt-oss-120b has a documented paid route of the exact same model in the 28 September portfolio. North-mini-code and dots-3-note are absent from the portfolio; their pages were checked on OpenRouter on 21 October 2026 and only free routes are listed.
- Free routes and rate limits can change: the same calls on another day may give other accesses.

### Remaining uncertainty

- Equality of the 20 references with the answer key: [confirmed by the instructor / to complete].
- Whether the age errors would repeat on a second run is unknown.

### Replayed or synthetic examples

None. Every trace line and every example in this report comes from a real call of this session.

### AI-assisted coding

An AI assistant helped draft the reference queries, the independent check and the consolidation scripts. Every query was run and checked by the sub-group; no model amount was used as a reference.

## 5. Division of work

| Member | Role | Contribution |
|---|---|---|
| Alice Quentrec | A | References C04, C05, C06 and their independent check; gpt-oss-120b batch (20 cells, 20 correct); consolidation scripts; five-model summary |
| [name] | B | References [...]; gpt-oss-20b batch |
| [name] | C | References [...]; north-mini-code batch |
| [name] | D | References [...]; qwen3.8-27b batch |
| [name] | E | References [...]; dots-3-note batch |
| [name] | F / G / H | Cross-check of the references; causes in the comparison file |

## 6. Next steps and help needed

### Next steps (TD 2, 18 November 2026)

- Write the k-of-n vote in `atelier-vote.py`, with abstention when no value reaches a strict majority.
- Use C02 as the wrong-consensus case: three models agree on 0 against a reference of 590320.
- Write the routing rule by question family, each line justified by a cell of the TD 1 table:
  - period and product questions: any model, the cheapest first;
  - age and combined questions: gpt-oss-120b first;
  - first model unavailable (as with the 429 on C20): next model, deferral or abstention.
- TD 2 preparation: [name].

### Help needed

[None / question for the teaching team]
