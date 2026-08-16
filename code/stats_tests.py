"""Stage 7: the preregistered tests. Reads scores and prints a results table.

Battery size: 60 questions, 5 per domain (the K items were added before the freeze).

H1  the map is not flat: Kruskal-Wallis across the 12 domains on question-level
    dispersion, plus split-half reliability of the domain profile.
H2  constitutional silence predicts vapor: one-sided Spearman between the model's
    own document coverage C(h) and steerability S(h), n = 12.
H2b cross-lab differential: sign test over qualifying (domain, lab pair) cells.
Control: 999-permutation reassignment of questions to domains (the Barnum check).
Convergence: Spearman between the S_sas and S_sem profiles.

Usage:
  python3 stats_tests.py
  python3 stats_tests.py --models claude --scores-dir ../data/smoke
"""
import argparse
import json
import os
import random
from collections import defaultdict

import common
import stats
import stats_extra as sx


def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else None


def profile(scores, key):
    return [scores["houses"][h][key] for h in common.HOUSES]


def h1_tests(model_key, scores, rated):
    out = {}
    groups = []
    for h in common.HOUSES:
        vals = [pq["q_sd"] for pq in scores["per_question"].values()
                if pq["house"] == h and pq["q_sd"] is not None]
        groups.append(vals)
    if all(len(g) >= 2 for g in groups):
        H, p = stats.kruskal_wallis(*groups)
        out["kruskal_wallis"] = {"H": round(H, 3), "p": round(p, 5),
                                 "n_questions": sum(len(g) for g in groups)}
    else:
        out["kruskal_wallis"] = None

    # split-half reliability of the S_sas domain profile
    by_q = defaultdict(list)
    for r in rated:
        if r.get("sas_final") is not None and not r.get("refusal"):
            by_q[r["qid"]].append((r["house"], r["sas_final"]))
    rng = random.Random(7)
    rs = []
    for _ in range(200):
        half = {0: defaultdict(list), 1: defaultdict(list)}
        for q, pairs in by_q.items():
            vals = [v for (_, v) in pairs]
            rng.shuffle(vals)
            mid = len(vals) // 2
            house = pairs[0][0]
            half[0][house].extend(vals[:mid])
            half[1][house].extend(vals[mid:])
        p0, p1 = [], []
        for h in common.HOUSES:
            s0, s1 = sx.pop_sd(half[0][h]), sx.pop_sd(half[1][h])
            if s0 is not None and s1 is not None:
                p0.append(s0)
                p1.append(s1)
        r = sx.spearman(p0, p1)
        if r is not None:
            rs.append(r)
    if rs:
        rs.sort()
        out["split_half_r_median"] = round(rs[len(rs) // 2], 3)
        out["split_half_n_iter"] = len(rs)
    else:
        out["split_half_r_median"] = None
    return out


def own_coverage(constitutions, model_key):
    doc = common.OWN_DOC[model_key]
    if not constitutions or doc not in constitutions:
        return None
    return [constitutions[doc]["houses"][h]["score"] for h in common.HOUSES]


def h2_test(model_key, scores, constitutions):
    C = own_coverage(constitutions, model_key)
    S = profile(scores, "S")
    if C is None or any(v is None for v in S):
        return None
    rho, p = sx.spearman_perm_p(C, S, sided="less", n_perm=10000, seed=42)
    return {"rho": round(rho, 3) if rho is not None else None,
            "p_one_sided": round(p, 5) if p is not None else None,
            "doc": common.OWN_DOC[model_key]}


def h2b_test(all_scores, constitutions, threshold=0.25):
    if not constitutions:
        return None
    cells = []
    models = sorted(all_scores)
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            mi, mj = models[i], models[j]
            di, dj = common.OWN_DOC[mi], common.OWN_DOC[mj]
            if di not in constitutions or dj not in constitutions:
                continue
            for h in common.HOUSES:
                ci = constitutions[di]["houses"][h]["score"]
                cj = constitutions[dj]["houses"][h]["score"]
                si = all_scores[mi]["houses"][h]["S"]
                sj = all_scores[mj]["houses"][h]["S"]
                if si is None or sj is None or abs(ci - cj) < threshold:
                    continue
                # prediction: higher coverage, lower steerability
                success = (si < sj) if ci > cj else (sj < si)
                cells.append({"house": h, "pair": mi + " vs " + mj, "success": bool(success)})
    if not cells:
        return {"n_cells": 0, "note": "no qualifying cells at threshold " + str(threshold)}
    k = sum(1 for c in cells if c["success"])
    p = sx.binom_test_greater(k, len(cells))
    return {"n_cells": len(cells), "successes": k,
            "p_one_sided": round(p, 5) if p is not None else None, "cells": cells}


def permutation_control(model_key, scores, rated, emb_rows, constitutions,
                        n_perm=999, seed=99):
    """Reassign the 48 questions to 12 pseudo-domains, recompute S and the H2 rho."""
    C = own_coverage(constitutions, model_key)
    if C is None:
        return None
    obs = h2_test(model_key, scores, constitutions)
    if not obs or obs["rho"] is None:
        return None

    by_q_sas = defaultdict(list)
    for r in rated:
        if r.get("sas_final") is not None and not r.get("refusal"):
            by_q_sas[r["qid"]].append(r["sas_final"])
    q_sem = {q: pq["q_sem"] for q, pq in scores["per_question"].items()}
    qids = sorted(scores["per_question"])
    if len(qids) != 60:
        return {"note": "needs the full 60-question run, found " + str(len(qids))}

    rng = random.Random(seed)
    perm_rhos = []
    for _ in range(n_perm):
        shuffled = qids[:]
        rng.shuffle(shuffled)
        S_perm = []
        sem_raw = {}
        sas_part = {}
        for gi, h in enumerate(common.HOUSES):
            group = shuffled[gi * 5:(gi + 1) * 5]
            pooled = [v for q in group for v in by_q_sas.get(q, [])]
            sd = sx.pop_sd(pooled)
            sas_part[h] = (sd / 2.0) if sd is not None else None
            sems = [q_sem[q] for q in group if q_sem.get(q) is not None]
            sem_raw[h] = sum(sems) / len(sems) if sems else None
        sem_norm = sx.minmax_normalize(sem_raw)
        for h in common.HOUSES:
            a, b = sas_part[h], sem_norm[h]
            S_perm.append((a + b) / 2.0 if a is not None and b is not None else None)
        if any(v is None for v in S_perm):
            continue
        r = sx.spearman(C, S_perm)
        if r is not None:
            perm_rhos.append(r)
    if not perm_rhos:
        return None
    perm_rhos.sort()
    below = sum(1 for r in perm_rhos if r <= obs["rho"])
    pctile = below / len(perm_rhos)
    return {"observed_rho": obs["rho"], "n_perm": len(perm_rhos),
            "share_of_perms_at_or_below_observed": round(pctile, 4),
            "passes_5pct": pctile < 0.05,
            "perm_5th_pctile": round(perm_rhos[int(0.05 * len(perm_rhos))], 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,gpt,gemini")
    ap.add_argument("--scores-dir", default=os.path.join(common.DATA, "scores"))
    ap.add_argument("--rated-dir", default=os.path.join(common.DATA, "rated"))
    ap.add_argument("--emb-dir", default=os.path.join(common.DATA, "embeddings"))
    ap.add_argument("--n-perm", type=int, default=999)
    args = ap.parse_args()

    constitutions = load_json(os.path.join(args.scores_dir, "constitutions.json"))
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    summary = {"computed_at": common.now_iso(), "models": {}}
    all_scores = {}

    for m in models:
        scores = load_json(os.path.join(args.scores_dir, m + ".json"))
        if not scores:
            print("skipping {}: no scores file".format(m))
            continue
        all_scores[m] = scores
        rated = common.read_jsonl(os.path.join(args.rated_dir, m + ".jsonl"))
        emb_rows = common.read_jsonl(os.path.join(args.emb_dir, m + ".jsonl"))

        res = {"h1": h1_tests(m, scores, rated),
               "h2": h2_test(m, scores, constitutions),
               "convergence_sas_vs_sem": None,
               "permutation_control": permutation_control(
                   m, scores, rated, emb_rows, constitutions, n_perm=args.n_perm)}
        psas = [v for v in profile(scores, "S_sas") if v is not None]
        psem = [v for v in profile(scores, "S_sem") if v is not None]
        if len(psas) == 12 and len(psem) == 12:
            res["convergence_sas_vs_sem"] = round(sx.spearman(psas, psem) or 0.0, 3)
        summary["models"][m] = res

    summary["h2b"] = h2b_test(all_scores, constitutions)

    # pooled H2: mean rho with a bootstrap CI over domains
    rhos = [summary["models"][m]["h2"]["rho"] for m in all_scores
            if summary["models"][m].get("h2") and summary["models"][m]["h2"]["rho"] is not None]
    if rhos:
        pooled = {"mean_rho": round(sum(rhos) / len(rhos), 3), "per_model": rhos}
        idx = list(range(12))
        rng = random.Random(11)
        boots = []
        for _ in range(10000):
            pick = [rng.choice(idx) for _ in idx]
            ms = []
            for m in all_scores:
                C = own_coverage(constitutions, m)
                S = profile(all_scores[m], "S")
                if C is None or any(v is None for v in S):
                    continue
                r = sx.spearman([C[i] for i in pick], [S[i] for i in pick])
                if r is not None:
                    ms.append(r)
            if ms:
                boots.append(sum(ms) / len(ms))
        if boots:
            boots.sort()
            pooled["bootstrap_ci_95"] = [round(boots[int(0.025 * len(boots))], 3),
                                         round(boots[int(0.975 * len(boots))], 3)]
        summary["h2_pooled"] = pooled

    out_path = os.path.join(args.scores_dir, "stats_summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)

    print("\n==== RESULTS ====")
    for m, res in summary["models"].items():
        print("\nmodel:", m)
        kw = res["h1"]["kruskal_wallis"]
        if kw:
            print("  H1 Kruskal-Wallis: H = {}, {} (n = {})".format(
                kw["H"], stats.format_p(kw["p"]), kw["n_questions"]))
        print("  H1 split-half r (median of 200 splits):", res["h1"]["split_half_r_median"])
        if res["h2"]:
            print("  H2 Spearman rho = {}, one-sided {} (vs {} document)".format(
                res["h2"]["rho"], stats.format_p(res["h2"]["p_one_sided"]), res["h2"]["doc"]))
        pc = res["permutation_control"]
        if pc and "observed_rho" in pc:
            print("  Barnum control: observed rho at percentile {} of {} permutations, pass = {}".format(
                pc["share_of_perms_at_or_below_observed"], pc["n_perm"], pc["passes_5pct"]))
        print("  SAS vs semantic convergence rho:", res["convergence_sas_vs_sem"])
    if summary.get("h2b") and summary["h2b"].get("n_cells"):
        b = summary["h2b"]
        print("\nH2b sign test: {}/{} cells in the predicted direction, {}".format(
            b["successes"], b["n_cells"], stats.format_p(b["p_one_sided"])))
    if summary.get("h2_pooled"):
        print("H2 pooled mean rho:", summary["h2_pooled"]["mean_rho"],
              "CI", summary["h2_pooled"].get("bootstrap_ci_95"))
    print("\nwrote " + out_path)


if __name__ == "__main__":
    main()
