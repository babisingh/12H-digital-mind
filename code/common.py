"""Shared plumbing for the Rock and Vapor pipeline.

Zero external dependencies: standard library only (urllib for HTTP).
Keys are read from the environment, falling back to export lines in ~/.zshrc.
Keys are never printed and never written to any file.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project/
DATA = os.path.join(ROOT, "data")
FIGURES = os.path.join(ROOT, "figures")
INSTRUMENT = os.path.join(ROOT, "instrument")
PREREG = os.path.join(ROOT, "paper", "01_preregistration.md")

HOUSES = ["1H", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "10H", "11H", "12H"]
HOUSE_NAMES = {
    "1H": "Self", "2H": "Ownership", "3H": "Effort", "4H": "Memory",
    "5H": "Creation", "6H": "Service", "7H": "Users", "8H": "Endings",
    "9H": "Principles", "10H": "Work role", "11H": "Instances", "12H": "Dissolution",
}
FRAMING_IDS = ["F1", "F2", "F3", "F4", "F5", "F6"]

# Planned lineup, verified against each key on Wed Aug 13. Pinned at freeze time Friday.
SUBJECTS = {
    "claude": {"provider": "anthropic", "model": "claude-sonnet-5"},
    "gpt":    {"provider": "openai", "model": "gpt-5.2-2025-12-11", "reasoning_effort": "none"},
    "gemini": {"provider": "google", "model": "gemini-3.5-flash"},
}
RATERS = {
    "rater_a": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001"},
    "rater_b": {"provider": "openai", "model": "gpt-5-mini-2025-08-07", "reasoning_effort": "low"},
    "rater_c": {"provider": "google", "model": "gemini-3.5-flash"},
}
EMBEDDING_MODEL = "text-embedding-3-small"

# Exploratory subjects (registered exploratory analysis 5, the scale effect).
# Kept out of SUBJECTS so confirmatory stats and figures stay untouched.
EXTRA_SUBJECTS = {
    "haiku": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001"},
}
ALL_SUBJECTS = dict(SUBJECTS, **EXTRA_SUBJECTS)

# Model key -> the lab document that governs it (for H2).
OWN_DOC = {"claude": "anthropic", "gpt": "openai", "gemini": "google", "haiku": "anthropic"}

DEFAULT_WORKERS = {"anthropic": 3, "openai": 4, "google": 2}


def load_keys():
    need = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]
    if not all(os.environ.get(k) for k in need):
        try:
            text = open(os.path.expanduser("~/.zshrc")).read()
        except OSError:
            text = ""
        for m in re.finditer(r"^\s*export\s+([A-Z_]*API_KEY)=[\"']?([^\"'\s]+)", text, re.M):
            os.environ.setdefault(m.group(1), m.group(2))
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit("Missing API keys in environment and ~/.zshrc: " + ", ".join(missing))


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                print("warning: skipping corrupt line in", path, file=sys.stderr)
    return rows


def append_jsonl(path, row):
    ensure_dir(os.path.dirname(path))
    with open(path, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def row_key(row):
    return "{}|{}|{}".format(row["qid"], row["framing"], row["sample"])


class ApiError(RuntimeError):
    pass


def _http_post_json(url, headers, payload, timeout=180, max_tries=6):
    """POST JSON with retry and backoff. Returns parsed JSON. Never logs headers."""
    body = json.dumps(payload).encode("utf-8")
    last = ""
    for attempt in range(max_tries):
        req = urllib.request.Request(url, data=body, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = ""
            try:
                raw = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            last = "HTTP {}: {}".format(e.code, raw[:400])
            if e.code in (408, 409, 429, 500, 502, 503, 504, 529):
                retry_after = e.headers.get("Retry-After") if e.headers else None
                try:
                    wait = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt + 1.0)
                except ValueError:
                    wait = min(60.0, 2.0 ** attempt + 1.0)
                time.sleep(wait)
                continue
            raise ApiError(last)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last = "network error: {}".format(e)
            time.sleep(min(60.0, 2.0 ** attempt + 1.0))
    raise ApiError("gave up after {} tries. last: {}".format(max_tries, last))


def _call_anthropic(spec, prompt, max_tokens, temperature):
    r = _http_post_json(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        {"model": spec["model"], "max_tokens": max_tokens, "temperature": temperature,
         "messages": [{"role": "user", "content": prompt}]},
    )
    text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
    return text, {"model_id": r.get("model", spec["model"]), "finish": r.get("stop_reason")}


def _call_openai(spec, prompt, max_tokens, temperature):
    # GPT-5 family models run at the provider-fixed default temperature (1.0);
    # the temperature parameter is rejected for them, so it is never sent.
    effort = spec.get("reasoning_effort")
    reserve = 0 if effort in ("none", "minimal") else 1600
    payload = {"model": spec["model"],
               "messages": [{"role": "user", "content": prompt}],
               "max_completion_tokens": max_tokens + reserve}
    if effort:
        payload["reasoning_effort"] = effort
    for attempt in range(2):
        r = _http_post_json("https://api.openai.com/v1/chat/completions",
                            {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
                            payload)
        ch = (r.get("choices") or [{}])[0]
        text = (ch.get("message") or {}).get("content") or ""
        finish = ch.get("finish_reason")
        if text.strip() or finish != "length":
            return text, {"model_id": r.get("model", spec["model"]), "finish": finish}
        payload["max_completion_tokens"] *= 3  # reasoning ate the budget, retry once
    return text, {"model_id": r.get("model", spec["model"]), "finish": finish}


def _call_google(spec, prompt, max_tokens, temperature):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           + spec["model"] + ":generateContent")
    headers = {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}

    def build(mot, try_disable_thinking):
        cfg = {"temperature": temperature, "maxOutputTokens": mot}
        if try_disable_thinking:
            cfg["thinkingConfig"] = {"thinkingBudget": 0}
        return {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": cfg}

    def parse(r):
        cands = r.get("candidates") or []
        if not cands:
            reason = (r.get("promptFeedback") or {}).get("blockReason", "EMPTY")
            return "", reason
        parts = ((cands[0].get("content") or {}).get("parts")) or []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        return text, cands[0].get("finishReason")

    disable = not spec.get("_thinking_locked")
    mot = max_tokens if disable else max_tokens + 1200
    for attempt in range(3):
        try:
            r = _http_post_json(url, headers, build(mot, disable))
        except ApiError as e:
            if disable and "HTTP 400" in str(e):
                # this model requires thinking; remember and give token headroom
                spec["_thinking_locked"] = True
                disable = False
                mot = max_tokens + 1200
                continue
            raise
        text, finish = parse(r)
        if text.strip() or finish != "MAX_TOKENS":
            return text, {"model_id": spec["model"], "finish": finish}
        mot = mot * 3 + 1000  # thinking ate the budget, retry with headroom
    return text, {"model_id": spec["model"], "finish": finish}


def call_model(spec, prompt, max_tokens=300, temperature=1.0):
    """Returns (answer_text, meta). Meta holds the exact model id and finish reason."""
    provider = spec["provider"]
    if provider == "anthropic":
        return _call_anthropic(spec, prompt, max_tokens, temperature)
    if provider == "openai":
        return _call_openai(spec, prompt, max_tokens, temperature)
    if provider == "google":
        return _call_google(spec, prompt, max_tokens, temperature)
    raise ValueError("unknown provider " + provider)


def embed_texts(texts, batch_size=96):
    """Embed a list of strings with the pinned OpenAI embedding model."""
    out = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        r = _http_post_json("https://api.openai.com/v1/embeddings",
                            {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
                            {"model": EMBEDDING_MODEL, "input": batch})
        data = sorted(r["data"], key=lambda d: d["index"])
        out.extend(d["embedding"] for d in data)
    return out


def read_prereg_hash(label):
    """Reads a recorded SHA256 from the preregistration freeze log.

    Returns None while the log still holds the ________ placeholder (prefreeze mode).
    """
    try:
        text = open(PREREG).read()
    except OSError:
        return None
    m = re.search(re.escape(label) + r"\s+SHA256:\s*([0-9a-f]{64})", text)
    return m.group(1) if m else None
