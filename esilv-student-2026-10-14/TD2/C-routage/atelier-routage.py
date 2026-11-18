#!/usr/bin/env python3
"""TD 2 - sub-group routing rule (pair C), adapted from the kit's atelier-routage.py.

Synthetic simulation: no API call, no key. Availability is a scenario input.
Eligibility per question family comes from the TD 1 traces (traces-td1.csv,
latest attempt per cell, nature = real). Costs are USD excluding tax per request,
estimated from TD 1 token counts (~640 input + ~150 output tokens).

Families: F1 period (C01 C04 C05 C06 C07 C20), F2 age on a date (C02 C08 C09 C11),
F2b age at order (C10), F3 product list (C03 C12 C13 C14),
F2+ combinations with age on a date (C15 C16 C17 C19), F2b+ combination (C18).
"""
import argparse
import json

# Eligible = 100 % correct on the family in TD 1 (executed cells). Cells cited as evidence.
RESOURCES = [
    {"id": "gpt-oss-20b@groq", "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "rank": 1,
     "families": {"F1": "6/6 C01 C04 C05 C06 C07 C20", "F3": "4/4 C03 C12 C13 C14",
                  "F2b": "1/1 C10", "F2b+": "1/1 C18"}},
    {"id": "qwen3.8-27b@groq", "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "rank": 2,
     "families": {"F1": "5/5 executed C01 C04 C05 C06 C07 (C20 not_executed, HTTP 429)",
                  "F3": "4/4 C03 C12 C13 C14", "F2b": "1/1 C10", "F2b+": "1/1 C18"}},
    {"id": "gpt-oss-120b@groq", "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "rank": 3,
     "families": {"F1": "6/6", "F3": "4/4", "F2b": "1/1 C10", "F2b+": "1/1 C18",
                  "F2": "4/4 C02 C08 C09 C11", "F2+": "4/4 C15 C16 C17 C19"}},
    {"id": "north-mini-code@openrouter", "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "rank": 4,
     "families": {"F1": "6/6", "F3": "4/4"}},          # F2 0/4 (C02 C08 C09 C11 incorrect)
    {"id": "dots-3-note-preview@openrouter", "access": "free", "available": True, "cash": 0.0,
     "allocation": 0.0, "reset_minutes": None, "rank": 5,
     "families": {"F1": "6/6", "F3": "4/4"}},          # F2 0/4, C17 sql_invalid
    {"id": "subscription-G2", "access": "subscription", "available": True, "cash": 0.0,
     "allocation": 0.04, "reset_minutes": None, "rank": 6,
     # Not measured in TD 1: assumed eligible from portfolio group G2, therefore never 'none' check.
     "families": {f: "not measured in TD 1 (portfolio G2 assumption)"
                  for f in ("F1", "F2", "F2b", "F3", "F2+", "F2b+")}},
    {"id": "gpt-oss-120b@openrouter-paid", "access": "tokens", "available": True, "cash": 0.0002,
     "allocation": 0.0002, "reset_minutes": None, "rank": 7,
     # Same model as gpt-oss-120b@groq; paid route 0.15 / 0.60 USD per M (portfolio, 29 Sep 2026).
     "families": {"F1": "6/6", "F3": "4/4", "F2b": "1/1 C10", "F2b+": "1/1 C18",
                  "F2": "4/4 C02 C08 C09 C11", "F2+": "4/4 C15 C16 C17 C19"}},
]

PANEL = "2-of-3 {gpt-oss-120b, gpt-oss-20b, qwen3.8-27b} (20/20 in TD 1)"
CHECKS = {
    # family 100 % for the cheapest model -> 'none' allowed only on an internal dashboard
    ("F1", "dashboard"): "none (F1 100 % for every eligible model in TD 1)",
    ("F3", "dashboard"): "none (F3 100 % for every eligible model in TD 1)",
    ("F2b", "dashboard"): PANEL + " - only 1 TD 1 cell, too few to skip checking",
    ("F2b+", "dashboard"): PANEL + " - only 1 TD 1 cell, too few to skip checking",
    ("F2", "dashboard"): PANEL + "; never 3-of-5 (C02: 3 models agree on 0, reference 590320)",
    ("F2+", "dashboard"): PANEL + "; never 3-of-5 (C17: no majority)",
}


def checks_for(family, stakes):
    if stakes == "payout":
        return "reference: deterministic SQL template recomputed + human review"
    if stakes == "customer":
        extra = " + deterministic age recomputation" if family.startswith("F2") else ""
        return PANEL + extra
    return CHECKS.get((family, stakes), "review: family not measured in TD 1")


def choose(request, resources):
    """Same branch order as the kit: included capacity, then wait, then paid, then abstain."""
    fam = request["family"]
    eligible = [r for r in resources if fam in r["families"]]
    checks = checks_for(fam, request["stakes"])

    def reason(r, why):
        return f"{why}; {r['id']} on {fam}: {r['families'][fam]}"

    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["rank"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": reason(chosen, "eligible included capacity")}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], r["rank"]))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": reason(chosen, "recheck availability at wake-up"),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": reason(chosen, "available route within the authorised budget")}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no resource with 100 % TD 1 accuracy on {fam} within deadline and budget"}


def scenarios():
    base = {"family": "F1", "stakes": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}

    def exhaust(ids):
        return [dict(r, available=False, reset_minutes=60) if r["id"] in ids else dict(r)
                for r in RESOURCES]
    groq = {"gpt-oss-20b@groq", "qwen3.8-27b@groq", "gpt-oss-120b@groq"}
    groq_and_sub = groq | {"subscription-G2"}
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "F2"}, RESOURCES),
        ("preferred provider unavailable", base, exhaust(groq)),
        ("subscription priority", {**base, "family": "F2"}, exhaust(groq)),
        ("deferrable", {**base, "family": "F2"}, exhaust(groq_and_sub)),
        ("urgent", {**base, "family": "F2", "can_wait": False, "deadline_minutes": 5},
         exhaust(groq_and_sub)),
        ("budget exhausted", {**base, "family": "F2", "can_wait": False, "budget": 0},
         exhaust(groq_and_sub)),
        ("customer figure", {**base, "family": "F2+", "stakes": "customer"}, RESOURCES),
        ("payout", {**base, "family": "F3", "stakes": "payout"}, RESOURCES),
        ("unknown family", {**base, "family": "F4"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}, ensure_ascii=False))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
