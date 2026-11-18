import sqlite3
import pandas as pd

DB = r"C:\10_generative_ai\esilv-student-2026-10-14\kit-td1\data\boutique.sqlite"   # adapte le chemin si besoin
t = pd.read_csv(r"TD1_traces\traces-td1.csv")
c = t[t.case_id == "C09"].set_index("model_returned")
con = sqlite3.connect(DB)

print("=== 1. Requêtes fautives ===")
for m in ["cohere/north-mini-code:free", "qwen/qwen3.8-27b"]:
    print(m, "->", con.execute(c.loc[m, "sql"]).fetchall())

print("\n=== 2. Delta : clients de la fenêtre correcte ===")
q = """
SELECT c.customer_id, SUM(o.quantity_product * p.price) AS revenue_cents
FROM customers c
JOIN orders o  ON o.customer_id = c.customer_id
JOIN product p ON p.product_id  = o.product_id
WHERE c.birth_date >  '2000-09-26' AND c.birth_date <= '2001-09-26'
GROUP BY c.customer_id ORDER BY c.customer_id
"""
rows = con.execute(q).fetchall()
for r in rows:
    print(r)
print("TOTAL SQL :", sum(r[1] for r in rows))

print("\n=== 3. Vérification indépendante (pandas) ===")
cu = pd.read_sql("SELECT * FROM customers", con)
o = pd.read_sql("SELECT * FROM orders", con)
p = pd.read_sql("SELECT * FROM product", con)
m = o.merge(cu, on="customer_id").merge(p, on="product_id")
m = m[(m.birth_date > "2000-09-26") & (m.birth_date <= "2001-09-26")]
print("TOTAL pandas :", (m.quantity_product * m.price).sum())