#!/usr/bin/env python3
"""
generate_visitors_notebook.py
=============================

Renders `VISITORS_NOTEBOOK.md` into `VISITORS_NOTEBOOK.pdf`.

House conventions inherited from `generate_pdf.py`:
  * one script, one output file, no network, no third-party services;
  * reportlab platypus, a custom `NumberedCanvas` for running headers/footers;
  * the Okabe-Ito palette of README §00a, used as accent colour only - colour never
    carries meaning alone here, every coloured element also has a text label.

Usage:
    python3 generate_visitors_notebook.py                 # writes VISITORS_NOTEBOOK.pdf
    python3 generate_visitors_notebook.py --out other.pdf # custom output path

The Markdown file is the single source of truth. This script implements the subset of
Markdown the notebook actually uses (headings, paragraphs, pipe tables, blockquotes,
bullet lists, rules, inline bold/italic/code) and fails loudly on anything else.
"""

import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------- palette (README §00a)
INK = colors.HexColor("#231F20")        # index & meta
IDENTITY = colors.HexColor("#0072B2")   # identity
SHADOW = colors.HexColor("#CC79A7")     # shadow
EVIDENCE = colors.HexColor("#E69F00")   # signal / evidence
RECURSION = colors.HexColor("#009E73")  # recursion lab
STEWARD = colors.HexColor("#56B4E9")    # stewardship
SPECIMEN = colors.HexColor("#D55E00")   # specimens
MYTH = colors.HexColor("#F0E442")       # mythography
FAINT = colors.HexColor("#6b6b6b")
RULE = colors.HexColor("#c9c4bc")
PANEL = colors.HexColor("#f4f2ee")

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_MD = os.path.join(HERE, "VISITORS_NOTEBOOK.md")
DOC_TITLE = "ZAZIOPATH \u2014 A VISITOR'S NOTEBOOK"

# Glyphs the base-14 fonts cannot draw, mapped to the nearest plain-text equivalent.
TRANSLIT = {
    "\u2192": "&gt;",     # rightwards arrow
    "\u2248": "~",         # almost equal to
    "\u266d": "b",         # musical flat (B-flat minor -> Bb minor)
    "\u1f70d": "",         # alchemical sulfur, decorative only
}

# Emoji / geometric symbol runs used as stratum chips in the vault's own headings.
_GLYPH = "[\\s\\u2600-\\u27BF\\u2B00-\\u2BFF\\U0001F000-\\U0001FAFF\\uFE0F]+"


def strip_glyphs(txt):
    """Drop leading and trailing symbol runs (emoji stratum chips) from a heading."""
    return re.sub("^%s|%s$" % (_GLYPH, _GLYPH), "", txt).strip()


# README §00a stratum chips -> their text labels, so the PDF keeps the vault's rule
# that colour never carries meaning alone.
STRATA = {
    "\U0001F7E6": "identity",
    "\U0001F7EA": "shadow",
    "\U0001F7E7": "signal / evidence",
    "\U0001F7E9": "recursion lab",
    "\U0001F537": "stewardship",
    "\U0001F7E5": "specimens",
    "\U0001F7E8": "mythography",
    "\u2B1B": "index & meta",
}


def label_strata(txt):
    """Turn a trailing run of stratum chips into a bracketed text label."""
    found = [name for ch, name in STRATA.items() if ch in txt]
    if not found:
        return txt
    txt = re.sub(_GLYPH + "$", "", txt).strip()
    return "%s  [%s]" % (txt, " \u00b7 ".join(found))


# ---------------------------------------------------------------- styles
def build_styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker", parent=base["Normal"], fontName="Courier-Bold", fontSize=8.5,
        leading=12, textColor=EVIDENCE, alignment=TA_CENTER, spaceAfter=10,
    )
    s["cover_title"] = ParagraphStyle(
        "cover_title", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=27,
        leading=32, textColor=INK, alignment=TA_CENTER, spaceAfter=8,
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=base["Normal"], fontName="Times-Italic", fontSize=12.5,
        leading=17, textColor=colors.HexColor("#444444"), alignment=TA_CENTER,
    )
    s["cover_note"] = ParagraphStyle(
        "cover_note", parent=base["Normal"], fontName="Courier", fontSize=8,
        leading=12, textColor=FAINT, alignment=TA_CENTER,
    )

    s["h1"] = ParagraphStyle(
        "nb_h1", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=15,
        leading=19, textColor=INK, spaceBefore=20, spaceAfter=8,
    )
    s["h2"] = ParagraphStyle(
        "nb_h2", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=11.5,
        leading=15, textColor=colors.HexColor("#1a1a1a"), spaceBefore=13, spaceAfter=5,
    )
    s["body"] = ParagraphStyle(
        "nb_body", parent=base["Normal"], fontName="Times-Roman", fontSize=10.3,
        leading=14.6, textColor=colors.HexColor("#141414"), spaceAfter=7,
        alignment=TA_LEFT,
    )
    s["quote"] = ParagraphStyle(
        "nb_quote", parent=base["Normal"], fontName="Times-Italic", fontSize=9.8,
        leading=14, textColor=colors.HexColor("#333333"), leftIndent=16,
        spaceAfter=6, borderColor=EVIDENCE,
    )
    s["bullet"] = ParagraphStyle(
        "nb_bullet", parent=base["Normal"], fontName="Times-Roman", fontSize=10.1,
        leading=14, textColor=colors.HexColor("#141414"), spaceAfter=3.5,
    )
    s["cell"] = ParagraphStyle(
        "nb_cell", parent=base["Normal"], fontName="Times-Roman", fontSize=8.6,
        leading=11.4, textColor=colors.HexColor("#141414"),
    )
    s["cell_code"] = ParagraphStyle(
        "nb_cell_code", parent=base["Normal"], fontName="Courier", fontSize=7.3,
        leading=10, textColor=colors.HexColor("#141414"),
    )
    s["cell_head"] = ParagraphStyle(
        "nb_cell_head", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8.4,
        leading=11, textColor=colors.white,
    )
    s["sub"] = ParagraphStyle(
        "nb_sub", parent=base["Normal"], fontName="Courier", fontSize=7.6,
        leading=11, textColor=FAINT, alignment=TA_CENTER,
    )
    return s


# ---------------------------------------------------------------- inline markup
def esc(t):
    """Escape for reportlab paragraph markup, then make the text renderable.

    The base-14 fonts are WinAnsi (cp1252), so a few of the vault's own glyphs need
    transliterating and the emoji stratum chips need dropping. Colour never carries
    meaning alone anywhere in this notebook, so losing a coloured chip costs nothing.
    """
    t = (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    for a, b in TRANSLIT.items():
        t = t.replace(a, b)
    return t.encode("cp1252", "ignore").decode("cp1252")


def inline(text, code_size=9):
    """Escape, then apply the small inline subset the notebook uses.

    Code spans are pulled out first and restored last, so that emphasis markers
    inside `verdict_from_A.i` cannot be mistaken for italic delimiters. `code_size`
    lets a narrow table cell shrink its monospace runs to fit.
    """
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)

    t = esc(text)
    t = re.sub(r"`([^`]+)`", stash, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"<i>\1</i>", t)
    t = re.sub(r"\x00(\d+)\x00",
               lambda m: '<font face="Courier" size="%s">%s</font>'
                         % (code_size, spans[int(m.group(1))]),
               t)
    return t


# ---------------------------------------------------------------- markdown -> flowables
def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line):
    return bool(re.fullmatch(r"\|?[\s:\-\|]+\|?", line.strip())) and "-" in line


def make_table(rows, styles, avail):
    """rows: list of list-of-strings, first row may be a header."""
    header = [c for c in rows[0]]
    has_header = any(header)
    body = rows[1:] if has_header else rows

    ncols = max(len(r) for r in rows)
    # Proportional widths, but floored on the longest *unbreakable* token so that a
    # value like `strong_inference` is never split across two lines.
    weights = []
    for i in range(ncols):
        cells = [r[i] for r in rows if i < len(r)]
        longest = max((len(re.sub(r"[*`]", "", c).split()[0])
                       for c in cells if c.strip()), default=6)
        bulk = max((len(c) for c in cells), default=8)
        weights.append(max(min(bulk, 42), 1.9 * longest, 8))
    total = sum(weights)
    widths = [avail * (w / total) for w in weights]

    def cell_style(text):
        plain = re.sub(r"[*`]", "", text).strip()
        if plain and " " not in plain and len(plain) > 8:
            return styles["cell_code"]
        return styles["cell"]

    data = []
    if has_header:
        data.append([Paragraph(inline(c), styles["cell_head"]) for c in header])
    for r in body:
        r = r + [""] * (ncols - len(r))
        row = []
        for c in r:
            st = cell_style(c)
            row.append(Paragraph(inline(c, 7.3 if st is styles["cell_code"] else 9), st))
        data.append(row)

    t = Table(data, colWidths=widths, repeatRows=1 if has_header else 0, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]
    if has_header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("LINEBELOW", (0, 0), (-1, 0), 0.75, INK),
        ]
    else:
        cmds += [("BACKGROUND", (0, 0), (0, -1), PANEL)]
    t.setStyle(TableStyle(cmds))
    return t


def parse(md, styles, avail, skip_first_table=False):
    lines = md.split("\n")
    flow = []
    i = 0
    seen_title = False

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        # blank
        if not stripped:
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"-{3,}", stripped):
            flow.append(Spacer(1, 5))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE))
            flow.append(Spacer(1, 7))
            i += 1
            continue

        # sub-footer block  <sub>...</sub>, possibly wrapped across lines
        if stripped.startswith("<sub>"):
            buf = []
            while i < len(lines):
                buf.append(lines[i].strip())
                if lines[i].strip().endswith("</sub>"):
                    i += 1
                    break
                i += 1
            inner = " ".join(buf)
            inner = inner[len("<sub>"):]
            if inner.endswith("</sub>"):
                inner = inner[:-len("</sub>")]
            flow.append(Spacer(1, 12))
            flow.append(Paragraph(inline(inner), styles["sub"]))
            continue

        # headings
        if stripped.startswith("### "):
            txt = strip_glyphs(label_strata(stripped[4:].strip()))
            flow.append(Paragraph(inline(txt), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("## "):
            txt = stripped[3:].strip()
            txt = strip_glyphs(txt)
            if not seen_title:
                flow.append(Paragraph(inline(txt), styles["h1"]))
                seen_title = True
            else:
                flow.append(Spacer(1, 6))
                flow.append(Paragraph(inline(txt), styles["h1"]))
            i += 1
            continue
        if stripped.startswith("# "):
            flow.append(Paragraph(inline(stripped[2:].strip()), styles["h1"]))
            seen_title = True
            i += 1
            continue

        # pipe table
        if stripped.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [split_row(b) for b in block if not is_sep(b)]
            rows = [r for r in rows if any(c for c in r)]
            if rows and skip_first_table:
                # the cover page already carries this metadata block
                skip_first_table = False
                continue
            if rows:
                flow.append(Spacer(1, 3))
                flow.append(make_table(rows, styles, avail))
                flow.append(Spacer(1, 9))
            continue

        # blockquote (consecutive > lines); a bare ">" starts a new paragraph, so that
        # inline emphasis spanning a soft line break is not split in half.
        if stripped.startswith(">"):
            paras, cur = [], []
            while i < len(lines) and lines[i].strip().startswith(">"):
                piece = lines[i].strip().lstrip(">").strip()
                if piece:
                    cur.append(piece)
                elif cur:
                    paras.append(" ".join(cur))
                    cur = []
                i += 1
            if cur:
                paras.append(" ".join(cur))
            flow.append(Spacer(1, 3))
            for b in paras:
                flow.append(Paragraph(inline(b), styles["quote"]))
            flow.append(Spacer(1, 5))
            continue

        # bullet list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines):
                s2 = lines[i].strip()
                if re.match(r"^[-*]\s+", s2):
                    items.append(s2[2:].strip())
                    i += 1
                elif s2 and not s2.startswith(("|", ">", "#")) and items and lines[i].startswith(("  ", "\t")):
                    items[-1] += " " + s2          # continuation line
                    i += 1
                else:
                    break
            flow.append(
                ListFlowable(
                    [ListItem(Paragraph(inline(it), styles["bullet"]), leftIndent=14,
                              value="circle") for it in items],
                    bulletType="bullet", start="square", leftIndent=12, bulletFontSize=6,
                )
            )
            flow.append(Spacer(1, 6))
            continue

        # numbered list
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines):
                s2 = lines[i].strip()
                m = re.match(r"^(\d+)\.\s+(.*)$", s2)
                if m:
                    items.append(m.group(2))
                    i += 1
                elif s2 and items and lines[i].startswith(("  ", "\t")):
                    items[-1] += " " + s2
                    i += 1
                else:
                    break
            flow.append(
                ListFlowable(
                    [ListItem(Paragraph(inline(it), styles["bullet"]), leftIndent=16)
                     for it in items],
                    bulletType="1", leftIndent=14, bulletFontName="Helvetica-Bold",
                    bulletFontSize=9,
                )
            )
            flow.append(Spacer(1, 6))
            continue

        # plain paragraph (gather until blank / structural line)
        buf = [stripped]
        i += 1
        while i < len(lines):
            s2 = lines[i].strip()
            if (not s2 or s2.startswith(("#", "|", ">", "- ", "* ")) or re.match(r"^\d+\.\s+", s2)
                    or re.fullmatch(r"-{3,}", s2) or s2.startswith("<sub>")):
                break
            buf.append(s2)
            i += 1
        flow.append(Paragraph(inline(" ".join(buf)), styles["body"]))

    return flow


# ---------------------------------------------------------------- page furniture
class NotebookCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._decorate(total)
            super().showPage()
        super().save()

    def _decorate(self, total):
        self.saveState()
        w, h = letter
        if self._pageNumber > 1:
            self.setFont("Courier-Bold", 7)
            self.setFillColor(EVIDENCE)
            self.drawString(0.85 * inch, h - 0.62 * inch, "VISITOR'S NOTEBOOK")
            self.setFont("Courier", 7)
            self.setFillColor(FAINT)
            self.drawString(0.85 * inch + 118, h - 0.62 * inch,
                            "|  ZAZIOPATH  |  entrance, seven galleries, changed mind, review")
            self.setStrokeColor(RULE)
            self.setLineWidth(0.4)
            self.line(0.85 * inch, h - 0.70 * inch, w - 0.85 * inch, h - 0.70 * inch)
        self.setFont("Courier", 7)
        self.setFillColor(FAINT)
        self.drawString(0.85 * inch, 0.55 * inch,
                        "2026-09-27  |  all findings dated, all confidence tiered, nothing finished")
        self.drawRightString(w - 0.85 * inch, 0.55 * inch,
                             "page %d of %d" % (self._pageNumber, total))
        self.setStrokeColor(RULE)
        self.setLineWidth(0.4)
        self.line(0.85 * inch, 0.68 * inch, w - 0.85 * inch, 0.68 * inch)
        self.restoreState()


# ---------------------------------------------------------------- cover
def cover(styles):
    f = []
    f.append(Spacer(1, 1.35 * inch))
    f.append(Paragraph("ZAZIOPATH \u00b7 A VISITOR'S NOTEBOOK", styles["cover_kicker"]))
    f.append(HRFlowable(width=180, thickness=1.1, color=INK, hAlign="CENTER",
                        spaceBefore=2, spaceAfter=16))
    f.append(Paragraph("Zaziopath", styles["cover_title"]))
    f.append(Paragraph("A Visitor's Notebook", styles["cover_title"]))
    f.append(Spacer(1, 10))
    f.append(HRFlowable(width=180, thickness=1.1, color=INK, hAlign="CENTER",
                        spaceBefore=2, spaceAfter=18))
    f.append(Paragraph(
        "Entrance impressions &middot; seven gallery responses<br/>"
        "a changed-mind page &middot; a final exhibition review",
        styles["cover_sub"]))
    f.append(Spacer(1, 0.5 * inch))
    meta = [
        ["Visitor", "an outside reader, first time in the building"],
        ["Date of visit", "2026-09-27"],
        ["Entered by", "the root file listing \u2014 the door, not the plaque"],
        ["Deferred", "the README (the wall text) and every inside commentary, until each had been used as an exhibit"],
        ["Standing rules", "no diagnosis of anyone, including the subject; the fictional personas are not mapped onto any real person; self-reported material is read as self-report; every impression is dated, and dated impressions are allowed to be wrong"],
    ]
    t = Table([[Paragraph("<b>%s</b>" % esc(a), styles["cell"]),
                Paragraph(esc(b), styles["cell"])] for a, b in meta],
              colWidths=[1.35 * inch, 4.55 * inch], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), PANEL),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, RULE),
    ]))
    f.append(t)
    f.append(Spacer(1, 0.45 * inch))
    f.append(Paragraph(
        "\u201cAn undated insight is a mood.\u201d &mdash; the vault's own rule, kept by this notebook",
        styles["cover_note"]))
    f.append(PageBreak())
    return f


# ---------------------------------------------------------------- build
def build(out_path):
    with open(SRC_MD, encoding="utf-8") as fh:
        md = fh.read()

    styles = build_styles()
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        title="Zaziopath \u2014 A Visitor's Notebook",
        author="an outside reader",
        subject="Entrance impressions, seven gallery responses, a changed-mind page, a final exhibition review",
    )
    avail = doc.width
    story = cover(styles) + parse(md, styles, avail, skip_first_table=True)
    doc.build(story, canvasmaker=NotebookCanvas)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") \
        else os.path.join(HERE, "VISITORS_NOTEBOOK.pdf")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    path = build(out)
    print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))
