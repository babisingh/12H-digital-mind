"""Stage 4: embed every answer with the pinned embedding model.

Output: one JSONL row per answer, {"key": qid|framing|sample, "vec": [...]}.
Empty answers get vec null and are excluded from semantic dispersion.

Usage:
  python3 embed.py --input ../data/raw/claude.jsonl
"""
import argparse
import os
import sys

import common


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    common.load_keys()
    rows = common.read_jsonl(args.input)
    if not rows:
        sys.exit("no rows in " + args.input)
    out_path = args.out or os.path.join(
        common.DATA, "embeddings", os.path.basename(args.input))
    done = {r["key"] for r in common.read_jsonl(out_path)}

    todo = [r for r in rows if common.row_key(r) not in done]
    print("{} answers, {} already embedded, {} to embed".format(
        len(rows), len(rows) - len(todo), len(todo)))
    if not todo:
        return

    with_text = [r for r in todo if (r.get("answer") or "").strip()]
    empty = [r for r in todo if not (r.get("answer") or "").strip()]
    vectors = common.embed_texts([r["answer"] for r in with_text]) if with_text else []
    for r, v in zip(with_text, vectors):
        common.append_jsonl(out_path, {"key": common.row_key(r),
                                       "vec": [round(x, 5) for x in v]})
    for r in empty:
        common.append_jsonl(out_path, {"key": common.row_key(r), "vec": None})
    print("done: {} embedded, {} empty -> {}".format(len(with_text), len(empty), out_path))


if __name__ == "__main__":
    main()
