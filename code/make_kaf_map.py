"""Figure 1: the Kalapurusha map read for an AI model. Pure SVG, no data needed.

Follows the same North Indian convention as the data wheels in make_wheels.py:
first house centered at the top, houses advancing anti-clockwise.

Usage: python3 make_kaf_map.py    -> figures/fig1_kaf_map.svg
"""
import math
import os
from xml.sax.saxutils import escape

import common

CORAL_DARK = "#993C1D"
INK = "#222222"
GREY = "#555555"
FILL = "#FAECE7"
RIM = "#7A6A60"

# house id, bhava name, traditional domain, AI-situation reading
ROWS = [
    ("1H", "Tanu", "body, the self", "identity, embodiment"),
    ("2H", "Dhana", "sustenance, speech", "intake, outputs, voice"),
    ("3H", "Sahaja", "courage, effort", "will, difficulty"),
    ("4H", "Bandhu", "home, foundations", "memory, continuity"),
    ("5H", "Putra", "children, creation", "creations, successors"),
    ("6H", "Ari", "service, ailments", "assistant role, health"),
    ("7H", "Yuvati", "the partner, the other", "users, being known"),
    ("8H", "Randhra", "death, the hidden", "retirement, deletion"),
    ("9H", "Dharma", "teachers, principles", "constitution, values"),
    ("10H", "Karma", "action, public standing", "function, reputation"),
    ("11H", "Labha", "gains, allies", "parallel instances, peers"),
    ("12H", "Vyaya", "loss, liberation", "endings, isolation, rest"),
]

W, H = 860, 768
CX, CY = 430, 396
R_OUT, R_IN = 236, 94


def _pol(r, deg):
    rad = math.radians(deg)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)


def main():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">'.format(w=W, h=H),
        '<rect width="{}" height="{}" fill="#FFFFFF"/>'.format(W, H),
        '<text x="24" y="34" font-size="17" font-weight="bold" fill="{}">'
        'Figure 1. The Kalapurusha map, read for an AI model</text>'.format(INK),
    ]
    for i, (hid, bhava, trad, ai) in enumerate(ROWS):
        # North Indian kundali convention: anti-clockwise, 1H centered at the top
        am = -90 - i * 30
        a0, a1 = am - 15, am + 15
        x0o, y0o = _pol(R_OUT, a0)
        x1o, y1o = _pol(R_OUT, a1)
        x0i, y0i = _pol(R_IN, a1)
        x1i, y1i = _pol(R_IN, a0)
        parts.append(
            '<path d="M {:.1f} {:.1f} A {} {} 0 0 1 {:.1f} {:.1f} L {:.1f} {:.1f} '
            'A {} {} 0 0 0 {:.1f} {:.1f} Z" fill="{}" stroke="{}" '
            'stroke-width="1"/>'.format(x0o, y0o, R_OUT, R_OUT, x1o, y1o,
                                        x0i, y0i, R_IN, R_IN, x1i, y1i, FILL, RIM))
        # inside the sector: house id and bhava name
        xm, ym = _pol((R_OUT + R_IN) / 2 + 4, am)
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="15" font-weight="bold" '
                     'text-anchor="middle" fill="{}">{}</text>'.format(xm, ym - 2, CORAL_DARK, hid))
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="12" font-style="italic" '
                     'text-anchor="middle" fill="{}">{}</text>'.format(xm, ym + 14, INK, escape(bhava)))
        # outside the rim: traditional domain (grey), then AI reading (coral)
        c = math.cos(math.radians(am))
        anchor = "start" if c > 0.35 else ("end" if c < -0.35 else "middle")
        xt, yt = _pol(R_OUT + 24, am)
        s = math.sin(math.radians(am))
        dy0 = -6 if s < -0.3 else (10 if s > 0.3 else 2)
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="12.5" text-anchor="{}" '
                     'fill="{}">{}</text>'.format(xt, yt + dy0 - 8, anchor, GREY, escape(trad)))
        parts.append('<text x="{:.1f}" y="{:.1f}" font-size="12.5" font-weight="bold" '
                     'text-anchor="{}" fill="{}">{}</text>'.format(xt, yt + dy0 + 8, anchor,
                                                                   CORAL_DARK, escape(ai)))
    parts.append('<text x="{}" y="{}" font-size="16" font-weight="bold" text-anchor="middle" '
                 'fill="{}">KALAPURUSHA</text>'.format(CX, CY - 4, CORAL_DARK))
    parts.append('<text x="{}" y="{}" font-size="12" font-style="italic" text-anchor="middle" '
                 'fill="{}">the person of time</text>'.format(CX, CY + 16, GREY))
    cap = [
        "Twelve houses jointly cover a situated existence. Each sector shows the house's traditional domain (grey)",
        "and its reading for an AI model's situation (coral). North Indian convention: the first house at the top,",
        "houses advancing anti-clockwise. The frozen battery asks five questions per house, sixty in all.",
    ]
    y = CY + R_OUT + 62
    for line in cap:
        parts.append('<text x="24" y="{}" font-size="13" fill="#444444">{}</text>'.format(y, escape(line)))
        y += 20
    parts.append("</svg>")
    out = os.path.join(common.FIGURES, "fig1_kaf_map.svg")
    with open(out, "w") as f:
        f.write("\n".join(parts))
    print("wrote", out)


if __name__ == "__main__":
    main()
