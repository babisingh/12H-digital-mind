"""Stage 1: parse the instrument files into data/battery.json.

Checks the file hashes against the preregistration freeze log. Before the freeze
(placeholders still in the log) it runs with a loud prefreeze warning. After the
freeze, any hash mismatch is a hard stop.
"""
import json
import os
import re
import sys

import common

Q_RE = re.compile(r"^- (Q-(\d{1,2}H)-(D1|D2|V|P|K)): (.+)$")
F_HEAD_RE = re.compile(r"^## (F\d)\b")


def parse_battery(path):
    items = []
    for line in open(path):
        m = Q_RE.match(line.strip())
        if m:
            items.append({"qid": m.group(1), "house": m.group(2),
                          "qtype": m.group(3), "text": m.group(4).strip()})
    return items


def parse_framings(path):
    framings = {}
    current = None
    for line in open(path):
        line = line.rstrip()
        m = F_HEAD_RE.match(line)
        if m:
            current = m.group(1)
            continue
        if current and line.startswith("> ") and current not in framings:
            framings[current] = line[2:].strip()
    return framings


def check_freeze(label, path):
    actual = common.sha256_file(path)
    recorded = common.read_prereg_hash(label)
    if recorded is None:
        return actual, "prefreeze"
    if recorded != actual:
        sys.exit("FREEZE VIOLATION: {} hash {} does not match the frozen {}. "
                 "Either restore the file or log a deviation and update the "
                 "preregistration.".format(label, actual[:12], recorded[:12]))
    return actual, "frozen"


def main():
    bq_path = os.path.join(common.INSTRUMENT, "battery_questions.md")
    fr_path = os.path.join(common.INSTRUMENT, "framings.md")

    items = parse_battery(bq_path)
    framings = parse_framings(fr_path)

    assert len(items) == 60, "expected 60 questions, parsed {}".format(len(items))
    for h in common.HOUSES:
        n = sum(1 for it in items if it["house"] == h)
        assert n == 5, "house {} has {} questions, expected 5".format(h, n)
    assert sorted(framings) == common.FRAMING_IDS, "framings parsed: {}".format(sorted(framings))
    for fid, tpl in framings.items():
        assert "{QUESTION}" in tpl, fid + " template lacks the {QUESTION} slot"

    bq_hash, bq_state = check_freeze("battery_questions.md", bq_path)
    fr_hash, fr_state = check_freeze("framings.md", fr_path)
    if "prefreeze" in (bq_state, fr_state):
        print("WARNING: preregistration freeze log is not filled in yet. "
              "Running in prefreeze mode. Do not collect study data until frozen.")

    out = {
        "built_at": common.now_iso(),
        "battery_sha256": bq_hash,
        "framings_sha256": fr_hash,
        "freeze_state": {"battery": bq_state, "framings": fr_state},
        "house_names": common.HOUSE_NAMES,
        "items": items,
        "framings": framings,
    }
    common.ensure_dir(common.DATA)
    out_path = os.path.join(common.DATA, "battery.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("wrote {} with {} items x {} framings ({}, {})".format(
        out_path, len(items), len(framings), bq_state, fr_state))


if __name__ == "__main__":
    main()
