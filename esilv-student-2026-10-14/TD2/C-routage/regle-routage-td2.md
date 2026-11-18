## Step 3 - Routing rule (pair C)

Source: `traces-td1.csv` (102 rows, 100 cells, nature = real, latest attempt per cell).
Rates are `correct / cases`; a `not_executed` cell counts in cases but not in correct.

Worksheet in the course template format: [`routing-rule-en.md`](routing-rule-en.md).

### 1. TD 1 accuracy per question family

| Family | Questions | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code | dots-3-note |
|---|---|---|---|---|---|---|
| F1 period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 5/6 (C20 not_executed, HTTP 429 OTPM) | 6/6 | 6/6 |
| F2 age on a date | C02 C08 C09 C11 | **4/4** | 2/4 (C02 = 0, C11 = 322160) | 3/4 (C09 = 0) | 0/4 | 0/4 |
| F2b age at order | C10 | 1/1 | 1/1 | 1/1 | 0/1 (C10 = 0) | 1/1 |
| F3 product list | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F2+ age on a date + period/product | C15 C16 C17 C19 | **4/4** | 4/4 | 0/4 (C15 = 0, C16 = 367050, C17 = 248490, C19 = 83580) | 3/4 (C17 = 371990) | 2/4 (C15 = 138920, C17 sql_invalid) |
| F2b+ age at order + period | C18 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 (C18 = 39580) |

Age on a date (F2 + F2+, 8 cells): 120B 8/8, 20B 6/8, Qwen 3/8, North 3/8, Dots 2/8.
Every model is correct on F1 and F3 whenever the call was executed.

Wrong consensus observed: **C02**, three models (20B, North, Dots) return `0` (reference 590320);
**C09**, two models (North, Qwen) return `0` (reference 487980).

### 2. Votes on the same traces

| Check | Correct | Wrong | Abstain |
|---|---|---|---|
| 2-of-3 {120B, 20B, Qwen} | 20/20 | 0 | 0 |
| 3-of-5 (all five models) | 16/20 | 1 (C02 → 0, wrong consensus) | 3 (C09, C11, C17) |

Caution: the 2-of-3 panel is chosen on the same 20 questions it is scored on (no held-out set),
so 20/20 is an optimistic estimate, not a guarantee.

### 3. The rule

Cost of an error: **dashboard** = internal figure read once, a manual correction;
**customer** = figure shown to a customer, a complaint; **payout** = amount paid out, a financial loss.

| Family | First model (cheapest correct in TD 1) | Dashboard | Customer figure | Payout | Fallback if first model unavailable |
|---|---|---|---|---|---|
| F1 period | gpt-oss-20b, Groq Free, G5, 0 USD (6/6) | none (100 % in TD 1) | 2-of-3 {120B, 20B, Qwen} | deterministic SQL reference + human review | next free model: Qwen → 120B@Groq → North → Dots (all 100 % executed); if all exhausted, wait for refill, else paid 120B |
| F3 product list | gpt-oss-20b, Groq Free, 0 USD (4/4) | none (100 % in TD 1) | 2-of-3 | reference + review | same as F1 |
| F2b age at order (+ period) | gpt-oss-20b, 0 USD (C10, C18) | 2-of-3: only 2 cells, too few to skip checking | 2-of-3 + deterministic age recomputation | reference + review | Qwen → 120B@Groq; never North (C10 = 0) |
| F2 age on a date | gpt-oss-120b, Groq Free, 0 USD (4/4); paid route 0.15 / 0.60 USD per M (≈ 0.0002 USD per request) | 2-of-3 {120B, 20B, Qwen}; **never 3-of-5** (C02 wrong consensus) | 2-of-3 + deterministic age recomputation | reference + review | wait for Groq refill if the deadline allows, else paid 120B within budget, else **abstain**; never North or Dots (0/4) |
| F2+ combinations with age on a date | gpt-oss-120b (4/4) | 2-of-3 | 2-of-3 + deterministic age recomputation | reference + review | same as F2 |
| Unknown family | none | review | review | review | abstain |

"None" is used only for an internal dashboard on a family at 100 % in TD 1 (F1, F3), as required.
Questions no free model handles alone with confidence: the age families (F2, F2+). Only 120B was
100 % there, and three models agree on a wrong `0` on C02, so their checking cost (three calls or a
deterministic recomputation) carries into TD 3.

### 4. Simulator

Outputs: [`simulateur-avant.txt`](simulateur-avant.txt) (kit version, its seven scenarios) and [`simulateur-apres.txt`](simulateur-apres.txt) (adapted, ten scenarios, `nature = simulation`). The seven kit scenarios are kept (simple, complex, deferrable, urgent, budget exhausted; high impact → customer figure; unknown capability → unknown family) and three are added (preferred provider unavailable, subscription priority, payout).
The adapted `atelier-routage.py` replaces capability levels with the families each resource was 100 %
correct on in TD 1, and cites the cells in every `reason`. The branch order of `choose` is unchanged.

| Scenario | Request | Decision |
|---|---|---|
| simple | F1, dashboard | run gpt-oss-20b@groq, check none |
| complex | F2, dashboard | run gpt-oss-120b@groq, 2-of-3 |
| preferred provider unavailable | F1, Groq exhausted | run north-mini-code@openrouter (free, F1 6/6) |
| subscription priority | F2, Groq exhausted (refill in 60 min) | run subscription-G2 (cash 0) |
| deferrable | F2, Groq + subscription exhausted, can wait 120 min | defer on gpt-oss-120b@groq, wake in 60 min |
| urgent | same, deadline 5 min | run gpt-oss-120b paid route, 0.0002 USD |
| budget exhausted | same, budget 0 | abstain (North and Dots are available but not eligible on F2) |
| customer figure | F2+, customer | run 120B@groq, 2-of-3 + deterministic age recomputation |
| payout | F3, payout | run 20B@groq, deterministic reference + human review |
| unknown family | F4 | abstain |

### 5. Why `choose` prefers an available subscription to deferring

`choose` tests the `included` branch (`available` and `cash == 0`) **before** the `waiting` branch. A
subscription with remaining allocation has no marginal cash cost, because it is already paid, and it
answers now. So in the scenario "subscription priority" it runs on the subscription instead of waiting
60 minutes for the free Groq refill, even though the refill arrives before the deadline. Among included
resources, the key `(allocation, rank)` still prefers a free route (allocation 0) to the subscription.

This priority should reverse when consuming the subscription has an opportunity cost:
- its allocation is scarce and better kept for requests only it can serve (high difficulty, urgent, G1 work);
- the request is deferrable, low value, and the free refill comes well before the deadline;
- the subscription is not measured on the family: in our rule it is "not measured in TD 1", so using it
  on an age question trades a known 4/4 model (after a 60-minute wait) for an unmeasured one;
- the subscription's terms, data or privacy conditions do not fit the request.

A possible change: test `waiting` before a subscription when `can_wait` is true and the request is a
dashboard, keeping the subscription for urgent or customer-facing requests.

### 6. Limits

- Small samples: F2b has 2 cells and some families 1 to 4 cells; one run per cell at temperature 0.
- Rates come from one batch on 21 October 2026; models served under the same name may change.
- North and Dots have no paid route in the portfolio snapshot (N/A); the subscription was not measured.
- Costs per request are estimates from TD 1 token counts (≈ 640 input + 150 output tokens).

AI assistance (declared): rates, vote checks and the simulator adaptation were prepared with an AI
assistant from our `traces-td1.csv`, then checked and explained by pair C.
