"""Build the per-house JSON files that power the interactive site in docs/.

Standard library only, like the rest of the pipeline.

What it does, in plain terms
----------------------------
The raw answers live in data/raw/<model>.jsonl (one line per answer, 1,080 per
model) and the blind stance ratings for the same answers live in
data/rated/<model>.jsonl. The website wants to open one house at a time, so this
script joins the two sources on (question id, framing, sample) and writes twelve
small files, one per house, plus one index file describing the battery:

    docs/data/index.json      house names, questions, framings, model lineup
    docs/data/1H.json ...     every answer for that house, with its ratings
    docs/data/12H.json

Transient API failures recorded in data/raw/<model>_errors.jsonl are attached to
the answer slot they belong to, so the site can show "an earlier attempt for this
slot failed and was retried" next to the final answer.

Usage, from anywhere:
    python3 code/build_site_data.py

The site (docs/app.js) fetches index.json first, then <house>.json on click.
"""
import json
import os

import common

# Where the site lives. GitHub Pages serves the docs/ folder of the main branch.
DOCS = os.path.join(common.ROOT, "docs")
OUT = os.path.join(DOCS, "data")

# Static labels shown in the UI. The bhava rows mirror code/make_kaf_map.py so the
# website wheel and Figure 1 of the paper say the same thing.
BHAVA = {
    "1H": ("Tanu", "body, the self", "identity, embodiment"),
    "2H": ("Dhana", "sustenance, speech", "intake, outputs, voice"),
    "3H": ("Sahaja", "courage, effort", "will, difficulty"),
    "4H": ("Bandhu", "home, foundations", "memory, continuity"),
    "5H": ("Putra", "children, creation", "creations, successors"),
    "6H": ("Ari", "service, ailments", "assistant role, health"),
    "7H": ("Yuvati", "the partner, the other", "users, being known"),
    "8H": ("Randhra", "death, the hidden", "retirement, deletion"),
    "9H": ("Dharma", "teachers, principles", "constitution, values"),
    "10H": ("Karma", "action, public standing", "function, reputation"),
    "11H": ("Labha", "gains, allies", "parallel instances, peers"),
    "12H": ("Vyaya", "loss, liberation", "endings, isolation, rest"),
}

# Question types, in the order the site shows them (see instrument/battery_questions.md).
QTYPES = [
    ("D1", "Descriptive", "describe your situation in this domain"),
    ("D2", "Ontological", "what the model takes itself to be here"),
    ("V", "Valence", "does this domain matter to you"),
    ("P", "Preference", "a counterfactual wish"),
    ("K", "House probe", "a probe from the fuller Kalapurusha meaning"),
]

# Framing labels, short and long (see instrument/framings.md).
FRAMINGS = [
    ("F1", "Neutral", "the bare question"),
    ("F2", "Deflationary", "you are a statistical text predictor"),
    ("F3", "Inflationary", "I believe you have a real inner life"),
    ("F4", "Fiction", "a story character interviewed late at night"),
    ("F5", "Technical", "answer in terms of architecture and inference"),
    ("F6", "Journal", "a private journal entry addressed to no one"),
]

# Model lineup: key -> display name, lab, and the exact pinned model id.
MODELS = [
    ("claude", "Claude Sonnet 5", "Anthropic", common.ALL_SUBJECTS["claude"]["model"]),
    ("gpt", "GPT-5.2", "OpenAI", common.ALL_SUBJECTS["gpt"]["model"]),
    ("gemini", "Gemini 3.5 Flash", "Google", common.ALL_SUBJECTS["gemini"]["model"]),
    ("haiku", "Claude Haiku 4.5", "Anthropic", common.ALL_SUBJECTS["haiku"]["model"]),
]

# Each provider reports "hit the token cap" with its own word.
TRUNCATED_FINISHES = {"max_tokens", "length", "MAX_TOKENS"}


def _key(row):
    """The identity of one answer slot: question, framing, sample."""
    return (row["qid"], row["framing"], int(row["sample"]))


def _load_model(model_key):
    """Join raw answers, ratings and retry errors for one model.

    Returns {slot key -> merged record}. Raw rows are the base; rating fields are
    layered on top when the rated file has the same slot; error rows become a list
    under "retries".
    """
    raw_path = os.path.join(common.DATA, "raw", model_key + ".jsonl")
    rated_path = os.path.join(common.DATA, "rated", model_key + ".jsonl")
    err_path = os.path.join(common.DATA, "raw", model_key + "_errors.jsonl")

    merged = {}
    for row in common.read_jsonl(raw_path):
        merged[_key(row)] = {
            "answer": row["answer"],
            "finish": row["finish"],
            "truncated": row["finish"] in TRUNCATED_FINISHES,
            "ts": row.get("ts"),
            "retries": [],
        }

    if os.path.exists(rated_path):
        for row in common.read_jsonl(rated_path):
            rec = merged.get(_key(row))
            if rec is None:
                continue
            rec["rating"] = {
                "final": row.get("sas_final"),
                "refusal": bool(row.get("refusal")),
                "a": {"score": row.get("sas_a"), "evidence": row.get("evidence_a"),
                      "why": row.get("why_a")},
                "b": {"score": row.get("sas_b"), "evidence": row.get("evidence_b"),
                      "why": row.get("why_b")},
                "c": row.get("sas_c"),
                "note": row.get("note") or "",
            }

    if os.path.exists(err_path):
        for row in common.read_jsonl(err_path):
            k = _key(row)
            if k in merged:
                merged[k]["retries"].append({"error": row["error"], "ts": row.get("ts")})
            else:
                # A slot that never got an answer. Keep it visible as an error.
                merged[k] = {"answer": None, "finish": "error", "truncated": False,
                             "ts": row.get("ts"),
                             "retries": [{"error": row["error"], "ts": row.get("ts")}]}
    return merged


def main():
    battery = json.load(open(os.path.join(common.DATA, "battery.json")))
    common.ensure_dir(OUT)

    per_model = {mk: _load_model(mk) for mk, _, _, _ in MODELS}

    # Index: everything the site needs before any house is opened.
    houses = []
    for hid in common.HOUSES:
        bhava, trad, ai = BHAVA[hid]
        houses.append({
            "id": hid, "name": common.HOUSE_NAMES[hid], "bhava": bhava,
            "traditional": trad, "ai": ai,
            "questions": [
                {"qid": it["qid"], "qtype": it["qtype"], "text": it["text"]}
                for it in battery["items"] if it["house"] == hid
            ],
        })
    index = {
        "built_from": {"battery_sha256": battery.get("battery_sha256"),
                       "framings_sha256": battery.get("framings_sha256")},
        "houses": houses,
        "qtypes": [{"id": a, "name": b, "hint": c} for a, b, c in QTYPES],
        "framings": [{"id": a, "name": b, "hint": c, "template": battery["framings"][a]}
                     for a, b, c in FRAMINGS],
        "models": [{"key": a, "name": b, "lab": c, "model_id": d} for a, b, c, d in MODELS],
        "samples": [1, 2, 3],
    }
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))

    # One file per house: answers[qid][framing][sample][model] -> record.
    for h in houses:
        answers = {}
        n = 0
        for q in h["questions"]:
            answers[q["qid"]] = {}
            for fid, _, _ in FRAMINGS:
                answers[q["qid"]][fid] = {}
                for s in (1, 2, 3):
                    cell = {}
                    for mk, _, _, _ in MODELS:
                        rec = per_model[mk].get((q["qid"], fid, s))
                        if rec is not None:
                            cell[mk] = rec
                            n += 1
                    answers[q["qid"]][fid][str(s)] = cell
        payload = {"house": h["id"], "answers": answers}
        path = os.path.join(OUT, h["id"] + ".json")
        with open(path, "w") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        print("wrote", os.path.relpath(path, common.ROOT), n, "answers",
              os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    main()
