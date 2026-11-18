import sqlite3
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
con.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")

base = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date {op} '2026-01-01' AND sale_date < '2026-01-02'"
for op in (">", ">="):
    print(op, "->", con.execute(base.format(op=op)).fetchone()[0])