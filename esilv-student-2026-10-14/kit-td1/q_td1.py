import sqlite3, csv
from datetime import datetime, date

# ---------- 1) Requêtes SQL ----------
Q = {}
Q["C13"] = """SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o JOIN product p ON p.product_id = o.product_id
WHERE o.date >= '2026-04-01 00:00:00' AND o.date < '2026-05-01 00:00:00'
AND o.product_id IN ('a', 'c')"""

Q["C14"] = """SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o JOIN product p ON p.product_id = o.product_id
WHERE o.date >= '2026-10-01 00:00:00' AND o.date < '2026-12-01 00:00:00'
AND o.product_id IN ('a', 'b', 'c')"""

Q["C15"] = """SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON p.product_id = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.date >= '2026-03-01 00:00:00' AND o.date < '2026-06-01 00:00:00'
AND c.birth_date <= date('2026-09-25', '-25 years')
AND c.birth_date >  date('2026-09-25', '-26 years')"""

con = sqlite3.connect("data/boutique.sqlite")
sql_values = {k: con.execute(v).fetchone()[0] for k, v in Q.items()}

# ---------- 2) Recoupement indépendant, sur les CSV, sans SQL ----------
def read(name):
    with open("data/" + name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

price = {r["product_id"]: int(r["price"]) for r in read("product.csv")}
birth = {r["customer_id"]: datetime.strptime(r["birth_date"], "%Y-%m-%d").date()
         for r in read("customers.csv")}
lines = read("orders.csv")

def age_on(b, ref):
    return ref.year - b.year - ((ref.month, ref.day) < (b.month, b.day))

def total(start, end, products=None, age=None, ref=None):
    s = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    e = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    t = 0
    for r in lines:
        d = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S")
        if not (s <= d < e):
            continue
        if products and r["product_id"] not in products:
            continue
        if age is not None and age_on(birth[r["customer_id"]], ref) != age:
            continue
        t += int(r["quantity_product"]) * price[r["product_id"]]
    return t

csv_values = {
    "C13": total("2026-04-01 00:00:00", "2026-05-01 00:00:00", products={"a", "c"}),
    "C14": total("2026-10-01 00:00:00", "2026-12-01 00:00:00", products={"a", "b", "c"}),
    "C15": total("2026-03-01 00:00:00", "2026-06-01 00:00:00", age=25, ref=date(2026, 9, 25)),
}

# ---------- 3) Comparaison ----------
for k in Q:
    statut = "OK" if sql_values[k] == csv_values[k] else "DIFFERENT"
    print(k, "SQL =", sql_values[k], "| CSV =", csv_values[k], "|", statut)

# ---------- 4) Écriture de mes 3 lignes (à lancer seulement si tout est OK) ----------
with open("mes-lignes-td1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["question_id", "sql_query", "revenue_cents"])
    for k in Q:
        w.writerow([k, " ".join(Q[k].split()), sql_values[k]])
print("Fichier mes-lignes-td1.csv écrit.")