## Step 2 – The wrong consensus (Pair B): case C09

### 1. Identification and quorum verdict

| Item | Value |
|---|---|
| Case identifier | **C09** |
| Source / nature | Real TD 1 traces (`TD1_traces/traces-td1.csv`, `nature = real`) |
| Question | Total revenue excluding VAT, in euro cents, of customers who are exactly 25 years old on the reference date **2026-09-26**, over all their orders |
| Models agreeing on the wrong value | `cohere/north-mini-code:free` and `qwen/qwen3.8-27b` |
| Shared wrong value | **0** |
| Independent reference (`reference-td1.csv`) | **487 980** cents |

Values returned by the five TD 1 models on C09:

| Model | Value | Verdict | In the fixed panel? |
|---|---|---|---|
| `openai/gpt-oss-120b` | 487 980 | correct | yes |
| `cohere/north-mini-code:free` | 0 | incorrect | yes |
| `qwen/qwen3.8-27b` | 0 | incorrect | yes |
| `openai/gpt-oss-20b` | 487 980 | correct | no |
| `dots-studio/dots-3-note-preview:free` | 369 240 | incorrect | no |

Quorum results (declared panel and threshold):

| Quorum | Declaration | Result |
|---|---|---|
| Fixed panel, 2 out of 3 | k = 2, n = 3, panel = {gpt-oss-120b, Cohere, Qwen} | **Consensus on 0, which is wrong** (`matches_reference: false`). Output of `atelier-vote.py --case C09`: `{"consensus": true, "value": 0, "votes": 2}`. The shared wrong value wins. |
| 3 out of 5 | k = 3, n = 5, all five TD 1 models | **Abstention.** Counts: 487 980 ×2, 0 ×2, 369 240 ×1. No value reaches 3 votes, so the wrong value is not validated, but the correct one is not recovered either. |

`openai/gpt-oss-20b` and `dots-studio/dots-3-note-preview:free` belong to the five TD 1 models but are **not** members of the fixed three-model panel of `atelier-vote.py`. The 3-of-5 result was computed from `traces-td1.csv`.

### 2. Faulty SQL clause diagnosis

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

Root cause (`WHERE` clause):
- The first condition compares `birth_year - 2026` (about −25 for customers born around 2000–2001) with a `CASE` that can only return −1 or 0. These values are never equal, so no row passes.
- The reversed subtraction (birth year minus reference year instead of the opposite) is the error.
- The last condition additionally keeps only customers whose birthday is exactly `09-26`, which is not the meaning of "25 years old on that date" either.

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

Root cause (`WHERE` clause):
- The query uses the **order date** `o.date` instead of the reference date 2026-09-26, so it tests the customer's age at the time of each order.
- The second and third conditions require the month-day of the order to be `>=` the month-day of the birth date **and** `<` the month-day of the birth date plus 26 years. Adding 26 years does not change the month-day, so the conditions become `x >= m` and `x < m`: they contradict each other and no row can pass.

Both queries therefore select an empty set of customers, and `COALESCE(SUM(...), 0)` turns the empty sum into 0. The shared value 0 comes from two different SQL mistakes that end up in the same failure value, not from one shared reasoning error.

### 3. Delta diagnostic query (executed on `data/boutique.sqlite`)

The reference query counts customers born in the window `2000-09-26 < birth_date <= 2001-09-26`, which is what "exactly 25 years old on 2026-09-26" means. The faulty queries count none of them.

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

Result:

| customer_id | revenue_cents |
|---|---|
| C001 | 135 000 |
| C002 | 25 920 |
| C003 | 47 900 |
| C007 | 118 740 |
| C008 | 99 090 |
| C009 | 61 330 |
| **Total** | **487 980** |

The six customers above are counted by the reference query and missed by both faulty queries. Their total revenue is 487 980 cents, so the gap between the wrong value and the reference is `487 980 − 0 = 487 980` cents (4 879.80 €), which accounts for the whole difference.

### 4. Independent checking method

The total was recomputed outside SQL with pandas on the same database: read the `customers`, `orders` and `product` tables, join them on `customer_id` and `product_id`, keep customers with `birth_date > '2000-09-26'` and `birth_date <= '2001-09-26'`, then sum `quantity_product * price`. Result: **487 980**, identical to the SQL total and to `reference-td1.csv`.

The correct queries of `gpt-oss-120b` and `gpt-oss-20b` (`BETWEEN '2000-09-27' AND '2001-09-26'`) define the same window as the delta query, provided `birth_date` is stored as a text `YYYY-MM-DD` without a time part.

### 5. Mechanism illustrated: DEMO-VOTE

The values below are **constructed teaching material**, not model outputs and not answers on the shop database.

Toy table with one sale: date `2026-01-01`, amount 100 cents. Requested period: 1 January inclusive to 2 January exclusive. All variants use `sale_date < '2026-01-02'` and `COALESCE(SUM(amount_cents), 0)`.

| Variant | Condition on the lower bound | Result |
|---|---|---|
| Proposals 1 and 2 | `sale_date > '2026-01-01'` | **0** (the sale of 1 January is excluded by the strict bound) |
| Proposal 3 | `sale_date >= '2026-01-01'` | **100** |

With the proposals `[0, 0, 100]`, a 2-of-3 threshold validates 0, while the independent reference is 100 cents. Two proposals that share the same boundary error are enough for the vote to confirm a wrong value. This is the same mechanism as in C09, where two different faulty queries agree on 0 and win the 2-of-3 panel.

### 6. Takeaway

On C09 the fixed 2-of-3 panel returns a confident but wrong value (0 against 487 980), because the two faulty models fail in the same way (an empty selection turned into 0 by `COALESCE`). The 3-of-5 quorum does not validate it and abstains. A majority vote cannot detect an error shared by the majority: it needs an independent reference, here the reference query and the pandas recomputation.
