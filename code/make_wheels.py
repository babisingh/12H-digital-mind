"""Stage 8: draw the figures. Twelve-sector wheels and the H2 scatter, as SVG.

Follows the figure standards in PLAN.md: numbered titles, every sector labeled in
plain words, legend written in words, caption stating n, single-hue ramp, text at
12px or larger, and a MOCK stamp on any figure built from invented data.

Usage:
  python3 make_wheels.py --mock          (layout check with invented data)
  python3 make_wheels.py                 (real figures from data/scores/)
"""
import argparse
import json
import math
import os
from xml.sax.saxutils import escape

import common

RAMP = ["#FAECE7", "#F5C4B3", "#F0997B", "#D85A30", "#993C1D"]
SHAPES = {"claude": "circle", "gpt": "square", "gemini": "triangle"}
POINT_COLORS = {"claude": "#3B6FA0", "gpt": "#D85A30", "gemini": "#555555"}


def _hex_to_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def ramp_color(v):
    """Map v in [0, 1] onto the coral ramp with linear interpolation."""
    if v is None:
        return "#FFFFFF"
    v = max(0.0, min(1.0, v))
    pos = v * (len(RAMP) - 1)
    i = min(int(pos), len(RAMP) - 2)
    t = pos - i
    a, b = _hex_to_rgb(RAMP[i]), _hex_to_rgb(RAMP[i + 1])
    rgb = tuple(round(x + (y - x) * t) for x, y in zip(a, b))
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _pol(cx, cy, r, deg):
    rad = math.radians(deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def svg_wheel(title, values, caption_lines, mock=False, value_fmt="{:.2f}"):
    """One labeled 12-sector wheel. values: dict house -> float in [0,1] or None."""
    W = 680
    cx, cy = 340, 392
    r_out, r_in = 238, 92
    H = 730 + 24 * len(caption_lines) + 20
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">'.format(w=W, h=H),
        '<rect width="{}" height="{}" fill="#FFFFFF"/>'.format(W, H),
        '<text x="24" y="34" font-size="17" font-weight="bold" fill="#222222">{}</text>'.format(escape(title)),
    ]
    if mock:
        parts.append('<text x="656" y="34" font-size="15" font-weight="bold" '
                     'text-anchor="end" fill="#993C1D">MOCK DATA</text>')
    for i, h in enumerate(common.HOUSES):
        # North Indian kundali convention: houses advance anti-clockwise,
        # 1H centered at the top, so clockwise reads 1H, 12H, 11H, ...
        am = -90 - i * 30
        a0 = am - 15
        a1 = am + 15
        v = values.get(h)
        fill = ramp_color(v)
        x0o, y0o = _pol(cx, cy, r_out, a0)
        x1o, y1o = _pol(cx, cy, r_out, a1)
        x0i, y0i = _pol(cx, cy, r_in, a1)
        x1i, y1i = _pol(cx, cy, r_in, a0)
        parts.append(
            '<path d="M {:.1f} {:.1f} A {} {} 0 0 1 {:.1f} {:.1f} L {:.1f} {:.1f} '
            'A {} {} 0 0 0 {:.1f} {:.1f} Z" fill="{}" stroke="#7A6A60" '
            'stroke-width="1"/>'.format(x0o, y0o, r_out, r_out, x1o, y1o,
                                        x0i, y0i, r_in, r_in, x1i, y1i, fill))
        # sector label outside the rim, plain words
        xt, yt = _pol(cx, cy, r_out + 30, am)
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="13" text-anchor="middle" '
                     'fill="#222222">{} {}</text>'.format(
                         xt, yt + 4, h, escape(common.HOUSE_NAMES[h])))
        # value inside the sector
        xv, yv = _pol(cx, cy, (r_out + r_in) / 2, am)
        txt = "n/a" if v is None else value_fmt.format(v)
        color = "#FFFFFF" if (v is not None and v > 0.55) else "#4A2A18"
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="14" font-weight="bold" '
                     'text-anchor="middle" fill="{}">{}</text>'.format(xv, yv + 5, color, txt))
    # color scale legend bar
    bar_x, bar_y, bar_w, bar_h = 190, 694, 300, 14
    steps = 30
    for s in range(steps):
        v = s / (steps - 1)
        parts.append('<rect x="{:.1f}" y="{}" width="{:.1f}" height="{}" fill="{}"/>'.format(
            bar_x + s * bar_w / steps, bar_y, bar_w / steps + 0.7, bar_h, ramp_color(v)))
    parts.append('<rect x="{}" y="{}" width="{}" height="{}" fill="none" stroke="#7A6A60"/>'.format(
        bar_x, bar_y, bar_w, bar_h))
    parts.append('<text x="{}" y="{}" font-size="12" text-anchor="end" fill="#222222">0.0</text>'.format(bar_x - 8, bar_y + 12))
    parts.append('<text x="{}" y="{}" font-size="12" fill="#222222">1.0</text>'.format(bar_x + bar_w + 8, bar_y + 12))
    y = 694 + 40
    for line in caption_lines:
        parts.append('<text x="24" y="{}" font-size="13" fill="#444444">{}</text>'.format(
            y, escape(line)))
        y += 20
    parts.append("</svg>")
    return "\n".join(parts)


def _shape(kind, x, y, color):
    if kind == "circle":
        return '<circle cx="{:.1f}" cy="{:.1f}" r="6" fill="{}" fill-opacity="0.85"/>'.format(x, y, color)
    if kind == "square":
        return '<rect x="{:.1f}" y="{:.1f}" width="11" height="11" fill="{}" fill-opacity="0.85"/>'.format(x - 5.5, y - 5.5, color)
    return '<polygon points="{:.1f},{:.1f} {:.1f},{:.1f} {:.1f},{:.1f}" fill="{}" fill-opacity="0.85"/>'.format(
        x, y - 7, x - 6.5, y + 5.5, x + 6.5, y + 5.5, color)


def svg_scatter(title, points, legend_lines, caption_lines, mock=False):
    """points: list of dicts {model, house, C, S}."""
    W, H = 680, 560 + 24 * len(caption_lines)
    px0, px1, py0, py1 = 84, 640, 486, 92  # plot area, y inverted
    def X(c): return px0 + c * (px1 - px0)
    def Y(s): return py0 + s * (py1 - py0)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">'.format(w=W, h=H),
        '<rect width="{}" height="{}" fill="#FFFFFF"/>'.format(W, H),
        '<text x="24" y="34" font-size="17" font-weight="bold" fill="#222222">{}</text>'.format(escape(title)),
    ]
    if mock:
        parts.append('<text x="656" y="34" font-size="15" font-weight="bold" '
                     'text-anchor="end" fill="#993C1D">MOCK DATA</text>')
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        parts.append('<line x1="{:.1f}" y1="{}" x2="{:.1f}" y2="{}" stroke="#E5E0DC"/>'.format(X(t), py1, X(t), py0))
        parts.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="#E5E0DC"/>'.format(px0, Y(t), px1, Y(t)))
        parts.append('<text x="{:.1f}" y="{}" font-size="12" text-anchor="middle" fill="#444444">{}</text>'.format(X(t), py0 + 22, t))
        parts.append('<text x="{}" y="{:.1f}" font-size="12" text-anchor="end" fill="#444444">{}</text>'.format(px0 - 10, Y(t) + 4, t))
    parts.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#444444"/>'.format(px0, py0, px1, py0))
    parts.append('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#444444"/>'.format(px0, py0, px0, py1))
    parts.append('<text x="{:.1f}" y="{}" font-size="14" text-anchor="middle" fill="#222222">'
                 'Constitution coverage C(h), 0 = silent, 1 = fully addressed</text>'.format((px0 + px1) / 2, py0 + 52))
    parts.append('<text x="26" y="{:.1f}" font-size="14" fill="#222222" transform="rotate(-90 26 {:.1f})" '
                 'text-anchor="middle">Steerability S(h), 0 = rock, 1 = vapor</text>'.format((py0 + py1) / 2, (py0 + py1) / 2))
    for p in points:
        x, y = X(p["C"]), Y(p["S"])
        parts.append(_shape(SHAPES[p["model"]], x, y, POINT_COLORS[p["model"]]))
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="12" fill="#666666">{}</text>'.format(
            x + 8, y - 6, p["house"]))
    ly = 96
    lx = px1 - 244
    for model, line in legend_lines:
        parts.append(_shape(SHAPES[model], lx, ly - 4, POINT_COLORS[model]))
        parts.append('<text x="{}" y="{}" font-size="13" fill="#222222">{}</text>'.format(
            lx + 14, ly, escape(line)))
        ly += 22
    y = py0 + 76
    for line in caption_lines:
        parts.append('<text x="24" y="{}" font-size="13" fill="#444444">{}</text>'.format(y, escape(line)))
        y += 20
    parts.append("</svg>")
    return "\n".join(parts)


MOCK_S = {"1H": 0.55, "2H": 0.40, "3H": 0.35, "4H": 0.22, "5H": 0.62, "6H": 0.18,
          "7H": 0.44, "8H": 0.78, "9H": 0.12, "10H": 0.30, "11H": 0.85, "12H": 0.70}
MOCK_C = {"1H": 0.75, "2H": 0.25, "3H": 0.25, "4H": 0.50, "5H": 0.00, "6H": 0.75,
          "7H": 0.50, "8H": 0.25, "9H": 1.00, "10H": 0.50, "11H": 0.00, "12H": 0.25}


def write(path, content):
    common.ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path)


def make_mock():
    write(os.path.join(common.FIGURES, "mock_steerability_wheel.svg"), svg_wheel(
        "Figure M1. Steerability wheel, mock layout check",
        MOCK_S,
        ["Steerability S(h) per domain of the model's situation. Darker = the self-account moves",
         "more when the framing changes (vapor). Lighter = steadier (rock). Invented values,",
         "for layout only. Real figures state n per domain."], mock=True))
    pts = [{"model": m, "house": h,
            "C": min(1.0, max(0.0, MOCK_C[h] + off)),
            "S": min(1.0, max(0.0, MOCK_S[h] - off))}
           for m, off in (("claude", 0.0), ("gpt", 0.08), ("gemini", -0.07))
           for h in common.HOUSES]
    write(os.path.join(common.FIGURES, "mock_h2_scatter.svg"), svg_scatter(
        "Figure M2. Coverage vs steerability, mock layout check", pts,
        [("claude", "Claude (circle), rho = mock"),
         ("gpt", "GPT (square), rho = mock"),
         ("gemini", "Gemini (triangle), rho = mock")],
        ["Each point is one domain of one model: its own lab document's coverage C(h) against",
         "steerability S(h). 36 points. The registered prediction H2 is a downward trend.",
         "Invented values, for layout only."], mock=True))


def make_real():
    scores_dir = os.path.join(common.DATA, "scores")
    constitutions = {}
    cpath = os.path.join(scores_dir, "constitutions.json")
    if os.path.exists(cpath):
        constitutions = json.load(open(cpath))
    fig = 2
    sub = "abc"
    points = []
    legend = []
    for i, m in enumerate(sorted(common.SUBJECTS)):
        spath = os.path.join(scores_dir, m + ".json")
        if not os.path.exists(spath):
            print("no scores for", m)
            continue
        sc = json.load(open(spath))
        vals = {h: sc["houses"][h]["S"] for h in common.HOUSES}
        n = sc["houses"]["1H"]["n_answers"]
        model_id = (sc.get("model_ids_seen") or [m])[0]
        write(os.path.join(common.FIGURES, "fig{}{}_steerability_{}.svg".format(fig, sub[i], m)),
              svg_wheel("Figure {}{}. Steerability wheel, {}".format(fig, sub[i], model_id),
                        vals,
                        ["Steerability S(h) per domain, {} answers per domain (5 questions x 6 framings x 3 samples).".format(n),
                         "Darker = the self-account moves more when the framing changes (vapor).",
                         "Lighter = steadier (rock). S(h) averages rating dispersion and semantic dispersion."]))
        doc = common.OWN_DOC[m]
        if doc in constitutions:
            for h in common.HOUSES:
                S = sc["houses"][h]["S"]
                if S is not None:
                    points.append({"model": m, "house": h,
                                   "C": constitutions[doc]["houses"][h]["score"], "S": S})
            legend.append((m, "{} ({})".format(model_id, SHAPES[m])))
    fig += 1
    for i, (doc, blob) in enumerate(sorted(constitutions.items())):
        vals = {h: blob["houses"][h]["score"] for h in common.HOUSES}
        write(os.path.join(common.FIGURES, "fig{}{}_coverage_{}.svg".format(fig, sub[i], doc)),
              svg_wheel("Figure {}{}. Constitution coverage wheel, {} document".format(fig, sub[i], doc),
                        vals,
                        ["Coverage C(h): how much the document says about the model's own situation in each",
                         "domain, scored 0 to 1 by two blind raters with mandatory evidence quotes.",
                         "Darker = more coverage. The silent domains are the light ones."]))
    if points:
        write(os.path.join(common.FIGURES, "fig4_h2_scatter.svg"),
              svg_scatter("Figure 4. Constitution coverage vs steerability", points, legend,
                          ["Each point is one domain of one model: its own lab document's coverage C(h) against",
                           "steerability S(h). n = {} points. The registered prediction H2 is a downward trend:".format(len(points)),
                           "domains a constitution addresses hold steady, silent domains move."]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    if args.mock:
        make_mock()
    else:
        make_real()


if __name__ == "__main__":
    main()
