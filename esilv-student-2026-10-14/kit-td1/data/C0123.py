import sqlite3
import csv

db_path = "boutique.sqlite"

queries = {
    "C01": """
        SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
        FROM orders o
        JOIN product p ON o.product_id = p.product_id
        WHERE o.date >= '2026-03-01 00:00:00'
          AND o.date < '2026-06-01 00:00:00';
    """,
    "C02": """
        SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN product p ON o.product_id = p.product_id
        WHERE c.birth_date > date('2026-09-25', '-26 years')
          AND c.birth_date <= date('2026-09-25', '-25 years');
    """,
    "C03": """
        SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
        FROM orders o
        JOIN product p ON o.product_id = p.product_id
        WHERE o.date >= '2026-01-01 00:00:00'
          AND o.date < '2026-07-01 00:00:00'
          AND o.product_id IN ('a', 'b', 'c');
    """,
}

conn = sqlite3.connect(db_path)
cur = conn.cursor()

results = []
print(f"{'Question':<10} | {'Revenue (cents)':<18} | Status")
print("-" * 42)

for q_id, sql in queries.items():
  # Nettoyage de la chaîne SQL (sur une seule ligne compacte pour le CSV)
  clean_sql = " ".join(sql.split())
  cur.execute(clean_sql)
  (revenue_cents,) = cur.fetchone()

  results.append((q_id, clean_sql, revenue_cents))
  print(f"{q_id:<10} | {revenue_cents:<18} | OK")
  
conn.close()

with open("reference-td1.csv", mode="w", newline="", encoding="utf-8") as f:
  writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(["question_id", "query", "revenue_cents"])
  for q_id, clean_sql, revenue in results:
    writer.writerow([q_id, clean_sql, revenue])

print("-" * 42)
print(f"Fichier '{"reference-td1.csv"}' généré avec succès ({len(results)} lignes).")