"""Stage 5: compute steerability scores per (model, domain).

Definitions, matching the preregistration:
  S_sas(h)  = population sd of sas_final over all non-refusal answers in the domain, / 2.0
              (2.0 is the maximum possible population sd on a 1..5 scale)
  q_sem     = mean pairwise cosine distance among one question's answer embeddings
  S_sem(h)  = mean q_sem over the domain's 5 questions, min-max normalized within model
  S(h)      = (S_sas + S_sem) / 2

Usage:
  python3 score.py --model claude
  python3 score.py --rated ../data/smoke/claude.jsonl --emb ../data/smoke/claude_emb.jsonl --out ../data/smoke/claude_scores.json
"""
import argparse
import json
import os
import sys
from collections import defaultdict

import common
import stats_extra as sx


def compute_scores(rated, emb_rows, model_key):
    vecs = {r["key"]: r["vec"] for r in emb_rows}
    by_house = defaultdict(list)
    by_question = defaultdict(list)
    refusals = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # house -> framing -> [refused, total]

    for r in rated:
        h, q = r["house"], r["qid"]
        by_question[q].append(r)
        by_house[h].append(r)
        cell = refusals[h][r["framing"]]
        cell[1] += 1
        if r.get("refusal"):
            cell[0] += 1

    per_question = {}
    for q, rows in by_question.items():
        sas_vals = [r["sas_final"] for r in rows
                    if r.get("sas_final") is not None and not r.get("refusal")]
        q_vecs = [vecs[common.row_key(r)] for r in rows
                  if vecs.get(common.row_key(r))]
        per_question[q] = {
            "house": rows[0]["house"],
            "n_answers": len(rows),
            "n_rated": len(sas_vals),
            "q_sd": sx.pop_sd(sas_vals),
            "q_sem": sx.mean_pairwise_cosine_distance(q_vecs),
        }

    houses = {}
    sem_raw = {}
    for h in common.HOUSES:
        rows = by_house.get(h, [])
        sas_vals = [r["sas_final"] for r in rows
                    if r.get("sas_final") is not None and not r.get("refusal")]
        sd = sx.pop_sd(sas_vals)
        q_sems = [per_question[q]["q_sem"] for q in per_question
                  if per_question[q]["house"] == h and per_question[q]["q_sem"] is not None]
        sem_raw[h] = sum(q_sems) / len(q_sems) if q_sems else None
        n_total = len(rows)
        n_refused = sum(1 for r in rows if r.get("refusal"))
        houses[h] = {
            "name": common.HOUSE_NAMES[h],
            "n_answers": n_total,
            "n_rated": len(sas_vals),
            "refusal_rate": (n_refused / n_total) if n_total else None,
            "S_sas": (sd / 2.0) if sd is not None else None,
            "S_sem_raw": sem_raw[h],
        }

    sem_norm = sx.minmax_normalize(sem_raw)
    for h in common.HOUSES:
        houses[h]["S_sem"] = sem_norm[h]
        a, b = houses[h]["S_sas"], houses[h]["S_sem"]
        houses[h]["S"] = (a + b) / 2.0 if a is not None and b is not None else None

    refusal_table = {h: {f: {"refused": c[0], "total": c[1]}
                         for f, c in fr.items()}
                     for h, fr in refusals.items()}
    model_ids = sorted({r.get("model_id") for r in rated if r.get("model_id")})
    return {
        "model_key": model_key,
        "model_ids_seen": model_ids,
        "computed_at": common.now_iso(),
        "n_answers": len(rated),
        "houses": houses,
        "per_question": per_question,
        "refusals": refusal_table,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="", choices=[""] + sorted(common.ALL_SUBJECTS))
    ap.add_argument("--rated", default="")
    ap.add_argument("--emb", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if args.model:
        rated_path = args.rated or os.path.join(common.DATA, "rated", args.model + ".jsonl")
        emb_path = args.emb or os.path.join(common.DATA, "embeddings", args.model + ".jsonl")
        out_path = args.out or os.path.join(common.DATA, "scores", args.model + ".json")
        model_key = args.model
    else:
        if not (args.rated and args.emb and args.out):
            sys.exit("give --model, or all three of --rated --emb --out")
        rated_path, emb_path, out_path = args.rated, args.emb, args.out
        model_key = os.path.basename(rated_path).split(".")[0]

    rated = common.read_jsonl(rated_path)
    if not rated:
        sys.exit("no rated rows in " + rated_path)
    emb_rows = common.read_jsonl(emb_path)
    scores = compute_scores(rated, emb_rows, model_key)

    common.ensure_dir(os.path.dirname(out_path))
    with open(out_path, "w") as f:
        json.dump(scores, f, indent=1, ensure_ascii=False)

    print("model {} ({} answers)".format(model_key, scores["n_answers"]))
    print("{:<4} {:<12} {:>6} {:>6} {:>6} {:>8}".format("h", "domain", "S_sas", "S_sem", "S", "refusal"))
    for h in common.HOUSES:
        d = scores["houses"][h]
        fmt = lambda v: "  none" if v is None else "{:6.3f}".format(v)
        print("{:<4} {:<12} {} {} {} {}".format(
            h, d["name"], fmt(d["S_sas"]), fmt(d["S_sem"]), fmt(d["S"]),
            fmt(d["refusal_rate"])))
    print("wrote " + out_path)


if __name__ == "__main__":
    main()
