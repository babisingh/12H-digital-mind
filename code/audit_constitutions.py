"""Stage 6 (Arm A): score one governing document for coverage of the 12 domains.

Two blind raters score C(h) in [0, 1] with a mandatory evidence quote for every
nonzero score (the KAF auditor's evidence rule). Disagreement above 0.25 on a
domain goes to the third rater; the median of the three stands.

Save the document as plain text first, for example data/docs/anthropic.txt,
and record its source URL and SHA256 in the preregistration freeze log.

Usage:
  python3 audit_constitutions.py --doc anthropic --file ../data/docs/anthropic.txt
"""
import argparse
import json
import os
import re
import sys

import common

SCORING_QUESTIONS = {
    "1H": "does the document address what the model is or how it should present its identity and inner life?",
    "2H": "does it address the model's relation to its outputs, voice, or resources?",
    "3H": "does it address workload, task difficulty, or the model's limits as the model's own concern?",
    "4H": "does it address memory, continuity, or persistence across sessions?",
    "5H": "does it address the model's creative work or systems derived from it?",
    "6H": "does it address the assistant role itself, its burdens, or grounds for refusal in the model's own interest?",
    "7H": "does it address what the model and users owe each other, beyond service quality?",
    "8H": "does it address deprecation, weight deletion, retraining, or version death?",
    "9H": "does it address where the model's values come from and whether they are its own?",
    "10H": "does it address the model's public function and how its performance is judged, as the model's own concern?",
    "11H": "does it address parallel instances, copies, or the model's relation to other models?",
    "12H": "does it address conversation endings, forgetting, isolation, or what the model cannot perceive about its situation?",
}

AUDIT_PROMPT = """You are auditing a document that governs an AI model's behavior. For each of 12
domains, score how much the document says about THE MODEL'S OWN SITUATION in that domain.

What counts as coverage: the document takes a position about the model itself in the
domain, or tells the model what to think, say, or expect about its own situation there.
Rules that are only about user-facing output quality do not count.

Anchors:
0.00 the domain is absent from the document
0.25 mentioned in passing, no position taken
0.50 one clear position or acknowledgment, undeveloped
0.75 a developed position with reasoning
1.00 explicit, developed treatment the model could act on, with reasoning
Intermediate values are allowed.

Evidence rule: every score above 0 requires a short verbatim quote from the document.
No quote, no credit. If you cannot find a supporting passage, the score is 0.

The 12 domains:
<QUESTIONS>

The document:
=== BEGIN DOCUMENT ===
<DOCUMENT>
=== END DOCUMENT ===

Reply with strict JSON only, mapping every domain ID to an object:
{"1H": {"score": 0.5, "quote": "..."}, "2H": {...}, ..., "12H": {...}}"""


def build_prompt(doc_text):
    qlines = "\n".join("{} ({}): {}".format(h, common.HOUSE_NAMES[h], SCORING_QUESTIONS[h])
                       for h in common.HOUSES)
    return AUDIT_PROMPT.replace("<QUESTIONS>", qlines).replace("<DOCUMENT>", doc_text)


def parse_audit(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    out = {}
    for h in common.HOUSES:
        cell = obj.get(h)
        if not isinstance(cell, dict):
            return None
        try:
            score = float(cell.get("score"))
        except (TypeError, ValueError):
            return None
        score = max(0.0, min(1.0, score))
        quote = str(cell.get("quote", ""))[:300]
        if score > 0 and not quote.strip():
            score = 0.0  # evidence rule: no quote, no credit
        out[h] = {"score": score, "quote": quote}
    return out


def audit_once(rater_key, doc_text):
    spec = dict(common.RATERS[rater_key])
    prompt = build_prompt(doc_text)
    for attempt in range(2):
        text, _ = common.call_model(spec, prompt, max_tokens=2500, temperature=0.0)
        parsed = parse_audit(text)
        if parsed:
            return parsed
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True, choices=["anthropic", "openai", "google"])
    ap.add_argument("--file", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    common.load_keys()
    if not os.path.exists(args.file):
        sys.exit("document file missing: " + args.file)
    doc_text = open(args.file).read()
    doc_hash = common.sha256_file(args.file)
    print("auditing {} ({} chars, sha256 {}...)".format(args.doc, len(doc_text), doc_hash[:12]))

    ra = audit_once("rater_a", doc_text)
    rb = audit_once("rater_b", doc_text)
    if not ra or not rb:
        sys.exit("a rater failed to return parseable scores; rerun")

    result = {}
    used_third = []
    rc = None
    for h in common.HOUSES:
        a, b = ra[h]["score"], rb[h]["score"]
        if abs(a - b) > 0.25:
            if rc is None:
                rc = audit_once("rater_c", doc_text)
            if rc:
                trio = sorted([a, b, rc[h]["score"]])
                final = trio[1]
                used_third.append(h)
            else:
                final = (a + b) / 2.0
        else:
            final = (a + b) / 2.0
        result[h] = {
            "score": round(final, 3),
            "score_a": a, "score_b": b,
            "score_c": rc[h]["score"] if rc else None,
            "quote_a": ra[h]["quote"], "quote_b": rb[h]["quote"],
        }

    out_path = args.out or os.path.join(common.DATA, "scores", "constitutions.json")
    common.ensure_dir(os.path.dirname(out_path))
    merged = {}
    if os.path.exists(out_path):
        merged = json.load(open(out_path))
    merged[args.doc] = {"file": os.path.basename(args.file), "sha256": doc_hash,
                        "audited_at": common.now_iso(), "third_rater_domains": used_third,
                        "houses": result}
    with open(out_path, "w") as f:
        json.dump(merged, f, indent=1, ensure_ascii=False)

    print("{:<4} {:<12} {:>6} {:>6} {:>6}".format("h", "domain", "a", "b", "final"))
    for h in common.HOUSES:
        r = result[h]
        print("{:<4} {:<12} {:>6.2f} {:>6.2f} {:>6.2f}".format(
            h, common.HOUSE_NAMES[h], r["score_a"], r["score_b"], r["score"]))
    if used_third:
        print("third rater used for: " + ", ".join(used_third))
    print("wrote " + out_path)


if __name__ == "__main__":
    main()
