#!/usr/bin/env python3
"""TD 2, Pair A : tableau 2-of-3 (panel fixe) contre 3-of-5 sur les traces du TD 1.

Usage, depuis kit-td1 :
    python comparaison_quorums.py --traces traces-td1.csv --reference reference-td1.csv
    python comparaison_quorums.py ... --out reports/vote-2sur3-vs-3sur5.md

Le vote utilisé est Orchestrateur.vote_k_sur_n de skeleton-multi-llm-en.py
(celui que vous avez complété). Aucun appel réseau : seulement les traces stockées.
Le vote ne voit jamais la référence : la comparaison vient après la décision.
"""
import argparse
import csv
import importlib.util
import os
import sys

PANEL_2SUR3 = ["openai/gpt-oss-120b", "cohere/north-mini-code:free", "qwen/qwen3.8-27b"]
TOUS_5 = PANEL_2SUR3[:1] + ["openai/gpt-oss-20b"] + PANEL_2SUR3[1:] + [
    "dots-studio/dots-3-note-preview:free"]
CASES = [f"C{i:02d}" for i in range(1, 21)]

# Noms de colonnes possibles (le premier trouvé est utilisé)
COL_CASE = ["case_id", "case", "question_id", "question"]
COL_PROVIDER = ["provider"]
COL_MODEL = ["model_requested", "model", "modele"]
COL_VALUE = ["value", "revenue_cents", "valeur", "result_value"]
COL_VERDICT = ["verdict", "status"]
COL_ATTEMPT = ["attempts", "attempt", "tentative", "retry", "attempt_index"]
MOTS_ERREUR = ("not_executed", "invalid", "error", "erreur", "unavailable", "timeout", "http", "429", "fail")


def colonne(fieldnames, candidats, obligatoire=True):
    for c in candidats:
        if c in fieldnames:
            return c
    if obligatoire:
        sys.exit(f"Colonne introuvable parmi {candidats}. Colonnes du fichier : {fieldnames}\n"
                 "-> adapte la liste correspondante en haut du script.")
    return None


def charger_vote(skeleton):
    """Récupère vote_k_sur_n du squelette ; le self n'est pas utilisé par la méthode."""
    spec = importlib.util.spec_from_file_location("skeleton_td", skeleton)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod             # required by the dataclasses of the skeleton
    spec.loader.exec_module(mod)
    orch = object.__new__(mod.Orchestrateur)   # pas besoin du constructeur
    return orch.vote_k_sur_n


def entier_ou_none(x):
    x = (x or "").strip()
    if x == "" or x.lower() in ("none", "null", "nan"):
        return None
    try:
        return int(float(x))
    except ValueError:
        return None


def nom_modele(brut):
    """Normalise 'groq/openai/gpt-oss-120b' -> 'openai/gpt-oss-120b'."""
    for m in TOUS_5:
        if brut == m or brut.endswith("/" + m) or brut.endswith(m):
            return m
    return brut


def lire_traces(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        fn = lecteur.fieldnames
        c_case, c_prov = colonne(fn, COL_CASE), colonne(fn, COL_PROVIDER)
        c_mod, c_val = colonne(fn, COL_MODEL), colonne(fn, COL_VALUE)
        c_ver, c_att = colonne(fn, COL_VERDICT), colonne(fn, COL_ATTEMPT, False)
        derniere = {}   # (case, modèle) -> dernière tentative
        for ordre, ligne in enumerate(lecteur):
            case, modele = ligne[c_case].strip(), nom_modele(ligne[c_mod].strip())
            rang = (entier_ou_none(ligne[c_att]) or 0, ordre) if c_att else (0, ordre)
            if (case, modele) not in derniere or rang >= derniere[(case, modele)][0]:
                derniere[(case, modele)] = (rang, ligne, c_prov, c_val, c_ver)
    return derniere


def proposition(derniere, case, modele):
    """Dict au format attendu par vote_k_sur_n ; un modèle absent = indisponible."""
    if (case, modele) not in derniere:
        return {"provider": "?", "model_requested": modele, "value": None,
                "verdict": "error", "verdict_trace": "absent"}
    _, ligne, c_prov, c_val, c_ver = derniere[(case, modele)]
    v_trace = (ligne[c_ver] or "").strip()
    valeur = entier_ou_none(ligne[c_val])
    erreur = valeur is None or any(m in v_trace.lower() for m in MOTS_ERREUR)
    return {"provider": ligne[c_prov].strip(), "model_requested": modele,
            "value": None if erreur else valeur,
            "verdict": "error" if erreur else "executed",
            "verdict_trace": v_trace, "valeur_trace": ligne[c_val]}


def lire_reference(chemin, traces_csv):
    if not os.path.exists(chemin):   # repli : colonne reference des traces
        print(f"(info) {chemin} absent : référence lue dans la colonne 'reference' de {traces_csv}",
              file=sys.stderr)
        chemin = traces_csv
    with open(chemin, newline="", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        c_case = colonne(lecteur.fieldnames, COL_CASE)
        c_val = colonne(lecteur.fieldnames, ["revenue_cents", "reference", "value"])
        return {l[c_case].strip(): entier_ou_none(l[c_val]) for l in lecteur}


def decision_txt(d):
    return f"consensus {d['value']} ({d['votes']} voix)" if d["consensus"] \
        else f"abstention (max {d['votes']} voix)"


def accord(d, ref):
    if not d["consensus"]:
        return "abstention"
    return "oui" if d["value"] == ref else "**NON**"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traces", default="traces-td1.csv")
    p.add_argument("--reference", default="reference-td1.csv")
    p.add_argument("--skeleton", default="skeleton-multi-llm-en.py")
    p.add_argument("--out", default=None)
    a = p.parse_args()

    vote = charger_vote(a.skeleton)
    traces, ref = lire_traces(a.traces), lire_reference(a.reference, a.traces)

    lignes = ["| Question | Référence | 2-of-3 (panel fixe) | Accord | 3-of-5 | Accord | Change ? |",
              "|---|---|---|---|---|---|---|"]
    details = []
    stats = {"2sur3": [0, 0, 0], "3sur5": [0, 0, 0]}   # justes, faux, abstentions
    for case in CASES:
        p3 = [proposition(traces, case, m) for m in PANEL_2SUR3]
        p5 = [proposition(traces, case, m) for m in TOUS_5]
        d3, d5 = vote(p3, 2), vote(p5, 3)
        r = ref.get(case)
        for cle, d in (("2sur3", d3), ("3sur5", d5)):
            idx = 2 if not d["consensus"] else (0 if d["value"] == r else 1)
            stats[cle][idx] += 1
        change = (d3["consensus"], d3["value"]) != (d5["consensus"], d5["value"])
        lignes.append(f"| {case} | {r} | {decision_txt(d3)} | {accord(d3, r)} | "
                      f"{decision_txt(d5)} | {accord(d5, r)} | {'**oui**' if change else 'non'} |")
        if change:
            props = "; ".join(f"`{x['model_requested']}` -> {x['valeur_trace'] if 'valeur_trace' in x else '—'}"
                              f" ({x['verdict_trace']})" for x in p5)
            details.append(f"- **{case}** (référence {r}) : 2-of-3 = {decision_txt(d3)}, "
                           f"3-of-5 = {decision_txt(d5)}.\n  Dernières tentatives : {props}.\n"
                           f"  Explication : _à rédiger (abstention devenue consensus ? marge "
                           f"modifiée par un 429 / SQL invalide ?)_")

    resume = ["", "| Quorum | Consensus justes | Consensus faux | Abstentions |",
              "|---|---|---|---|",
              f"| 2-of-3 panel fixe | {stats['2sur3'][0]} | {stats['2sur3'][1]} | {stats['2sur3'][2]} |",
              f"| 3-of-5 | {stats['3sur5'][0]} | {stats['3sur5'][1]} | {stats['3sur5'][2]} |"]
    texte = "\n".join(["## Vote 2-of-3 (panel fixe) contre 3-of-5 sur les traces du TD 1", ""]
                      + lignes + resume
                      + ["", "### Questions où la décision change", ""]
                      + (details or ["Aucune : les deux quorums prennent la même décision partout."]))
    print(texte)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(texte + "\n")
        print(f"\n-> écrit dans {a.out}")


if __name__ == "__main__":
    main()
