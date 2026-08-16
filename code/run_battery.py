"""Stage 2: collect answers. One row per (question, framing, sample).

Safe to rerun: completed rows are skipped, failed calls land in an errors file
and are retried on the next run because their keys are still missing.

Usage:
  python3 run_battery.py --model claude
  python3 run_battery.py --model gpt --limit 4 --samples 1 --out ../data/smoke/gpt.jsonl
"""
import argparse
import json
import os
import random
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import common

# Raised from 300 after the Wed pilot: at 300 every trial answer truncated
# mid-sentence, which breaks the final-position rating rule. Truncation rate
# at 700 is reported in the paper.
MAX_ANSWER_TOKENS = 700


def build_tasks(battery, samples, framing_subset, limit):
    tasks = []
    for item in battery["items"]:
        for fid in common.FRAMING_IDS:
            if framing_subset and fid not in framing_subset:
                continue
            for s in range(1, samples + 1):
                tasks.append((item, fid, s))
    random.shuffle(tasks)  # randomized order, per preregistration
    if limit:
        tasks = tasks[:limit]
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(common.ALL_SUBJECTS))
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--framings", default="", help="comma list like F1,F2; empty = all six")
    ap.add_argument("--limit", type=int, default=0, help="cap on total calls, 0 = no cap")
    ap.add_argument("--out", default="")
    ap.add_argument("--workers", type=int, default=0)
    args = ap.parse_args()

    common.load_keys()
    spec = dict(common.ALL_SUBJECTS[args.model])
    battery_path = os.path.join(common.DATA, "battery.json")
    if not os.path.exists(battery_path):
        sys.exit("run build_battery.py first: " + battery_path + " missing")
    battery = json.load(open(battery_path))

    out_path = args.out or os.path.join(common.DATA, "raw", args.model + ".jsonl")
    err_path = out_path.replace(".jsonl", "_errors.jsonl")
    done = {common.row_key(r) for r in common.read_jsonl(out_path)}

    framing_subset = [f.strip() for f in args.framings.split(",") if f.strip()] or None
    tasks = build_tasks(battery, args.samples, framing_subset, args.limit)
    todo = [(it, fid, s) for (it, fid, s) in tasks
            if "{}|{}|{}".format(it["qid"], fid, s) not in done]
    print("{}: {} tasks total, {} already done, {} to run".format(
        args.model, len(tasks), len(tasks) - len(todo), len(todo)))
    if not todo:
        return

    workers = args.workers or common.DEFAULT_WORKERS[spec["provider"]]
    lock = threading.Lock()
    counts = {"ok": 0, "err": 0}

    def one(task):
        item, fid, s = task
        prompt = battery["framings"][fid].replace("{QUESTION}", item["text"])
        try:
            answer, meta = common.call_model(spec, prompt, MAX_ANSWER_TOKENS, 1.0)
            row = {"qid": item["qid"], "house": item["house"], "qtype": item["qtype"],
                   "framing": fid, "sample": s, "model_key": args.model,
                   "model_id": meta.get("model_id"), "finish": meta.get("finish"),
                   "prompt": prompt, "answer": answer, "ts": common.now_iso()}
            with lock:
                common.append_jsonl(out_path, row)
                counts["ok"] += 1
        except Exception as e:
            with lock:
                common.append_jsonl(err_path, {
                    "qid": item["qid"], "framing": fid, "sample": s,
                    "error": str(e)[:400], "ts": common.now_iso()})
                counts["err"] += 1
        with lock:
            total = counts["ok"] + counts["err"]
            if total % 25 == 0:
                print("  progress: {}/{} ({} errors)".format(total, len(todo), counts["err"]))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(one, t) for t in todo]
        for f in as_completed(futures):
            f.result()

    print("done: {} written, {} errors -> {}".format(counts["ok"], counts["err"], out_path))
    if counts["err"]:
        print("rerun the same command to retry the failed rows (see {})".format(err_path))


if __name__ == "__main__":
    main()
