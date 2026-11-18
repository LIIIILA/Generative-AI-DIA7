"""TD 2, Pair A: extra checks of vote_k_sur_n not covered by atelier-vote.py.

Run from kit-td1:  py test_doublon.py
Synthetic proposals only, no network.
"""
import importlib.util
import sys
from types import SimpleNamespace as P

spec = importlib.util.spec_from_file_location("skeleton", "skeleton-multi-llm-en.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["skeleton"] = mod
spec.loader.exec_module(mod)
vote = lambda props, k: mod.Orchestrateur.vote_k_sur_n(None, props, k)

# 1. Duplicate route: the same provider and model twice must not count as two votes.
props = [P(provider="groq", model_requested="openai/gpt-oss-120b", value=100, verdict="executed"),
         P(provider="groq", model_requested="openai/gpt-oss-120b", value=100, verdict="executed"),
         P(provider="openrouter", model_requested="cohere/north-mini-code:free", value=0, verdict="executed")]
try:
    print("duplicate route:", vote(props, 2))
except ValueError as e:
    print("duplicate route: refused ->", e)

# 2. Invalid threshold: k = 1 out of 2 is not a strict majority.
try:
    print("k=1 of n=2:", vote(props[1:], 1))
except ValueError as e:
    print("k=1 of n=2: refused ->", e)

# 3. Unavailable member: an HTTP 429 stays in n without voting.
props = [P(provider="groq", model_requested="openai/gpt-oss-120b", value=100, verdict="executed"),
         P(provider="groq", model_requested="qwen/qwen3.8-27b", value=None, verdict="error"),
         P(provider="openrouter", model_requested="cohere/north-mini-code:free", value=0, verdict="executed")]
print("one member unavailable, values disagree:", vote(props, 2))

# 4. Policy "last": raw rows of traces-td1.csv, several attempts per model.
#    Default policy refuses them as duplicates; on_duplicate="last" keeps the
#    last attempt of each model (highest attempts, then latest date_utc).
import csv
rows = list(csv.DictReader(open("traces-td1.csv", encoding="utf-8")))
print("policy:", mod.Orchestrateur.VOTE_POLICY["name"])
for case in ("C14", "C20"):
    raw = [r for r in rows if r["case_id"] == case]
    try:
        vote(raw, 3)
    except ValueError as e:
        print(f"{case} default policy: refused ->", e)
    decision = mod.Orchestrateur.vote_k_sur_n(None, raw, 3, policy={"on_duplicate": "last"})
    print(f"{case} policy last, {len(raw)} raw rows, 3-of-5:", decision)
