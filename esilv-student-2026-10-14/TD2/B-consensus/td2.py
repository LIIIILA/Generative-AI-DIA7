import pandas as pd
pd.set_option("display.max_colwidth", None)
t = pd.read_csv("TD1_traces/traces-td1.csv", dtype={"value": "string"})
t = t[t.nature == "real"]
t["attempts"] = t["attempts"].astype(int)
t = t.sort_values("attempts").groupby(["model_requested", "case_id"], as_index=False).last()

for case in ["C02", "C09"]:
    print("=====", case)
    d = t[t.case_id == case]
    print(d[["model_requested", "value", "verdict", "reference"]].to_string(index=False))
    for _, r in d.iterrows():
        print("\n--", r.model_requested, "--")
        print(r["sql"])