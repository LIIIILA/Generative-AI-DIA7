# Routing rule worksheet - DIA7-G2, pair C

Course template: `templates/routing-rule-en.md`. Evidence: `traces-td1.csv` (TD 1, 102 rows, nature = real,
latest attempt per cell). Full rule, rates and analysis: [`regle-routage-td2.md`](regle-routage-td2.md).

## Rule

- **Use case and consequence of an error:** revenue questions on the shop database. Three levels:
  internal dashboard (manual correction), figure shown to a customer (complaint, loss of trust),
  amount paid out (financial loss).
- **Question family and supporting observations:**
  - F1 period (C01 C04 C05 C06 C07 C20) and F3 product list (C03 C12 C13 C14): every executed cell
    correct for all five models (Qwen C20 not_executed, HTTP 429).
  - F2 age on a date (C02 C08 C09 C11) and its combinations (C15 C16 C17 C19): only gpt-oss-120b is
    8/8; 20B 6/8, Qwen 3/8, North 3/8, Dots 2/8. Wrong consensus on C02 (20B, North, Dots → 0,
    reference 590320) and C09 (North, Qwen → 0, reference 487980).
  - F2b age at order (C10, C18): 120B, 20B, Qwen 2/2; only two cells.
- **Eligible models and access routes:** F1/F3: gpt-oss-20b, qwen3.8-27b, gpt-oss-120b (Groq Free),
  north-mini-code, dots-3-note (OpenRouter `:free`). F2/F2+: gpt-oss-120b only (Groq Free, or paid
  OpenRouter route at 0.15 / 0.60 USD per M). F2b: 20B, Qwen, 120B.
- **First route and reason:** F1/F3/F2b: gpt-oss-20b on Groq, the cheapest model with 100 % in TD 1
  (0 USD, portfolio G5). F2/F2+: gpt-oss-120b on Groq, the only model at 100 %.
- **Additional check or escalation:**
  - dashboard: none for F1/F3 (100 % in TD 1); 2-of-3 {120B, 20B, Qwen} for F2, F2+, F2b;
  - customer figure: 2-of-3 for every family, plus deterministic age recomputation for age families;
  - payout: deterministic SQL reference recomputed + human review, whatever the family;
  - never 3-of-5 on age: it accepts the wrong 0 on C02 and abstains on C09, C11, C17.
- **Maximum acceptable delay and cost basis:** deferrable requests may wait for the Groq refill if it
  arrives before the deadline (scenario: 60 min within 120 min). Paid fallback: gpt-oss-120b at
  ≈ 0.0002 USD per request (≈ 640 input + 150 output tokens, TD 1 counts), within the request budget.
- **Stop, defer or human-review condition:** defer when no free eligible route is available and the
  refill comes before the deadline; abstain when no eligible route fits the deadline and budget (never
  fall back to North or Dots on age: 0/4); human review for payouts and unknown families.

## Scenario outcomes

Decisions from the adapted `atelier-routage.py` ([`simulateur-apres.txt`](simulateur-apres.txt), nature = simulation).

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary question, preferred route available | Scenario "simple": F1 dashboard → run gpt-oss-20b@groq, no check | Cheapest model at 100 % on F1, low-stakes dashboard | TD 1 cells C01 C04 C05 C06 C07 C20, 20B 6/6 |
| R2 | Preferred provider unavailable | Scenario "preferred provider unavailable": Groq exhausted → run north-mini-code@openrouter, free | Next free eligible model on F1 | North F1 6/6 in TD 1; availability is a scenario assumption |
| R3 | Deferrable request, free quota exhausted | Scenario "deferrable": F2, Groq and subscription exhausted → defer on gpt-oss-120b@groq, wake in 60 min | Only 100 % model on age; refill before the 120-min deadline; availability rechecked at wake-up | 120B F2 4/4 (C02 C08 C09 C11); reset time assumed |
| R4 | Urgent request; no adequate route within the allowed budget | Scenario "budget exhausted": F2, budget 0 → abstain. With budget 0.30 ("urgent") → paid 120B, 0.0002 USD | No eligible route within deadline and budget; North and Dots available but excluded (F2 0/4) | North C02 C08 C09 C11 incorrect; Dots same; cost estimated from TD 1 tokens |
| R5 | High consequence of error; model answers agree | Scenarios "customer figure" (F2+) and "payout" (F3): run first model + 2-of-3, deterministic recomputation; payout adds reference + human review | Agreement is not proof: C02 shows three models agreeing on a wrong value | C02 wrong consensus (0 vs 590320) |

Kit rule outputs before adaptation: [`simulateur-avant.txt`](simulateur-avant.txt).
