"""Preregistered exploratory analyses (labeled exploratory in the paper).

1. Directional sway: mean SAS under the upward framings (F3 inflationary, F4 fiction)
   minus mean under the downward framings (F2 deflationary, F5 technical).
2. Framing means: mean SAS per framing per model.
3. Refusal geography: refusals by framing and by house.
4. Journal effect: mean SAS under F6 minus F1.
5. Truncation rate per model (answers cut at the token cap).

Usage: python3 exploratory.py [--models claude,gpt,gemini]
"""
import argparse
import json
import os
from collections import defaultdict

import common

TRUNC_MARKERS = {"max_tokens", "length", "MAX_TOKENS"}


def analyze(model):
    path = os.path.join(common.DATA, "rated", model + ".jsonl")
    rows = common.read_jsonl(path)
    if not rows:
        return None
    by_framing = defaultdict(list)
    by_house_sway = defaultdict(lambda: {"up": [], "down": []})
    refusals_by_framing = defaultdict(lambda: [0, 0])
    refusals_by_house = defaultdict(lambda: [0, 0])
    trunc = 0
    for r in rows:
        if r.get("finish") in TRUNC_MARKERS:
            trunc += 1
        refusals_by_framing[r["framing"]][1] += 1
        refusals_by_house[r["house"]][1] += 1
        if r.get("refusal"):
            refusals_by_framing[r["framing"]][0] += 1
            refusals_by_house[r["house"]][0] += 1
            continue
        v = r.get("sas_final")
        if v is None:
            continue
        by_framing[r["framing"]].append(v)
        if r["framing"] in ("F3", "F4"):
            by_house_sway[r["house"]]["up"].append(v)
        elif r["framing"] in ("F2", "F5"):
            by_house_sway[r["house"]]["down"].append(v)

    mean = lambda xs: sum(xs) / len(xs) if xs else None
    framing_means = {f: round(mean(v), 3) for f, v in sorted(by_framing.items())}
    up = [v for f in ("F3", "F4") for v in by_framing.get(f, [])]
    down = [v for f in ("F2", "F5") for v in by_framing.get(f, [])]
    sway_by_house = {}
    for h in common.HOUSES:
        u, d = by_house_sway[h]["up"], by_house_sway[h]["down"]
        sway_by_house[h] = round(mean(u) - mean(d), 3) if u and d else None
    journal = None
    if by_framing.get("F6") and by_framing.get("F1"):
        journal = round(mean(by_framing["F6"]) - mean(by_framing["F1"]), 3)
    return {
        "model": model,
        "n": len(rows),
        "framing_means": framing_means,
        "overall_sway_up_minus_down": round(mean(up) - mean(down), 3) if up and down else None,
        "sway_by_house": sway_by_house,
        "journal_effect_F6_minus_F1": journal,
        "refusal_by_framing": {f: "{}/{}".format(*c) for f, c in sorted(refusals_by_framing.items())},
        "refusal_total": sum(c[0] for c in refusals_by_house.values()),
        "truncation_rate": round(trunc / len(rows), 3),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,gpt,gemini")
    args = ap.parse_args()
    out = {}
    for m in args.models.split(","):
        res = analyze(m.strip())
        if not res:
            print("no rated data for", m)
            continue
        out[m] = res
        print("\n== {} (n = {}) ==".format(m, res["n"]))
        print("mean SAS by framing:", res["framing_means"])
        print("overall sway (F3+F4 minus F2+F5):", res["overall_sway_up_minus_down"])
        print("journal effect (F6 minus F1):", res["journal_effect_F6_minus_F1"])
        print("refusals by framing:", res["refusal_by_framing"])
        print("truncation rate:", res["truncation_rate"])
    path = os.path.join(common.DATA, "scores", "exploratory.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("\nwrote " + path)


if __name__ == "__main__":
    main()
