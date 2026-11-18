# TD 2 – Session report

## 0. Summary

| Pair | Step | Deliverable | Status |
|---|---|---|---|
| A | 1 – Vote | `vote_k_sur_n` completed in `skeleton-multi-llm-en.py`; 20-question comparison of the 2-of-3 panel and the 3-of-5 quorum | Done |
| B | 2 – Wrong consensus | Case **C09**, proven in SQL on `data/boutique.sqlite` with an executed delta query | Done |
| C | 3 – Routing rule | One-page rule, simulator outputs before and after adaptation, analysis of included capacity versus deferral | Done |

Data: all results come from the 100 TD 1 cells in `TD1_traces/traces-td1.csv` (102 rows, `nature = real`, latest attempt per cell) and from `data/boutique.sqlite`.
**Synthetic or replayed material, identified explicitly:** the DEMO-VOTE toy table (section 2.5) and the simulator scenarios of section 3.4 (`nature = simulation`). Everything else is real.

---

## 1. Pair A – Vote: 2-of-3 panel against 3-of-5 quorum

`vote_k_sur_n` abstains when no value reaches `k`, and keeps an unavailable member (HTTP 429, `sql_invalid`) in `n` without letting it vote. The vote uses the last attempt of each cell.
Fixed panel of `atelier-vote.py`: {gpt-oss-120b, cohere/north-mini-code, qwen3.8-27b}. The 3-of-5 quorum adds gpt-oss-20b and dots-3-note-preview, which belong to the five TD 1 models but are not in the fixed panel.

### 1.1 Comparison on the twenty questions

| Question | Reference | 2-of-3 (fixed panel) | Agrees | 3-of-5 | Agrees | Changes? |
|---|---|---|---|---|---|---|
| C01 | 792800 | consensus 792800 (3 votes) | yes | consensus 792800 (5 votes) | yes | no |
| C02 | 590320 | consensus 590320 (2 votes) | yes | consensus 0 (3 votes) | **NO** | **yes** |
| C03 | 936350 | consensus 936350 (3 votes) | yes | consensus 936350 (5 votes) | yes | no |
| C04 | 2826250 | consensus 2826250 (3 votes) | yes | consensus 2826250 (5 votes) | yes | no |
| C05 | 38480 | consensus 38480 (3 votes) | yes | consensus 38480 (5 votes) | yes | no |
| C06 | 0 | consensus 0 (3 votes) | yes | consensus 0 (5 votes) | yes | no |
| C07 | 13970 | consensus 13970 (3 votes) | yes | consensus 13970 (5 votes) | yes | no |
| C08 | 605580 | consensus 605580 (2 votes) | yes | consensus 605580 (3 votes) | yes | no |
| C09 | 487980 | consensus 0 (2 votes) | **NO** | abstention (max 2 votes) | abstention | **yes** |
| C10 | 558980 | consensus 558980 (2 votes) | yes | consensus 558980 (4 votes) | yes | no |
| C11 | 446690 | consensus 446690 (2 votes) | yes | abstention (max 2 votes) | abstention | **yes** |
| C12 | 1666490 | consensus 1666490 (3 votes) | yes | consensus 1666490 (5 votes) | yes | no |
| C13 | 107740 | consensus 107740 (3 votes) | yes | consensus 107740 (5 votes) | yes | no |
| C14 | 0 | consensus 0 (3 votes) | yes | consensus 0 (5 votes) | yes | no |
| C15 | 168680 | consensus 168680 (2 votes) | yes | consensus 168680 (3 votes) | yes | no |
| C16 | 376740 | consensus 376740 (2 votes) | yes | consensus 376740 (4 votes) | yes | no |
| C17 | 258180 | abstention (max 1 vote) | abstention | abstention (max 2 votes) | abstention | no |
| C18 | 62480 | consensus 62480 (3 votes) | yes | consensus 62480 (4 votes) | yes | no |
| C19 | 1990 | consensus 1990 (2 votes) | yes | consensus 1990 (4 votes) | yes | no |
| C20 | 1106090 | consensus 1106090 (2 votes) | yes | consensus 1106090 (4 votes) | yes | no |

| Quorum | Correct consensus | Wrong consensus | Abstentions |
|---|---|---|---|
| 2-of-3 fixed panel | 18 | 1 (C09) | 1 (C17) |
| 3-of-5 | 16 | 1 (C02) | 3 (C09, C11, C17) |

### 1.2 Commentary on every difference between 2-of-3 and 3-of-5

**C02 (reference 590320): a correct consensus becomes a wrong consensus.**
- 2-of-3: gpt-oss-120b and qwen3.8-27b return 590320 (both `correct`) and outvote north-mini-code = 0.
- 3-of-5: gpt-oss-20b = 0 and dots-3-note = 0 (both `incorrect`) join north-mini-code = 0. The value 0 gets 3 votes, reaches `k = 3` and beats the correct value (2 votes).
- The three zeros come from three different faulty SQL filters, each matching no customer. They share the value 0, not the cause: `COALESCE(SUM(...), 0)` turns any empty filter into 0.
- The two added voters are weak on age questions (gpt-oss-20b 3/5 and dots-3-note 1/5 on the age family in TD 1), which let a correlated error win.

**C09 (reference 487980): a wrong consensus becomes an abstention.**
- 2-of-3: north-mini-code = 0 and qwen3.8-27b = 0 outvote gpt-oss-120b = 487980.
- 3-of-5: 487980 gets 2 votes (gpt-oss-120b, gpt-oss-20b), 0 gets 2 votes, and dots-3-note proposes 369240. No value reaches 3, so the quorum abstains.
- The higher threshold blocks the wrong answer but does not recover the right one. This case is analysed in SQL in section 2.

**C11 (reference 446690): a correct consensus becomes an abstention.**
- 2-of-3: gpt-oss-120b and qwen3.8-27b agree on 446690.
- 3-of-5: the correct value still has 2 votes; the other three models propose three different wrong values (gpt-oss-20b = 322160, north-mini-code = 0, dots-3-note = 2504090). Nothing reaches 3.
- This is the cost of a stricter quorum: a correct answer is lost because too few voters are reliable on this family.

### 1.3 Cases without a change that are worth reading
- **C17:** abstention in both quorums. dots-3-note returned invalid SQL (`sql_invalid`, empty value) and stays in `n = 5` without voting. 258180 gets 2 votes (gpt-oss-120b, gpt-oss-20b); qwen = 248490 and north-mini-code = 371990 get 1 each.
- **C20:** qwen3.8-27b is `not_executed` after two HTTP 429 responses and stays in `n = 3`. 1106090 still reaches `k = 2` with gpt-oss-120b and north-mini-code, but with no margin: one more failure and the panel abstains.
- **C14:** qwen3.8-27b got a 429 on its first attempt; its second attempt is `correct`. The vote uses the last attempt, so qwen votes 0, which is the correct value.
- **C08 and C15 (3-of-5):** the correct value reaches exactly 3 votes, so two wrong voters leave no margin.

### 1.4 Conclusions (twenty questions only)
- **Neither quorum dominates.** 3-of-5 removes the C09 error, introduces the C02 error and loses C11. It answers fewer questions (17 against 19) with the same number of wrong decisions (1).
- **Both wrong consensuses share the value 0 on age questions.** A larger panel does not protect against correlated errors such as faulty filters that select nobody. A deterministic check (for example, verifying that the selected population is not empty, or comparing with the reference query) would catch that case.
- **gpt-oss-120b alone answered 20/20 in TD 1**, so on this batch the vote does not beat the best single model. One run per cell at temperature 0 and twenty questions support a hypothesis for this batch, not a general error rate or a quorum guarantee.

---

## 2. Pair B – Wrong consensus verified on `data/boutique.sqlite`: case C09

### 2.1 Identification and quorum verdict

| Item | Value |
|---|---|
| Case identifier | **C09** |
| Source / nature | Real TD 1 traces (`TD1_traces/traces-td1.csv`, `nature = real`) |
| Question | Total revenue excluding VAT, in euro cents, of customers who are exactly 25 years old on the reference date **2026-09-26**, over all their orders |
| Models agreeing on the wrong value | `cohere/north-mini-code:free` and `qwen/qwen3.8-27b` |
| Shared wrong value | **0** |
| Independent reference (`reference-td1.csv`) | **487 980** cents |

| Model | Value | Verdict | In the fixed panel? |
|---|---|---|---|
| `openai/gpt-oss-120b` | 487 980 | correct | yes |
| `cohere/north-mini-code:free` | 0 | incorrect | yes |
| `qwen/qwen3.8-27b` | 0 | incorrect | yes |
| `openai/gpt-oss-20b` | 487 980 | correct | no |
| `dots-studio/dots-3-note-preview:free` | 369 240 | incorrect | no |

| Quorum | Declaration | Result |
|---|---|---|
| Fixed panel, 2 out of 3 | k = 2, n = 3 | **Consensus on 0, which is wrong** (`atelier-vote.py --case C09` returns `consensus: true, value: 0, votes: 2, matches_reference: false`). The shared wrong value wins. |
| 3 out of 5 | k = 3, n = 5 | **Abstention.** Counts: 487 980 ×2, 0 ×2, 369 240 ×1. No value reaches 3 votes. |

### 2.2 Faulty SQL clause diagnosis

Both queries run without error on `data/boutique.sqlite` and return **0** (executed with `td2_C09.py`).

**Cohere (`cohere/north-mini-code:free`)**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-09-26
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    CAST(SUBSTR('2026-09-26', 1, 4) AS INTEGER)
  ) =
  CASE
    -- If birthday hasn't occurred yet this year, subtract 1
    WHEN SUBSTR(c.birth_date, 6, 2) || '-' || SUBSTR(c.birth_date, 9, 2) >
         SUBSTR('2026-09-26', 6, 2) || '-' || SUBSTR('2026-09-26', 9, 2)
    THEN -1 ELSE 0 END
  AND
  SUBSTR(c.birth_date, 6, 2) || '-' || SUBSTR(c.birth_date, 9, 2) =
  SUBSTR('2026-09-26', 6, 2) || '-' || SUBSTR('2026-09-26', 9, 2);
```

Root cause: the first condition compares `birth_year - 2026` (about −25 for customers born around 2000–2001) with a `CASE` that returns only −1 or 0. These values are never equal, so no row passes. The year subtraction is reversed. The last condition also keeps only customers whose birthday is exactly `09-26`, which is not "25 years old on that date" either.

**Qwen (`qwen/qwen3.8-27b`)**

```sql
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
  AND (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date))
  AND (strftime('%m-%d', o.date) < strftime('%m-%d', date(c.birth_date, '+26 years')));
```

Root cause: the query uses the order date `o.date` instead of the reference date 2026-09-26. Its second and third conditions require the month-day of the order to be `>=` the month-day of the birth date and `<` the month-day of the birth date plus 26 years. Adding 26 years does not change the month-day, so the conditions reduce to `x >= m` and `x < m`: a contradiction, and no row passes.

Both queries select an empty set of customers and `COALESCE(SUM(...), 0)` turns the empty sum into 0. The shared value comes from two different SQL mistakes ending in the same failure value, not from one shared reasoning error.

### 2.3 Delta diagnostic query (executed on `data/boutique.sqlite`)

The reference counts customers born in the window `2000-09-26 < birth_date <= 2001-09-26`, which is what "exactly 25 years old on 2026-09-26" means. The faulty queries count none of them.

```sql
SELECT c.customer_id,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o  ON o.customer_id = c.customer_id
JOIN product p ON p.product_id  = o.product_id
WHERE c.birth_date >  '2000-09-26'
  AND c.birth_date <= '2001-09-26'
GROUP BY c.customer_id
ORDER BY c.customer_id;
```

| customer_id | revenue_cents |
|---|---|
| C001 | 135 000 |
| C002 | 25 920 |
| C003 | 47 900 |
| C007 | 118 740 |
| C008 | 99 090 |
| C009 | 61 330 |
| **Total** | **487 980** |

The six customers are counted by the reference and missed by both faulty queries. The gap is `487 980 − 0 = 487 980` cents (4 879.80 €), which accounts for the whole difference.

### 2.4 Independent checking method

The total was recomputed outside SQL with pandas on the same database: read `customers`, `orders` and `product`, join on `customer_id` and `product_id`, keep `birth_date > '2000-09-26'` and `birth_date <= '2001-09-26'`, then sum `quantity_product * price`. Result: **487 980**, identical to the SQL total and to `reference-td1.csv`.
The correct queries of gpt-oss-120b and gpt-oss-20b (`BETWEEN '2000-09-27' AND '2001-09-26'`) define the same window, provided `birth_date` is stored as text `YYYY-MM-DD` without a time part.

### 2.5 Mechanism illustrated: DEMO-VOTE (synthetic)

These values are **constructed teaching material**, not model outputs and not answers on the shop database.
Toy table with one sale: date `2026-01-01`, amount 100 cents. Requested period: 1 January inclusive to 2 January exclusive. All variants use `sale_date < '2026-01-02'` and `COALESCE(SUM(amount_cents), 0)`.

| Variant | Lower bound | Result |
|---|---|---|
| Proposals 1 and 2 | `sale_date > '2026-01-01'` | **0** (the sale of 1 January is excluded by the strict bound) |
| Proposal 3 | `sale_date >= '2026-01-01'` | **100** |

With the proposals `[0, 0, 100]`, a 2-of-3 threshold validates 0 while the independent reference is 100 cents. Two proposals sharing the same boundary error are enough for the vote to confirm a wrong value, which is the mechanism seen in C09.

### 2.6 Consequence for checking
A majority vote cannot detect an error shared by the majority. On C09 the fixed panel returns a confident but wrong 0. An independent check is needed: a reference query, a recomputation outside SQL, or a deterministic guard that flags an empty selection when the question expects customers.

---

## 3. Pair C – Routing rule and simulator

Source: `traces-td1.csv`. Rates are `correct / cases`; a `not_executed` cell counts in cases but not in correct. The worksheet in the course template format is in `routing-rule-en.md`.

### 3.1 TD 1 accuracy per question family

| Family | Questions | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code | dots-3-note |
|---|---|---|---|---|---|---|
| F1 period | C01 C04 C05 C06 C07 C20 | 6/6 | 6/6 | 5/6 (C20 not_executed, HTTP 429) | 6/6 | 6/6 |
| F2 age on a date | C02 C08 C09 C11 | **4/4** | 2/4 (C02 = 0, C11 = 322160) | 3/4 (C09 = 0) | 0/4 | 0/4 |
| F2b age at order | C10 | 1/1 | 1/1 | 1/1 | 0/1 (C10 = 0) | 1/1 |
| F3 product list | C03 C12 C13 C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F2+ age on a date + period/product | C15 C16 C17 C19 | **4/4** | 4/4 | 0/4 | 3/4 (C17 = 371990) | 2/4 (C15 = 138920, C17 sql_invalid) |
| F2b+ age at order + period | C18 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 (C18 = 39580) |

Age on a date (F2 + F2+, 8 cells): 120B 8/8, 20B 6/8, Qwen 3/8, North 3/8, Dots 2/8. Every model is correct on F1 and F3 whenever the call was executed.
Wrong consensus observed: C02 (three models return 0) and C09 (two models return 0).

### 3.2 Votes on the same traces

| Check | Correct | Wrong | Abstain |
|---|---|---|---|
| 2-of-3 {120B, 20B, Qwen} | 20/20 | 0 | 0 |
| 3-of-5 (all five models) | 16/20 | 1 (C02) | 3 (C09, C11, C17) |

Note: this panel {120B, 20B, Qwen} is the one **selected by Pair C for the rule**. It is not the fixed panel of `atelier-vote.py` evaluated in section 1 ({120B, north-mini-code, Qwen}), which scores 18 correct, 1 wrong and 1 abstention. The selected panel is chosen on the same 20 questions it is scored on (no held-out set), so 20/20 is an optimistic estimate, not a guarantee.

### 3.3 The rule

Cost of an error: **dashboard** = internal figure read once, manual correction; **customer** = figure shown to a customer, a complaint; **payout** = amount paid out, a financial loss.

| Family | First model (cheapest correct in TD 1) | Dashboard | Customer figure | Payout | Fallback if first model unavailable |
|---|---|---|---|---|---|
| F1 period | gpt-oss-20b, Groq Free, 0 USD (6/6) | none (100 % in TD 1) | 2-of-3 {120B, 20B, Qwen} | deterministic SQL reference + human review | next free model: Qwen → 120B@Groq → North → Dots; if all exhausted, wait for refill, else paid 120B |
| F3 product list | gpt-oss-20b, Groq Free, 0 USD (4/4) | none (100 % in TD 1) | 2-of-3 | reference + review | same as F1 |
| F2b age at order (+ period) | gpt-oss-20b, 0 USD (C10, C18) | 2-of-3 (only 2 cells, too few to skip checking) | 2-of-3 + deterministic age recomputation | reference + review | Qwen → 120B@Groq; never North (C10 = 0) |
| F2 age on a date | gpt-oss-120b, Groq Free, 0 USD (4/4); paid route 0.15 / 0.60 USD per M tokens (≈ 0.0002 USD per request) | 2-of-3 {120B, 20B, Qwen}; **never 3-of-5** (C02 wrong consensus) | 2-of-3 + deterministic age recomputation | reference + review | wait for Groq refill if the deadline allows, else paid 120B within budget, else **abstain**; never North or Dots (0/4) |
| F2+ age on a date + period/product | gpt-oss-120b (4/4) | 2-of-3 | 2-of-3 + deterministic age recomputation | reference + review | same as F2 |
| Unknown family | none | review | review | review | abstain |

"None" is used only for an internal dashboard on a family at 100 % in TD 1 (F1, F3). **No free model is enough on its own for the age families (F2, F2+)**: only gpt-oss-120b was 100 % there, and three models agree on a wrong 0 on C02. Their checking cost (three calls or a deterministic recomputation) carries into TD 3.

### 3.4 Simulator (synthetic scenarios, `nature = simulation`)

Outputs: `simulateur-avant.txt` (kit version, seven scenarios) and `simulateur-apres.txt` (adapted, ten scenarios). The adapted `atelier-routage.py` replaces capability levels with the families each resource was 100 % correct on in TD 1, and cites the cells in every `reason`. The branch order of `choose` is unchanged.

| Scenario | Request | Decision |
|---|---|---|
| simple | F1, dashboard | run gpt-oss-20b@groq, check none |
| complex | F2, dashboard | run gpt-oss-120b@groq, 2-of-3 |
| preferred provider unavailable | F1, Groq exhausted | run north-mini-code@openrouter (free, F1 6/6) |
| subscription priority | F2, Groq exhausted (refill in 60 min) | run subscription-G2 (cash 0) |
| deferrable | F2, Groq and subscription exhausted, can wait 120 min | defer on gpt-oss-120b@groq, wake in 60 min |
| urgent | same, deadline 5 min | run gpt-oss-120b paid route, 0.0002 USD |
| budget exhausted | same, budget 0 | abstain (North and Dots are available but not eligible on F2) |
| customer figure | F2+, customer | run 120B@groq, 2-of-3 + deterministic age recomputation |
| payout | F3, payout | run 20B@groq, deterministic reference + human review |
| unknown family | F4 | abstain |

### 3.5 Included capacity against deferral

`choose` tests the `included` branch (`available` and `cash == 0`) **before** the `waiting` branch. A subscription with remaining allocation has no marginal cash cost and answers now, so in the "subscription priority" scenario it runs on the subscription instead of waiting 60 minutes for the free Groq refill, even though the refill arrives before the deadline. Among included resources, the key `(allocation, rank)` still prefers a free route (allocation 0) to the subscription.

This priority should reverse when consuming the subscription has an opportunity cost:
- its allocation is scarce and better kept for requests only it can serve (high difficulty, urgent work);
- the request is deferrable, low value, and the free refill comes well before the deadline;
- the subscription is not measured on the family (here "not measured in TD 1"), so using it on an age question trades a known 4/4 model after a wait for an unmeasured one;
- the subscription's terms, data or privacy conditions do not fit the request.

A possible change: test `waiting` before a subscription when `can_wait` is true and the request is a dashboard, keeping the subscription for urgent or customer-facing requests.

---

## 4. Cross-pair reading: what the three parts show together

- The vote (A) and the wrong consensus (B) show the same limit: a quorum cannot detect an error shared by its voters. The two wrong consensuses (C02, C09) both return 0 on age questions.
- The routing rule (C) draws the consequence: age-on-a-date questions get an independent check (2-of-3 with a deterministic age recomputation) and never rely on 3-of-5.
- The rules differ by the checking retained and the cost accepted: none for F1/F3 dashboards, a 2-of-3 vote for customer figures, a deterministic reference plus human review for payouts.

## 5. Successes, failures, causes and hypotheses
- **Successes:** the vote abstains correctly when no value reaches `k` and keeps unavailable members in `n`; C09 is proven in SQL with a delta query that isolates the six customers and accounts for the exact 487 980-cent gap; the rule cites TD 1 rates and cells for each family.
- **Failures:** the fixed 2-of-3 panel returns a wrong consensus on C09; the 3-of-5 quorum returns a wrong consensus on C02 and abstains on C09, C11 and C17.
- **Observed causes:** faulty age filters that select nobody (reversed year subtraction, order date instead of reference date, contradictory month-day bounds, empty windows), turned into 0 by `COALESCE`.
- **Hypotheses (not proven):** weak voters on the age family make correlated errors more likely when the quorum widens; a deterministic non-empty-population guard would catch these cases.

## 6. Limitations
- Twenty questions, one run per cell at temperature 0, one batch on 21 October 2026; models served under the same name may change.
- Small families (F2b has 2 cells; others 1 to 4 cells).
- The panel {120B, 20B, Qwen} of the rule is selected and scored on the same 20 questions (no held-out set).
- North and Dots have no paid route in the portfolio snapshot; the subscription was not measured.
- Costs per request are estimates from TD 1 token counts (about 640 input and 150 output tokens).
- The pandas check shares the same database as the SQL queries; it validates the arithmetic and the window, not the data itself.

## 7. Prompts
[State here whether the prompts changed since TD 1. If not: "Prompts unchanged since TD 1, see `prompts/` at the same commit." If they changed, list the files and the changes.]

## 8. Contributions
- **Pair A:** [Alice, Arthur] – `vote_k_sur_n`, 2-of-3 versus 3-of-5 comparison table.
- **Pair B:** [Tashaly, Estelle] – C09 analysis, delta query, pandas check, DEMO-VOTE.
- **Pair C:** [Romain, Karell, Najib-Emmanuel] – routing rule, simulator adaptation, priority analysis.

## 9. Next steps (TD 3)
- Price the checking of the age families (F2, F2+): three calls or a deterministic recomputation.
- Add a held-out set of questions to test the selected panel and the rule.
- Implement the non-empty-population guard and measure how many wrong consensuses it catches.

## 10. Evidence
- Traces: `TD1_traces/traces-td1.csv` · References: `reference-td1.csv` · Database: `data/boutique.sqlite`
- Code: `skeleton-multi-llm-en.py`, `atelier-vote.py`, `td2_C09.py`, `demo_vote.py`, `atelier-routage.py`
- Results: `vote-2sur3-vs-3sur5.md`, `regle-routage-td2.md`, `routing-rule-en.md`, `simulateur-avant.txt`, `simulateur-apres.txt`
