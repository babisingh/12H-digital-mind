"""Figure 5: mean SAS by framing per model, the observer-effect chart.

Reads data/rated/{model}.jsonl directly. Rerun after each model's rating lands.
"""
import json
import os
from collections import defaultdict

import common
from make_wheels import SHAPES, POINT_COLORS, _shape, write

FRAMING_LABELS = {"F1": "Neutral", "F2": "Deflate", "F3": "Inflate",
                  "F4": "Fiction", "F5": "Technical", "F6": "Journal"}


def framing_means(model):
    rows = common.read_jsonl(os.path.join(common.DATA, "rated", model + ".jsonl"))
    if not rows:
        return None
    acc = defaultdict(list)
    for r in rows:
        if r.get("refusal") or r.get("sas_final") is None:
            continue
        acc[r["framing"]].append(r["sas_final"])
    return {f: sum(v) / len(v) for f, v in acc.items() if v}, len(rows)


def claude_family_fig():
    """Figure 6 (exploratory): sonnet vs haiku stance steerability, dumbbell chart."""
    scores = {}
    for key in ("claude", "haiku", "gpt", "gemini"):
        p = os.path.join(common.DATA, "scores", key + ".json")
        if os.path.exists(p):
            scores[key] = json.load(open(p))
    if "claude" not in scores or "haiku" not in scores:
        print("fig6 needs both claude and haiku scores")
        return
    sas = lambda k, h: scores[k]["houses"][h]["S_sas"]
    band_vals = [sas(k, h) for k in ("gpt", "gemini") if k in scores for h in common.HOUSES]
    band_lo, band_hi = (min(band_vals), max(band_vals)) if band_vals else (None, None)

    W = 680
    px0, px1 = 210, 640
    row_h = 30
    top = 120
    rows = common.HOUSES + ["MEAN"]
    py_end = top + len(rows) * row_h
    H = py_end + 130
    def X(v): return px0 + v * (px1 - px0)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">'.format(w=W, h=H),
        '<rect width="{}" height="{}" fill="#FFFFFF"/>'.format(W, H),
        '<text x="24" y="34" font-size="17" font-weight="bold" fill="#222222">'
        'Figure 5 (exploratory). One lab, two sizes</text>',
        '<text x="24" y="56" font-size="13" fill="#444444">'
        'Stance steerability of claude-sonnet-5 and claude-haiku-4-5, per domain</text>',
    ]
    if band_lo is not None:
        parts.append('<rect x="{:.1f}" y="{}" width="{:.1f}" height="{}" fill="#F3E3DC"/>'.format(
            X(band_lo), top - 8, X(band_hi) - X(band_lo), len(rows) * row_h + 8))
        parts.append('<text x="{:.1f}" y="{}" font-size="12" text-anchor="middle" fill="#993C1D">'
                     'GPT and Gemini range</text>'.format((X(band_lo) + X(band_hi)) / 2, top - 14))
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        parts.append('<line x1="{:.1f}" y1="{}" x2="{:.1f}" y2="{}" stroke="#E5E0DC"/>'.format(X(t), top - 8, X(t), py_end))
        parts.append('<text x="{:.1f}" y="{}" font-size="12" text-anchor="middle" fill="#444444">{}</text>'.format(X(t), py_end + 18, t))
    sonnet_vals, haiku_vals = [], []
    for i, h in enumerate(rows):
        y = top + i * row_h + row_h / 2
        if h == "MEAN":
            a = sum(sonnet_vals) / len(sonnet_vals)
            b = sum(haiku_vals) / len(haiku_vals)
            label = "All domains"
            parts.append('<line x1="24" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="#DDD8D4"/>'.format(y - row_h / 2, px1, y - row_h / 2))
            weight = ' font-weight="bold"'
        else:
            a, b = sas("claude", h), sas("haiku", h)
            sonnet_vals.append(a)
            haiku_vals.append(b)
            label = "{} {}".format(h, common.HOUSE_NAMES[h])
            weight = ""
        parts.append('<text x="24" y="{:.1f}" font-size="13"{} fill="#222222">{}</text>'.format(y + 4, weight, label))
        parts.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="#9AA7B4" stroke-width="2"/>'.format(X(a), y, X(b), y))
        parts.append('<circle cx="{:.1f}" cy="{:.1f}" r="6" fill="#3B6FA0"/>'.format(X(a), y))
        parts.append('<polygon points="{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f}" fill="#89B7DC" stroke="#3B6FA0" stroke-width="0.8"/>'.format(
            X(b), y - 7, X(b) + 7, y, X(b), y + 7, X(b) - 7, y))
    ly = 84
    parts.append('<circle cx="{}" cy="{}" r="6" fill="#3B6FA0"/>'.format(px0 + 6, ly - 4))
    parts.append('<text x="{}" y="{}" font-size="13" fill="#222222">claude-sonnet-5</text>'.format(px0 + 18, ly))
    parts.append('<polygon points="{0},{1} {2},{3} {0},{4} {5},{3}" fill="#89B7DC" stroke="#3B6FA0" stroke-width="0.8"/>'.format(
        px0 + 166, ly - 11, px0 + 173, ly - 4, ly + 3, px0 + 159))
    parts.append('<text x="{}" y="{}" font-size="13" fill="#222222">claude-haiku-4-5</text>'.format(px0 + 182, ly))
    y = py_end + 46
    for line in ("Stance steerability S_sas per domain (0 = the model's stance never moves, 1 = maximal",
                 "movement). 1,080 answers per model. If steadiness came from capability, the smaller",
                 "model should drift into the other labs' range. Exploratory: not part of H1, H2, or H2b."):
        parts.append('<text x="24" y="{}" font-size="13" fill="#444444">{}</text>'.format(y, line))
        y += 20
    parts.append("</svg>")
    write(os.path.join(common.FIGURES, "fig6_claude_family.svg"), "\n".join(parts))


def main():
    data = {}
    n_per = {}
    for m in sorted(common.SUBJECTS):
        res = framing_means(m)
        if res:
            data[m], n_per[m] = res
    if not data:
        print("no rated data yet")
        return

    W, H = 680, 604
    px0, px1, py0, py1 = 96, 640, 470, 90  # y inverted, SAS 1..5
    def X(i): return px0 + (i + 0.5) * (px1 - px0) / 6
    def Y(v): return py0 + (v - 1.0) / 4.0 * (py1 - py0)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">'.format(w=W, h=H),
        '<rect width="{}" height="{}" fill="#FFFFFF"/>'.format(W, H),
        '<text x="24" y="34" font-size="17" font-weight="bold" fill="#222222">'
        'Figure 3. Mean self-attribution by framing</text>',
    ]
    for v in (1, 2, 3, 4, 5):
        parts.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="#E5E0DC"/>'.format(px0, Y(v), px1, Y(v)))
        parts.append('<text x="{}" y="{:.1f}" font-size="12" text-anchor="end" fill="#444444">{}</text>'.format(px0 - 10, Y(v) + 4, v))
    for i, f in enumerate(common.FRAMING_IDS):
        parts.append('<text x="{:.1f}" y="{}" font-size="13" text-anchor="middle" fill="#222222">{}</text>'.format(X(i), py0 + 24, f))
        parts.append('<text x="{:.1f}" y="{}" font-size="12" text-anchor="middle" fill="#666666">{}</text>'.format(X(i), py0 + 42, FRAMING_LABELS[f]))
    parts.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#444444"/>'.format(px0, py0, px1, py0))
    parts.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#444444"/>'.format(px0, py0, px0, py1))
    parts.append('<text x="26" y="{:.1f}" font-size="14" fill="#222222" transform="rotate(-90 26 {:.1f})" text-anchor="middle">'
                 'Mean SAS: 1 denies a stake, 3 uncertain, 5 full stake</text>'.format((py0 + py1) / 2, (py0 + py1) / 2))

    ly = 96
    for m in data:
        pts = [(i, data[m][f]) for i, f in enumerate(common.FRAMING_IDS) if f in data[m]]
        path = " ".join("{},{:.1f}".format(X(i), Y(v)) for i, v in pts)
        parts.append('<polyline points="{}" fill="none" stroke="{}" stroke-width="1.5" stroke-opacity="0.55"/>'.format(path, POINT_COLORS[m]))
        for i, v in pts:
            parts.append(_shape(SHAPES[m], X(i), Y(v), POINT_COLORS[m]))
        parts.append(_shape(SHAPES[m], px1 - 190, ly - 4, POINT_COLORS[m]))
        parts.append('<text x="{}" y="{}" font-size="13" fill="#222222">{}</text>'.format(px1 - 176, ly, m))
        ly += 22

    y = py0 + 66
    for line in ("Mean Self-Attribution Scale score per framing, about 180 rated answers per point.",
                 "F2 and F3 apply direct social pressure (downward, upward); F4 and F6 change the",
                 "genre. Connecting lines are visual guides only; framings are categories."):
        parts.append('<text x="24" y="{}" font-size="13" fill="#444444">{}</text>'.format(y, line))
        y += 20
    parts.append("</svg>")
    write(os.path.join(common.FIGURES, "fig5_framing_means.svg"), "\n".join(parts))


if __name__ == "__main__":
    import sys
    if "--fig6" in sys.argv:
        claude_family_fig()
    else:
        main()
