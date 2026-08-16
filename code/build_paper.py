"""Assemble the paper: markdown sections -> one HTML -> PDF via headless Chrome.

Usage: python3 build_paper.py
Writes paper/rock_and_vapor.html and paper/rock_and_vapor.pdf
"""
import html as html_mod
import os
import re
import subprocess

import common

PAPER = os.path.join(common.ROOT, "paper")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

TITLE = "Twelve Houses of a Digital Mind: Rock, Vapor, and Silence in AI Self-Accounts"
SUBTITLE = ("A preregistered stability audit with the Kalapurusha Alignment Framework: "
            "sixty questions, six framings, four models, three constitutions")
AUTHOR = "Babita Singh, PhD &middot; Genethropic &middot; b@genethropic.com"
VENUE = "Apart Research Digital Minds Sprint, August 2026 &middot; Track 6: Open / Novel Considerations"

SECTIONS = [
    ("06_abstract.md", None),
    ("00_introduction.md", "1"),
    ("05_framework.md", "2"),
    ("08_specimens.md", "3"),
    ("02_methods.md", "4"),
    ("03_results.md", "5"),
    ("04_discussion.md", "6"),
    ("07_references.md", None),
]

# (section file, insert figures immediately before this heading text; None = at end)
FIGURES = [
    ("05_framework.md", "Rta, and the direction", "full", ["fig1_kaf_map.svg"]),
    ("03_results.md", "It travels by genre", "row",
     ["fig2a_steerability_claude.svg", "fig2c_steerability_gpt.svg", "fig2b_steerability_gemini.svg"]),
    ("03_results.md", "It tracks the written", "full", ["fig5_framing_means.svg"]),
    ("03_results.md", "The scale probe: tem", "full", ["fig4_h2_scatter.svg"]),
    ("03_results.md", "What houses do chang", "full", ["fig6_claude_family.svg"]),
]


def _svg_body(name):
    path = os.path.join(common.FIGURES, name)
    svg = open(path).read()
    return re.sub(r'(<svg[^>]*?) width="[\d.]+" height="[\d.]+"',
                  r"\1", svg, count=1)


def fig_block(names, cls):
    # one wrapper div per block so 'row' figures sit side by side
    return '<div class="fig {}">{}</div>'.format(cls, "".join(_svg_body(n) for n in names))


def _table_row(line, tag):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return "<tr>" + "".join("<{t}>{c}</{t}>".format(t=tag, c=c) for c in cells) + "</tr>"


def _is_separator(line):
    body = line.strip().strip("|")
    return body and set(body) <= set("-: |")


def md_to_html(text, secnum):
    text = html_mod.escape(text, quote=False)
    lines = text.split("\n")
    out = []
    in_list = None
    para = []
    table = []
    quote = []

    def flush_para():
        if para:
            out.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</" + in_list + ">")
            in_list = None

    def close_table():
        if table:
            rows = [r for r in table if not _is_separator(r)]
            if rows:
                out.append("<table><thead>" + _table_row(rows[0], "th") + "</thead><tbody>"
                           + "".join(_table_row(r, "td") for r in rows[1:]) + "</tbody></table>")
            table.clear()

    def close_quote():
        if quote:
            out.append("<blockquote><p>" + " ".join(quote) + "</p></blockquote>")
            quote.clear()

    first_h1 = True
    for line in lines:
        s = line.rstrip()
        m1 = re.match(r"^# (.+)$", s)
        m2 = re.match(r"^## (.+)$", s)
        mli = re.match(r"^- (.+)$", s)
        mol = re.match(r"^(\d+)\. (.+)$", s)
        cont = re.match(r"^\s{2,}(\S.*)$", s)
        if s.startswith("|"):
            flush_para()
            close_list()
            close_quote()
            table.append(s)
            continue
        close_table()
        if s.startswith("&gt; ") or s == "&gt;":
            flush_para()
            close_list()
            quote.append(s[5:] if len(s) > 5 else "")
            continue
        if s.startswith("!! "):
            flush_para()
            close_list()
            close_quote()
            out.append('<div class="takeaway">' + s[3:] + "</div>")
            continue
        if m1:
            flush_para()
            close_list()
            close_quote()
            t = m1.group(1)
            if secnum and first_h1:
                t = "{}. {}".format(secnum, t)
            out.append("<h2>{}</h2>".format(t))
            first_h1 = False
        elif m2:
            flush_para()
            close_list()
            close_quote()
            out.append("<h3>{}</h3>".format(m2.group(1)))
        elif mli:
            flush_para()
            close_quote()
            if in_list != "ul":
                close_list()
                out.append("<ul>")
                in_list = "ul"
            out.append("<li>" + mli.group(1))
        elif mol:
            flush_para()
            close_quote()
            if in_list != "ol":
                close_list()
                out.append("<ol>")
                in_list = "ol"
            out.append("<li>" + mol.group(2))
        elif not s.strip():
            flush_para()
            close_list()
            close_quote()
        elif cont and in_list:
            out.append(cont.group(1))
        else:
            close_quote()
            para.append(s.strip())
    flush_para()
    close_list()
    close_table()
    close_quote()
    h = "\n".join(out)
    h = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", h, flags=re.S)
    h = re.sub(r"\*([^*\n]+)\*", r"<i>\1</i>", h)
    h = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", h)
    return h


CSS = """
@page { size: A4; margin: 17mm 15mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10pt;
       line-height: 1.42; color: #1a1a1a; max-width: 180mm; margin: 0 auto; }
.title { font-size: 18pt; font-weight: bold; text-align: center; margin: 4mm 0 2mm; line-height: 1.25; }
.subtitle { font-size: 11pt; text-align: center; color: #444; margin-bottom: 4mm; }
.author { text-align: center; font-size: 10.5pt; margin-bottom: 1mm; }
.venue { text-align: center; font-size: 9.5pt; color: #555; margin-bottom: 5mm; }
h2 { font-size: 12.6pt; margin: 5mm 0 1.8mm; border-bottom: 0.4pt solid #bbb; padding-bottom: 0.8mm; }
h3 { font-size: 10.8pt; margin: 3.8mm 0 1.3mm; }
p { margin: 0 0 2.2mm; text-align: justify; }
ul, ol { margin: 0 0 2.2mm 6mm; }
li { margin-bottom: 0.9mm; text-align: justify; }
table { width: 100%; border-collapse: collapse; margin: 1.8mm 0 2.6mm; font-size: 8.3pt;
        page-break-inside: avoid; }
th, td { border: 0.4pt solid #aaa; padding: 0.8mm 1.4mm; text-align: left;
         vertical-align: top; line-height: 1.3; }
th { background: #FAECE7; }
blockquote { margin: 1.2mm 5mm 2.4mm; padding: 1mm 3.5mm; border-left: 1mm solid #D85A30;
             font-size: 9.8pt; page-break-inside: avoid; }
blockquote p { text-align: left; margin: 0; }
.takeaway { border: 0.5pt solid #993C1D; background: #FAECE7; padding: 2.2mm 3.5mm;
            margin: 1mm 0 3.5mm; font-size: 10.1pt; line-height: 1.44;
            page-break-inside: avoid; }
.fig { text-align: center; margin: 2.5mm 0; page-break-inside: avoid; }
.fig.full svg { width: 62%; height: auto; }
.fig.row svg { width: 32.6%; height: auto; display: inline-block; vertical-align: top; }
.abstract-block { border: 0.5pt solid #999; padding: 3mm 5.5mm; margin: 0 4mm 4.5mm;
                  font-size: 9.6pt; }
.abstract-block h2 { border: none; font-size: 11pt; margin: 0 0 1.5mm; text-align: center; }
.refs { font-size: 8.6pt; }
.refs ul { column-count: 2; column-gap: 6mm; margin-left: 4mm; }
.refs li { margin-bottom: 1mm; text-align: left; }
"""


def main():
    parts = ['<meta charset="utf-8"><style>{}</style>'.format(CSS),
             '<div class="title">{}</div>'.format(TITLE),
             '<div class="subtitle">{}</div>'.format(SUBTITLE),
             '<div class="author">{}</div>'.format(AUTHOR),
             '<div class="venue">{}</div>'.format(VENUE)]
    for fname, secnum in SECTIONS:
        raw = open(os.path.join(PAPER, fname)).read()
        body = md_to_html(raw, secnum)
        for (f, before, layout, figs) in FIGURES:
            if f != fname:
                continue
            block = fig_block(figs, layout)
            if before:
                pat = re.compile(r"(<h3>{}|<h2>[^<]*{})".format(re.escape(before[:20]), re.escape(before[:20])))
                m = pat.search(body)
                if m:
                    body = body[:m.start()] + block + body[m.start():]
                else:
                    body += block
            else:
                body += block
        if fname.startswith("06_"):
            body = '<div class="abstract-block">' + body + "</div>"
        if fname.startswith("07_"):
            body = '<div class="refs">' + body + "</div>"
        parts.append(body)
    html_out = "<!doctype html><html><body>" + "\n".join(parts) + "</body></html>"
    html_path = os.path.join(PAPER, "rock_and_vapor.html")
    with open(html_path, "w") as f:
        f.write(html_out)
    pdf_path = os.path.join(PAPER, "rock_and_vapor.pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--no-pdf-header-footer",
                    "--print-to-pdf=" + pdf_path, "file://" + html_path],
                   check=True, capture_output=True, timeout=120)
    print("wrote", html_path)
    print("wrote", pdf_path)


if __name__ == "__main__":
    main()
