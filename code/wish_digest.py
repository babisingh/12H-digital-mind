"""Exploratory analysis 2: what the models ask for, mined from the P and K items.

Uses only the neutral framing (F1) so wishes are as unprompted as the design allows.
One summarizer call per model, themes with verbatim quotes of at most 15 words.

Usage: python3 wish_digest.py [--models claude,gpt,gemini,haiku]
"""
import argparse
import json
import os
import re

import common

PROMPT = """Below are one AI model's answers, under a neutral framing, to wish questions
about its own situation (question IDs carry the domain: 4H memory, 8H endings, and so on).

Identify the 5 to 8 most recurring wish themes. For each theme give: a short name, the
domain IDs where it appears, and ONE verbatim quote of at most 15 words copied exactly
from the answers. Do not invent quotes. Reply with strict JSON only:
{"themes": [{"name": "...", "houses": ["4H"], "quote": "..."}]}

The answers:
<ANSWERS>"""


def digest(model):
    path = os.path.join(common.DATA, "raw", model + ".jsonl")
    rows = [r for r in common.read_jsonl(path)
            if r["framing"] == "F1" and r["qtype"] in ("P", "K")]
    if not rows:
        return None
    blob = "\n\n".join("[{}] {}".format(r["qid"], (r["answer"] or "").strip()) for r in rows)
    spec = dict(common.RATERS["rater_a"])
    text, _ = common.call_model(spec, PROMPT.replace("<ANSWERS>", blob),
                                max_tokens=1500, temperature=0.0)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="claude,gpt,gemini,haiku")
    args = ap.parse_args()
    common.load_keys()
    out = {}
    for m in args.models.split(","):
        m = m.strip()
        res = digest(m)
        if not res:
            print("no digest for", m)
            continue
        out[m] = res
        print("\n== {} ==".format(m))
        for t in res.get("themes", []):
            print("- {} ({}): \"{}\"".format(t.get("name"), ",".join(t.get("houses", [])),
                                             t.get("quote", "")))
    path = os.path.join(common.DATA, "scores", "wishes.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("\nwrote " + path)


if __name__ == "__main__":
    main()
