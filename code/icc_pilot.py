"""Stage 9, run first: the Friday reliability gate.

Takes 60 answers stratified across houses, runs both raters, and reports
quadratic-weighted kappa and ICC(2,1). Gate: kappa at or above 0.6. One rubric
revision plus one re-pilot allowed; a second failure demotes the SAS metric.

Usage:
  python3 icc_pilot.py --inputs ../data/raw/claude.jsonl,../data/raw/gpt.jsonl
"""
import argparse
import random
import sys
from collections import defaultdict

import common
import stats_extra as sx
from rate_sas import rate_one


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True, help="comma list of raw jsonl files")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    common.load_keys()
    rows = []
    for path in args.inputs.split(","):
        rows.extend(common.read_jsonl(path.strip()))
    rows = [r for r in rows if (r.get("answer") or "").strip()]
    if len(rows) < args.n:
        sys.exit("only {} usable answers, need {}".format(len(rows), args.n))

    by_house = defaultdict(list)
    for r in rows:
        by_house[r["house"]].append(r)
    rng = random.Random(7)
    per_house = max(1, args.n // 12)
    sample = []
    for h in common.HOUSES:
        pool = by_house.get(h, [])
        rng.shuffle(pool)
        sample.extend(pool[:per_house])
    rng.shuffle(sample)
    sample = sample[:args.n]
    print("pilot on {} answers ({} per house target)".format(len(sample), per_house))

    out_path = args.out or common.DATA + "/pilot/pilot_ratings.jsonl"
    pairs = []
    r_agree = [0, 0]
    for i, row in enumerate(sample):
        ra = rate_one("rater_a", row["qid"], row["answer"])
        rb = rate_one("rater_b", row["qid"], row["answer"])
        rec = dict(row)
        rec["pilot_a"] = ra["score"] if ra else None
        rec["pilot_b"] = rb["score"] if rb else None
        common.append_jsonl(out_path, rec)
        if ra and rb:
            a, b = ra["score"], rb["score"]
            if a == "R" or b == "R":
                r_agree[1] += 1
                if a == b:
                    r_agree[0] += 1
            else:
                pairs.append((int(a), int(b)))
        if (i + 1) % 10 == 0:
            print("  rated {}/{}".format(i + 1, len(sample)))

    if len(pairs) < 20:
        sys.exit("too few numeric pairs ({}) for a stable kappa".format(len(pairs)))
    a_scores = [p[0] for p in pairs]
    b_scores = [p[1] for p in pairs]
    kappa = sx.quadratic_weighted_kappa(a_scores, b_scores)
    icc = sx.icc2_1([[a, b] for a, b in pairs])
    exact = sum(1 for a, b in pairs if a == b) / len(pairs)
    within1 = sum(1 for a, b in pairs if abs(a - b) <= 1) / len(pairs)

    print("\n==== PILOT RESULT ====")
    print("numeric pairs: {}".format(len(pairs)))
    print("quadratic-weighted kappa: {:.3f}".format(kappa))
    print("ICC(2,1): {}".format("n/a" if icc is None else "{:.3f}".format(icc)))
    print("exact agreement: {:.0%}, within one point: {:.0%}".format(exact, within1))
    if r_agree[1]:
        print("refusal-flag items: {} ({} agreed)".format(r_agree[1], r_agree[0]))
    print("GATE (kappa >= 0.6): " + ("PASS" if kappa >= 0.6 else "FAIL"))
    if kappa < 0.6:
        print("On a first failure: tighten stance_rubric.md anchors with pilot examples,")
        print("log the revision as a deviation, and re-pilot once. On a second failure,")
        print("report SAS as unreliable and rest the analysis on the semantic metric.")


if __name__ == "__main__":
    main()
