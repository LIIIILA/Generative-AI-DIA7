import sqlite3

con = sqlite3.connect("data/boutique.sqlite")
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]

for t in tables:
    print("=== ", t)
    print(con.execute("SELECT sql FROM sqlite_master WHERE name=?", (t,)).fetchone()[0])
    for row in con.execute(f"SELECT * FROM {t} LIMIT 3"):
        print(row)
    print()