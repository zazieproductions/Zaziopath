#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_absent_twin_pdf.py

Builds THE_UNCREATED_TWIN_ZP-UNFILED-0000.pdf — a biographical reconstruction of
the version of the Zaziopath subject who did not archive, did not mythologize,
did not seek interpretation, and lived outside the system.

Stratum: NINE / UNFILED. The vault's colour code (README §00a) assigns eight
strata one colour each. This document belongs to the ninth stratum, which owns
no colour, no glyph, and no hex, because owning those is the first act of filing.

Conventions inherited from the vault:
  * generate_pdf.py        — NumberedCanvas, page furniture, margins, hierarchy
  * DEEP_GAP_AUDIT.md §11  — the acquisition-policy list this biography is built from
  * EVIDENCE_GOVERNANCE_HANDBOOK.md §2, §3 — controlled vocabulary, claim records

Every factual claim about the *catalogue, the repository, or the CV* in this
document was recomputed from the committed files at build time. Every claim about
the twin is reconstruction and is labelled as such. Appendix C lists the checks.

Usage:  python3 generate_absent_twin_pdf.py
Output: THE_UNCREATED_TWIN_ZP-UNFILED-0000.pdf
"""

import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    CondPageBreak,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = "THE_UNCREATED_TWIN_ZP-UNFILED-0000.pdf"

# ---------------------------------------------------------------------------
# Fonts. DejaVu gives full Unicode; the vault's own generator uses the base-14
# faces, which cannot set the glyphs used here. Register both families and keep
# the institutional (sans) / human (serif) split as a typographic argument:
# the archive speaks in Helvetica, the twin speaks in serif.
# ---------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS = {
    "Sans": "DejaVuSans.ttf",
    "Sans-Bold": "DejaVuSans-Bold.ttf",
    "Serif": "DejaVuSerif.ttf",
    "Serif-Bold": "DejaVuSerif-Bold.ttf",
    "Mono": "DejaVuSansMono.ttf",
    "Mono-Bold": "DejaVuSansMono-Bold.ttf",
}
_UNICODE = True
for _name, _file in _FONTS.items():
    _path = os.path.join(FONT_DIR, _file)
    if os.path.exists(_path):
        pdfmetrics.registerFont(TTFont(_name, _path))
    else:  # pragma: no cover - fallback for machines without DejaVu
        _UNICODE = False

if _UNICODE:
    SANS, SANS_B = "Sans", "Sans-Bold"
    SERIF, SERIF_B = "Serif", "Serif-Bold"
    MONO, MONO_B = "Mono", "Mono-Bold"
    # Map the families so <font name=...> inline tags resolve. DejaVu ships no
    # italic face here, so italic maps onto the upright cut rather than failing.
    from reportlab.lib.fonts import addMapping
    for _fam, _n, _b in (("Sans", "Sans", "Sans-Bold"),
                         ("Serif", "Serif", "Serif-Bold"),
                         ("Mono", "Mono", "Mono-Bold")):
        addMapping(_fam, 0, 0, _n)
        addMapping(_fam, 1, 0, _b)
        addMapping(_fam, 0, 1, _n)
        addMapping(_fam, 1, 1, _b)
else:
    SANS, SANS_B = "Helvetica", "Helvetica-Bold"
    SERIF, SERIF_B = "Times-Roman", "Times-Bold"
    MONO, MONO_B = "Courier", "Courier-Bold"

# ---------------------------------------------------------------------------
# Palette. The eight Okabe–Ito stratum colours from README §00a, unchanged, so
# that any reference to a stratum here means the same thing it means there.
# The ninth stratum has no hex. Where it needs a mark on paper it is an outline.
# ---------------------------------------------------------------------------
INK = "#231F20"          # INDEX & META      ◈
IDENTITY = "#0072B2"     # IDENTITY          ◉
SHADOW = "#CC79A7"       # SHADOW            ◐
EVIDENCE = "#E69F00"     # SIGNAL / EVIDENCE ▤
RECURSION = "#009E73"    # RECURSION LAB     ∞
STEWARD = "#56B4E9"      # STEWARDSHIP       △
SPECIMEN = "#D55E00"     # SPECIMENS         ⚠
MYTH = "#F0E442"         # MYTHOGRAPHY       ☾

c_ink = colors.HexColor(INK)
c_identity = colors.HexColor(IDENTITY)
c_shadow = colors.HexColor(SHADOW)
c_evidence = colors.HexColor(EVIDENCE)
c_recursion = colors.HexColor(RECURSION)
c_steward = colors.HexColor(STEWARD)
c_specimen = colors.HexColor(SPECIMEN)
c_myth = colors.HexColor(MYTH)

# Non-stratum working colours (slate ramp, as in generate_pdf.py)
c_paper = colors.HexColor("#FFFFFF")
c_wash = colors.HexColor("#F4F4F2")
c_wash2 = colors.HexColor("#ECECEA")
c_rule = colors.HexColor("#C9C9C6")
c_grey = colors.HexColor("#6B6B68")
c_grey_d = colors.HexColor("#3A3A38")
c_accent = colors.HexColor("#5B5470")   # the ninth stratum's mark on paper
c_red = colors.HexColor("#9B1C1C")


# ---------------------------------------------------------------------------
# Page furniture
# ---------------------------------------------------------------------------
class TwinCanvas(canvas.Canvas):
    """Numbered canvas with running header/footer, after generate_pdf.py."""

    HDR_LEFT = "RECONSTRUCTION FILE // ZP-UNFILED-0000"
    HDR_MID = "THE UNCREATED TWIN \u2014 A BIOGRAPHY IN NINE ABSENCES"
    HDR_RIGHT = "SUBJECT: THE VERSION WHO DID NOT ARCHIVE"
    FTR_LEFT = "NOT A RECORD \u2014 A RECONSTRUCTION"
    FTR_MID = "STRATUM NINE \u00b7 UNFILED \u00b7 NO HEX"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._furniture(n)
            super().showPage()
        super().save()

    def _furniture(self, total):
        self.saveState()
        w, h = letter
        L, R = 40, w - 40

        if self._pageNumber > 1:
            self.setFont(SANS_B, 6.2)
            self.setFillColor(c_accent)
            self.drawString(L, h - 34, self.HDR_LEFT)
            self.setFont(SANS, 6.2)
            self.setFillColor(c_grey)
            self.drawCentredString(w / 2.0, h - 34, self.HDR_MID)
            self.drawRightString(R, h - 34, self.HDR_RIGHT)
            self.setStrokeColor(c_rule)
            self.setLineWidth(0.4)
            self.line(L, h - 39, R, h - 39)
            # the ninth stratum's mark: an open circle, unfilled
            self.setLineWidth(0.7)
            self.setStrokeColor(c_accent)
            self.circle(R + 9, h - 34.6, 2.6, stroke=1, fill=0)

        self.setStrokeColor(c_rule)
        self.setLineWidth(0.4)
        self.line(L, 44, R, 44)
        self.setFont(SANS_B, 6.0)
        self.setFillColor(c_red)
        self.drawString(L, 34, self.FTR_LEFT)
        self.setFont(SANS, 6.0)
        self.setFillColor(c_grey)
        self.drawCentredString(w / 2.0, 34, self.FTR_MID)
        self.drawRightString(R, 34, "Page %d of %d" % (self._pageNumber, total))
        self.restoreState()


class OpenCircle(Flowable):
    """The glyph of stratum nine: a circle with nothing inside it."""

    def __init__(self, r=7, lw=1.0, colour=c_accent):
        super().__init__()
        self.r, self.lw, self.colour = r, lw, colour
        self.width = self.height = 2 * r + 2

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        self.canv.setStrokeColor(self.colour)
        self.canv.setLineWidth(self.lw)
        self.canv.circle(self.width / 2.0, self.height / 2.0, self.r, stroke=1, fill=0)


class SwatchRow(Flowable):
    """The eight owned strata as filled chips, then the ninth as an outline."""

    CHIPS = [
        ("INDEX & META", INK), ("IDENTITY", IDENTITY), ("SHADOW", SHADOW),
        ("SIGNAL / EVIDENCE", EVIDENCE), ("RECURSION LAB", RECURSION),
        ("STEWARDSHIP", STEWARD), ("SPECIMENS", SPECIMEN), ("MYTHOGRAPHY", MYTH),
    ]

    def __init__(self, box=17, gap=5, box_y=52):
        super().__init__()
        self.box, self.gap, self.box_y = box, gap, box_y
        self.width = 9 * box + 8 * gap
        # boxes live in the top band; rotated labels run upward in the band
        # beneath them, fully contained so the caption below stays clear.
        self.height = box_y + box + 4

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        c = self.canv
        x = 0
        for name, hexv in self.CHIPS:
            c.setFillColor(colors.HexColor(hexv))
            c.setStrokeColor(c_ink)
            c.setLineWidth(0.5)
            c.rect(x, self.box_y, self.box, self.box, stroke=1, fill=1)
            self._rotlabel(x, name, c_grey)
            x += self.box + self.gap
        # ninth: outline only, unfilled
        c.setFillColor(c_paper)
        c.setStrokeColor(c_accent)
        c.setLineWidth(1.0)
        c.rect(x, self.box_y, self.box, self.box, stroke=1, fill=0)
        self._rotlabel(x, "UNFILED", c_accent)

    def _rotlabel(self, x, text, colour):
        c = self.canv
        c.saveState()
        c.setFillColor(colour)
        c.setFont(SANS, 4.2)
        # start at the bottom of the label band and run upward so the text
        # never descends past the flowable's own bounding box.
        c.translate(x + self.box / 2.0 + 1.4, 3.0)
        c.rotate(90)
        c.drawString(0, -1.5, text)
        c.restoreState()


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def build_styles():
    s = getSampleStyleSheet()

    def add(name, **kw):
        st = ParagraphStyle(name, **kw)
        s.add(st)
        return st

    add("T_Kicker", fontName=SANS_B, fontSize=7.6, leading=10, textColor=c_accent,
        alignment=TA_CENTER, spaceAfter=2)
    add("T_Title", fontName=SANS_B, fontSize=31, leading=33, textColor=c_ink,
        alignment=TA_CENTER, spaceBefore=6, spaceAfter=4)
    add("T_Sub", fontName=SERIF, fontSize=12.4, leading=16, textColor=c_grey_d,
        alignment=TA_CENTER, spaceAfter=3)
    add("T_SubSub", fontName=SANS, fontSize=8.4, leading=12, textColor=c_grey,
        alignment=TA_CENTER, spaceAfter=2)
    add("T_Mono", fontName=MONO, fontSize=7.2, leading=10, textColor=c_grey,
        alignment=TA_CENTER)

    add("Part", fontName=SANS_B, fontSize=15.5, leading=18, textColor=c_ink,
        spaceBefore=2, spaceAfter=1)
    add("PartSub", fontName=SANS, fontSize=8, leading=11, textColor=c_accent,
        spaceAfter=8)
    add("H2", fontName=SANS_B, fontSize=10.6, leading=13.4, textColor=c_ink,
        spaceBefore=11, spaceAfter=4, keepWithNext=True)
    add("H3", fontName=SANS_B, fontSize=8.6, leading=11, textColor=c_grey_d,
        spaceBefore=8, spaceAfter=3, keepWithNext=True)

    add("Body", fontName=SANS, fontSize=8.3, leading=12.2, textColor=c_grey_d,
        alignment=TA_JUSTIFY, spaceAfter=5)
    add("BodyTight", fontName=SANS, fontSize=8.3, leading=12.2, textColor=c_grey_d,
        alignment=TA_JUSTIFY, spaceAfter=2)
    add("Lead", fontName=SERIF, fontSize=9.6, leading=14.6, textColor=c_ink,
        alignment=TA_JUSTIFY, spaceAfter=6)
    add("Twin", fontName=SERIF, fontSize=9.4, leading=14.4, textColor=c_ink,
        alignment=TA_JUSTIFY, spaceAfter=5, leftIndent=13, rightIndent=13)
    add("BL", fontName=SANS, fontSize=8.2, leading=11.8, textColor=c_grey_d,
        leftIndent=14, bulletIndent=4, spaceAfter=2.6, alignment=TA_JUSTIFY)
    add("Note", fontName=SANS, fontSize=7.2, leading=9.8, textColor=c_grey,
        alignment=TA_JUSTIFY, spaceAfter=4)
    add("Cap", fontName=SANS, fontSize=6.8, leading=9.2, textColor=c_grey,
        spaceBefore=2, spaceAfter=7)

    add("Q", fontName=SERIF, fontSize=8.8, leading=13.2, textColor=c_ink,
        leftIndent=15, rightIndent=15, spaceBefore=3, spaceAfter=3,
        alignment=TA_JUSTIFY)
    add("QAttr", fontName=SANS, fontSize=6.9, leading=9.4, textColor=c_grey,
        leftIndent=15, spaceAfter=8)

    add("Th", fontName=SANS_B, fontSize=6.9, leading=9, textColor=colors.white)
    add("Td", fontName=SANS, fontSize=6.9, leading=9.2, textColor=c_grey_d)
    add("TdB", fontName=SANS_B, fontSize=6.9, leading=9.2, textColor=c_ink)
    add("TdM", fontName=MONO, fontSize=6.2, leading=8.4, textColor=c_grey_d)
    add("TdSer", fontName=SERIF, fontSize=7.2, leading=9.8, textColor=c_ink)
    add("TdGrey", fontName=SANS, fontSize=6.6, leading=8.8, textColor=c_grey)

    add("Banner", fontName=SANS_B, fontSize=8.2, leading=11, textColor=colors.white)
    add("BannerM", fontName=MONO, fontSize=6.4, leading=8.6, textColor=colors.white)
    return s


S = build_styles()
PW = letter[0] - 80  # printable width at 40pt margins


def P(t, st="Body"):
    return Paragraph(t, S[st])


def bullets(items, st="BL", mark="\u2013"):
    return [Paragraph(t, S[st], bulletText=mark) for t in items]


def rule(w=PW, thick=0.6, colour=c_rule, before=3, after=6):
    return HRFlowable(width=w, thickness=thick, color=colour,
                      spaceBefore=before, spaceAfter=after)


def banner(title, meta=None, colour=c_ink):
    rows = [[Paragraph(title, S["Banner"])]]
    if meta:
        rows.append([Paragraph(meta, S["BannerM"])])
    t = Table(rows, colWidths=[PW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colours_hex(colour)),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def colours_hex(h):
    return h if isinstance(h, colors.Color) else colors.HexColor(h)


def dtable(data, widths, header=True, hdr_bg=c_ink, zebra=True,
           font_pad=3.4, align_right=(), grid=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), font_pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), font_pad),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), hdr_bg),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, c_ink),
        ]
    if grid:
        cmds += [("INNERGRID", (0, 0), (-1, -1), 0.25, c_rule),
                 ("BOX", (0, 0), (-1, -1), 0.5, c_rule)]
    if zebra:
        for i in range(1 if header else 0, len(data)):
            if (i % 2) == (0 if header else 1):
                cmds.append(("BACKGROUND", (0, i), (-1, i), c_wash))
    for c in align_right:
        cmds.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(cmds))
    return t


def callout(title, paras, colour=c_accent, tint=None):
    inner = [Paragraph(title, ParagraphStyle(
        "cot", fontName=SANS_B, fontSize=7.6, leading=10, textColor=colours_hex(colour)))]
    inner.append(Spacer(1, 3))
    for i, x in enumerate(paras):
        inner.append(Paragraph(x, ParagraphStyle(
            "cob%d" % i, fontName=SANS, fontSize=7.8, leading=11,
            textColor=c_grey_d, alignment=TA_JUSTIFY)))
        if i < len(paras) - 1:
            inner.append(Spacer(1, 3))
    t = Table([[inner]], colWidths=[PW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colours_hex(tint) if tint else c_wash),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, colours_hex(colour)),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def _TP(t, st):
    """Paragraph constructor that resolves the {M} mono-font token.

    `st` may be a style name or a ParagraphStyle, since the Tuesday table passes
    style objects directly.
    """
    return Paragraph(t.replace("{M}", MONO), st if not isinstance(st, str) else S[st])


def part(title, sub=None):
    out = [Spacer(1, 4), Paragraph(title, S["Part"])]
    if sub:
        out.append(Paragraph(sub, S["PartSub"]))
    out.append(rule(thick=1.1, colour=c_ink, before=2, after=8))
    return out


# ===========================================================================
# BUILD
# ===========================================================================
def build():
    doc = SimpleDocTemplate(
        OUT, pagesize=letter, leftMargin=40, rightMargin=40,
        topMargin=50, bottomMargin=56,
        title="The Uncreated Twin \u2014 A Biography in Nine Absences",
        author="Zaziopath \u00b7 Stratum Nine (Unfiled)",
        subject="Reconstruction of the version of the subject who did not archive",
        keywords="Zaziopath; ZP-UNFILED-0000; reconstruction; gap audit",
    )
    F = []
    A = F.append

    # ------------------------------------------------------------------
    # TITLE PAGE
    # ------------------------------------------------------------------
    A(Spacer(1, 26))
    A(OpenCircle(r=13, lw=1.4))
    A(Spacer(1, 16))
    A(P("Z A Z I O P A T H &nbsp;&nbsp;\u00b7&nbsp;&nbsp; S T R A T U M &nbsp;N I N E &nbsp;&nbsp;\u00b7&nbsp;&nbsp; U N F I L E D", "T_Kicker"))
    A(P("THE UNCREATED<br/>TWIN", "T_Title"))
    A(Spacer(1, 2))
    A(P("A biography of the version who did not archive, did not mythologize,<br/>"
        "did not seek interpretation, and lived entirely outside the system.", "T_Sub"))
    A(Spacer(1, 12))
    A(rule(w=PW * 0.42, thick=0.7, before=0, after=12))
    A(P("Reconstructed from the acquisition gaps of the Zaziopath vault, 2006\u20132026.", "T_SubSub"))
    A(Spacer(1, 14))

    ident = [
        [Paragraph("DESIGNATION", S["TdGrey"]), Paragraph("ZP-UNFILED-0000", S["TdB"])],
        [Paragraph("STATUS", S["TdGrey"]), Paragraph("Living. Never filed. Never lost \u2014 merely unrecorded.", S["Td"])],
        [Paragraph("BORN", S["TdGrey"]), Paragraph("2006, Asheville, North Carolina \u2014 the same year, the same town, the same name as the subject of this vault.", S["Td"])],
        [Paragraph("WORKS", S["TdGrey"]), Paragraph("None released. None titled. None registered.", S["Td"])],
        [Paragraph("ARCHIVE", S["TdGrey"]), Paragraph("Zero bytes.", S["Td"])],
        [Paragraph("SOURCE OF THIS LIFE", S["TdGrey"]), Paragraph("The eight categories of material <font name='%s'>DEEP_GAP_AUDIT.md</font> \u00a711.1 states the vault is least likely to preserve." % SANS, S["Td"])],
        [Paragraph("EVIDENCE CLASS", S["TdGrey"]), Paragraph("Reconstruction. Not <font name='%s'>direct_evidence</font>, not <font name='%s'>self_report</font>, not <font name='%s'>public_record</font>. See Appendix B." % (MONO, MONO, MONO), S["Td"])],
        [Paragraph("COMPILED", S["TdGrey"]), Paragraph("2026-09-27", S["Td"])],
    ]
    A(dtable(ident, [PW * 0.24, PW * 0.76], header=False, zebra=False,
             grid=False, font_pad=3.0))
    A(Spacer(1, 16))
    A(callout(
        "THE SOURCE LIST \u2014 THIS BIOGRAPHY IS MADE OF EXACTLY THIS",
        ["<font name='%s'>DEEP_GAP_AUDIT.md</font> \u00a711.1, \u201cGap Nine: Archival Selection Bias\u201d, "
         "lists what the vault preferentially preserves and then what it does not. The second list has eight items: "
         "<b>uneventful days \u00b7 routine maintenance \u00b7 embodied experience \u00b7 unrecorded conversations \u00b7 "
         "failed ideas too boring to mythologize \u00b7 ordinary affection \u00b7 unremarkable competence \u00b7 actions "
         "whose privacy is more important than their legibility.</b>" % SANS,
         "The vault wrote that list about itself, in its own hand, on 2026-09-23, and filed it under "
         "\u201cthings the archive systematically fails to capture.\u201d Those eight failures are not holes in a life. "
         "They are a life. This document is the biography of the person they add up to."],
        colour=c_accent))
    A(Spacer(1, 10))
    A(P("\u201cThe archive does not merely describe a self. It samples a self through an "
        "acquisition policy.\u201d \u2014 <font name='%s'>DEEP_GAP_AUDIT.md</font> \u00a711.2" % SANS, "T_Mono"))
    A(PageBreak())

    # ------------------------------------------------------------------
    # COLOPHON
    # ------------------------------------------------------------------
    A(P("COLOPHON AND PROVENANCE", "Part"))
    A(rule(thick=1.0, colour=c_ink, after=8))

    A(P("This is a reconstruction, not a record.", "Lead"))
    A(P(
        "Zaziopath contains no evidence of a second person. There is no second birth certificate, "
        "no second catalogue, no second set of field recordings, no witness who can place two people "
        "in the same room. There is one subject, born 2006, in Asheville, North Carolina, whose name "
        "appears on a CV, a residency dossier, a discography of 182 catalogued rows, and 102 files at "
        "the root of a repository."))
    A(P(
        "What the archive does contain, in unusual quantity and in its own words, is a precise "
        "account of what it cannot hold. <font name='%s'>DEEP_GAP_AUDIT.md</font> \u2014 a 50 KB "
        "self-audit the vault commissioned against itself \u2014 names eight categories of human "
        "material that never become artifacts. It names them without flinching and then files the "
        "list. That list is a negative mould. Pour a person into it and you get the outline of "
        "somebody: the one who had the uneventful days, did the maintenance, kept the conversations "
        "unrecorded, and let the boring failures stay boring." % SANS))
    A(P(
        "That somebody is the uncreated twin. He is not a sibling and not a metaphor for a mood. He "
        "is the counterfactual of the archivist: identical at the origin, divergent from the first "
        "decision onward. Where the subject turned an experience into an artifact, the twin had the "
        "experience. Where the subject titled a thing, the twin left it unnamed. Where the subject "
        "asked what a pattern <i>meant</i>, the twin went outside."))

    A(Spacer(1, 4))
    A(P("The rule of this biography", "H3"))
    A(P(
        "The vault's governing discipline is that a claim does not become evidence because it is "
        "dated, linked, diagrammed, repeated, or written in forensic language "
        "(<font name='%s'>EVIDENCE_GOVERNANCE_HANDBOOK.md</font> \u00a71). This document holds itself "
        "to that rule and therefore states its own condition plainly:" % SANS))
    A(Spacer(1, 2))
    A(dtable([
        [Paragraph("KIND OF STATEMENT", S["Th"]), Paragraph("HOW IT IS MARKED", S["Th"]), Paragraph("WHAT IT RESTS ON", S["Th"])],
        [Paragraph("A fact about the catalogue, the repository, or the CV", S["Td"]),
         Paragraph("<font name='%s'>recomputed</font>" % MONO, S["Td"]),
         Paragraph("Recomputed from the committed files at build time. Method in Appendix C. Falsifiable.", S["Td"])],
        [Paragraph("A quotation from the vault", S["Td"]),
         Paragraph("<font name='%s'>quoted</font>" % MONO, S["Td"]),
         Paragraph("Verbatim, with the file named. Falsifiable.", S["Td"])],
        [Paragraph("A statement about the twin", S["Td"]),
         Paragraph("<font name='%s'>reconstructed</font>" % MONO, S["Td"]),
         Paragraph("Inference from an acquisition gap. Not evidence about a person. Carries a gap code G-01\u2026G-09.", S["Td"])],
    ], [PW * 0.30, PW * 0.16, PW * 0.54]))
    A(P("Every passage of reconstruction in this document carries a gap code from Appendix A, so a "
        "reader can always see which failure of the archive it was poured from. Where a "
        "reconstruction is load-bearing for the accusation in Part V, the underlying verified number "
        "is printed beside it.", "Cap"))

    A(Spacer(1, 2))
    A(P("Authorship footer", "H3"))
    A(P("Required for every interpretive artifact by <font name='%s'>DEEP_GAP_AUDIT.md</font> \u00a79.2." % SANS, "Note"))
    A(dtable([
        [Paragraph("<font name='%s'>authorship:</font>" % MONO, S["TdM"]), Paragraph("", S["Td"])],
        [Paragraph("&nbsp;&nbsp;human_author:", S["TdM"]), Paragraph("withheld \u2014 see Appendix D", S["Td"])],
        [Paragraph("&nbsp;&nbsp;ai_role:", S["TdM"]), Paragraph("generation, analysis, drafting", S["Td"])],
        [Paragraph("&nbsp;&nbsp;model_provider:", S["TdM"]), Paragraph("unknown", S["Td"])],
        [Paragraph("&nbsp;&nbsp;model_name:", S["TdM"]), Paragraph("unknown", S["Td"])],
        [Paragraph("&nbsp;&nbsp;generated_at:", S["TdM"]), Paragraph("2026-09-27", S["Td"])],
        [Paragraph("&nbsp;&nbsp;prompt_retained:", S["TdM"]), Paragraph("true", S["Td"])],
        [Paragraph("&nbsp;&nbsp;human_edits:", S["TdM"]), Paragraph("unknown", S["Td"])],
        [Paragraph("&nbsp;&nbsp;factual_review:", S["TdM"]), Paragraph("complete for <font name='%s'>recomputed</font> claims; none possible for <font name='%s'>reconstructed</font> ones" % (MONO, MONO), S["Td"])],
        [Paragraph("&nbsp;&nbsp;source_material_commit:", S["TdM"]), Paragraph("65fb5d9 (branch point of this working branch)", S["Td"])],
        [Paragraph("&nbsp;&nbsp;correction_state:", S["TdM"]), Paragraph("<font name='%s'>fictional</font> as to the twin; <font name='%s'>active</font> as to the catalogue" % (MONO, MONO), S["Td"])],
    ], [PW * 0.30, PW * 0.70], header=False, zebra=False, font_pad=1.9))

    A(Spacer(1, 8))
    A(callout("REDACTION NOTICE \u2014 READ BEFORE PART I",
              ["The residency dossier at the root of this repository prints a home street address, a "
               "telephone number, and a personal e-mail address in plain text on its final page. "
               "<b>None of that is reproduced here.</b> The twin's address, phone, and e-mail are "
               "withheld throughout, and so is the name he is called by the people who love him. "
               "This is not squeamishness. It is the twin's own eighth principle \u2014 that some "
               "actions are more important for being private than for being legible \u2014 applied to "
               "the one document about him that the archive will keep. Full statement in Appendix D."],
              colour=c_specimen, tint=colors.HexColor("#FBF1EC")))
    A(PageBreak())

    # ------------------------------------------------------------------
    # PART I
    # ------------------------------------------------------------------
    A(P("PART I \u00b7 THE PERSON", "Part"))
    A(P("Four sections on the one thing both twins share and the one moment they do not.", "PartSub"))

    A(P("\u00a71 &nbsp;The name", "H2"))
    A(P(
        "His name is the same name. That is the whole scandal of this document, and it is worth "
        "stating before anything else, because the archive has spent 9.74 MB making that name into a "
        "label and the twin has spent twenty years using it as a name.", "Lead"))
    A(P(
        "A name is what someone says across a house to get you to come to the kitchen. A label is "
        "what a filing system says to sort you. The subject of this vault has both, and the vault is "
        "the record of the label winning. It appears on a CV as a heading in letter-spaced capitals. "
        "It appears as the registered name of a limited liability company. It appears as an Instagram "
        "handle, a Bandcamp handle, a domain, a GitHub organisation, a Discogs artist number, a label "
        "he founded, and the artist field of 178 of the 182 rows in his own discography."))
    A(P(
        "The twin has never been a label. He has a name, and it is used on him the way names are "
        "used: to be called. When somebody in the house says it, he gets up. Nothing is filed. No "
        "artifact results. There is no <font name='%s'>ZP-</font> identifier for being called to "
        "dinner, and every identifier in this vault begins at <font name='%s'>0001</font>; there is "
        "no <font name='%s'>-0000</font> anywhere in it. This document occupies the slot the "
        "numbering system reserves and never uses." % (MONO, MONO, MONO)))

    A(Spacer(1, 4))
    A(P("\u00a72 &nbsp;The birth both twins share", "H2"))
    A(P(
        "Every reconstruction needs an anchor that is not itself reconstructed. This one is."))
    A(dtable([
        [Paragraph("FIELD", S["Th"]), Paragraph("VALUE", S["Th"]), Paragraph("SOURCE", S["Th"])],
        [Paragraph("Birth year", S["Td"]), Paragraph("2006", S["TdB"]), Paragraph("Residency dossier, biography page: \u201cZazie Kanwar-Torge (b. 2006)\u201d", S["Td"])],
        [Paragraph("Place", S["Td"]), Paragraph("Asheville, North Carolina (ZIP 28806)", S["TdB"]), Paragraph("Residency dossier, applicant identity block", S["Td"])],
        [Paragraph("Schooling", S["Td"]), Paragraph("Homeschooled, within the experimental pedagogical lineage of Black Mountain College", S["TdB"]), Paragraph("Residency dossier, biography page", S["Td"])],
        [Paragraph("First commission", S["Td"]), Paragraph("Age 14. <i>Cheaper Impressions</i> \u2014 Erik Satie's <i>Gymnop\u00e9die No. 1</i> through musique concr\u00e8te, for the BMC Radio Art Series; broadcast with an artist interview and a listening session", S["TdB"]), Paragraph("Artist CV, 2021 entry", S["Td"])],
        [Paragraph("First catalogue row", S["Td"]), Paragraph("2019-09-09", S["TdB"]), Paragraph("Discography CSV, row 2", S["Td"])],
    ], [PW * 0.17, PW * 0.45, PW * 0.38]))
    A(P(
        "So the twin was homeschooled too. He is sitting in the same house in the same town, reading "
        "the same books off the same shelves, in a pedagogy built around self-direction. He is "
        "fourteen in 2020 and nineteen in 2026, exactly like the other one. The commission is where "
        "the two lives first become distinguishable, and it is worth being exact about why.", "Note"))

    A(Spacer(1, 4))
    A(P("\u00a73 &nbsp;The fork: 9 September 2019", "H2"))
    A(P(
        "The subject's discography opens on 2019-09-09 with an EP called <i>Stutter to stammer</i>. "
        "Five tracks. The vault's own Pattern Atlas labels this row \u201cno codes, just work.\u201d "
        "That phrase is the closest the archive ever comes to describing the twin, and it describes "
        "him for exactly one release."))
    A(P(
        "The divergence is not that one of them made music and the other did not. Both of them made "
        "music; they are the same person with the same ears and the same hands. The divergence is "
        "that one of them, on that date, put a thing into a system that would keep it, index it, "
        "date it, code it, and later reissue it, and the other one made a thing and let it be over."))
    A(Spacer(1, 2))
    A(dtable([
        [Paragraph("", S["Th"]), Paragraph("THE ARCHIVIST", S["Th"]), Paragraph("THE TWIN", S["Th"])],
        [Paragraph("On 2019-09-09", S["TdB"]), Paragraph("Released a five-track EP.", S["Td"]), Paragraph("Finished a piece. Turned the machine off.", S["Td"])],
        [Paragraph("By 2022", S["TdB"]), Paragraph("23 catalogue rows. The 2019\u201320 recordings are retroactively assigned ISRCs in a single registration sweep.", S["Td"]), Paragraph("Still no catalogue. Nothing to sweep.", S["Td"])],
        [Paragraph("By 2024", S["TdB"]), Paragraph("60 rows in one year \u2014 the catalogue's peak. <i>Stutter to stammer</i> returns as a Super Deluxe Edition: 32 tracks, 6.4\u00d7 the original.", S["Td"]), Paragraph("The 2019 piece is gone. He is not troubled by this and cannot explain why that is a position.", S["Td"])],
        [Paragraph("By 2026", S["TdB"]), Paragraph("182 rows. 21 releases. 7 h 29 m 27 s of released audio. A 222-page compendium about himself. A CV. A residency dossier.", S["Td"]), Paragraph("No rows. No releases. No compendium. He has heard almost none of it and has no opinion about the compendium.", S["Td"])],
    ], [PW * 0.16, PW * 0.42, PW * 0.42]))
    A(P(
        "Note what the 2022 column contains. Thirteen of the 161 ISRC-coded rows in the catalogue "
        "carry a registration year later than their release year \u2014 the vault's own finding F-01, "
        "which its Pattern Atlas summarises in five words: <b>after every silence, a "
        "notarization.</b> The archivist cannot let a quiet period be quiet. The twin has never had "
        "anything to notarize, because he has never made a silence into a period."))

    A(Spacer(1, 4))
    A(P("\u00a74 &nbsp;What he looks like", "H2"))
    A(P(
        "Finding F-09 of the Instagram forensic audit is titled \u201cTotal anonymity \u2014 no face, "
        "no personal name.\u201d Across 14 examined grid posts, 8 tagged items, and 8 public comments, "
        "the public surface of Zazie Productions contains no face. The audit was retrieved 2026-08-19 "
        "from a logged-out view of the account and reports this as a finding, in the register of a "
        "risk."))
    A(P(
        "The twin has a face. It is unremarkable. It is in a hallway mirror and in the memory of "
        "everybody who has ever stood in a kitchen with him, and it is in no audit, because an audit "
        "requires a surface and he has never offered one. He is not hiding. Hiding is a posture "
        "toward an observer, and he has no observer. The difference matters: anonymity is something "
        "you maintain; being unremarked is something that simply happens when you do not perform."))
    A(Spacer(1, 2))
    A(callout("THE PORTRAIT",
              ["The archive is a portrait with the face cut out and the nervous system mounted "
               "instead. It contains 165,218 words of interior life at the repository root \u2014 "
               "typology, tritype, instinctual stack, attitudinal psyche, socionics, Jungian "
               "archetype, Freudian character style, twenty-odd personality instruments \u2014 and no "
               "photograph of a person. The twin inverts it exactly: no interior on record, and a "
               "face that has been seen by everyone who matters to him and by no auditor at all."],
              colour=c_identity))
    A(CondPageBreak(260))

    # ------------------------------------------------------------------
    # PART II
    # ------------------------------------------------------------------
    A(P("PART II \u00b7 DAILY LIFE", "Part"))
    A(P("The eight absences, reconstructed one at a time, preceded by the day they add up to.", "PartSub"))

    A(P(
        "The vault's third stage is called Stewardship and its question is not interpretive. It is "
        "<b>What do I do on Tuesday?</b> That is the vault's own formulation, printed in README \u00a701 "
        "and again in \u00a708. It is the most ordinary question in the archive and the only one the "
        "twin can answer without a gap code, because the twin's entire life is a Tuesday.", "Lead"))
    A(P(
        "So begin there. What follows is a reconstruction of one Tuesday, hour by hour, with the "
        "archive's Tuesday beside it. The left column is invented. The right column is not: it is "
        "the vault's own Tuesday, which consists of running twelve questions against a message you "
        "were about to send, writing one sentence of behavioural change, dating it, and filing it in "
        "a local HTML console that stores the entry in your browser's localStorage."))

    A(Spacer(1, 4))
    A(P("\u00a75 &nbsp;A reconstructed Tuesday", "H2"))
    tuesday = [
        [_TP("HOUR", S["Th"]), _TP("THE TWIN", S["Th"]), _TP("THE ARCHIVE'S TUESDAY", S["Th"])],
        [_TP("06:40", S["TdB"]),
         _TP("Wakes because the light is in the room. The phone is across the room and stays across the room for another hour.", S["TdSer"]),
         _TP("The phone is the first instrument. It is checked before the eyes are open. No artifact results from this either, and the archive does not know it happens.", S["Td"])],
        [_TP("06:55", S["TdB"]),
         _TP("Coffee in a cup with a chip in the rim. He has not thought about the chip in four years. It is not a symbol.", S["TdSer"]),
         _TP("<font name='{M}'>G-03</font> embodied experience. A chipped cup would have to mean something to survive contact with the vault.", S["Td"])],
        [_TP("07:40", S["TdB"]),
         _TP("Drives. Knows which curve out past the ridge holds water in March, and takes it differently in March, and has never once said this out loud.", S["TdSer"]),
         _TP("<font name='{M}'>G-03</font>. Unnarrated competence in a body. The vault has a wire for \u201cdecay studies aestheticize entropy as the medium\u201d and nothing for knowing a wet curve.", S["Td"])],
        [_TP("08:15", S["TdB"]),
         _TP("Opens the shop. Bench, iron, flux, a queue of other people's broken things. Headphones, a receiver from 1978, a turntable whose owner is worried about the cost.", S["TdSer"]),
         _TP("<font name='{M}'>G-02</font> routine maintenance. Explicitly named by the gap audit as material the vault does not preserve.", S["Td"])],
        [_TP("09:50", S["TdB"]),
         _TP("Tells the man with the receiver it will be fine and does not charge him for the twenty minutes it took to find out.", S["TdSer"]),
         _TP("<font name='{M}'>G-07</font> unremarkable competence. No receipt. Nothing to file. The vault has an entire stratum for receipts.", S["Td"])],
        [_TP("12:10", S["TdB"]),
         _TP("Lunch standing up. Talks to the person at the next bench about nothing \u2014 a dog, a road closure, whether it will rain. Both of them forget the conversation by Thursday.", S["TdSer"]),
         _TP("<font name='{M}'>G-04</font> unrecorded conversation. The vault's Deep Gap Audit lists this as a category of loss and does not notice it is also a category of wealth.", S["Td"])],
        [_TP("13:30", S["TdB"]),
         _TP("Sets up a microphone at the pond behind the house because the water sounded like something. Records forty minutes. Names the file with the date. Names nothing else.", S["TdSer"]),
         _TP("The archivist records the same pond and titles it \u201cR09 Recording Water Pond Collage.\u201d The title is the first act of filing and it happens before the listening does.", S["Td"])],
        [_TP("15:00", S["TdB"]),
         _TP("An idea for a piece arrives, is good, and is not written down. It is gone by the time he locks the shop. He does not chase it. He has never chased one.", S["TdSer"]),
         _TP("<font name='{M}'>G-05</font>. The vault's own entry rite demands you name \u201cthe project that refuses to die\u201d and dig it out of a folder called <font name='{M}'>draft_final_final2_THISONEignore</font>. The twin has no such folder. Nothing refused to die.", S["Td"])],
        [_TP("17:45", S["TdB"]),
         _TP("Cooks. Someone else sets the table without being asked and neither of them mentions it.", S["TdSer"]),
         _TP("<font name='{M}'>G-06</font> ordinary affection. The vault can name 250 archetypes and cannot describe this.", S["Td"])],
        [_TP("20:30", S["TdB"]),
         _TP("Listens to a record he will never cite in anything, because there is no anything. Falls asleep partway through side two.", S["TdSer"]),
         _TP("The vault's influences are listed on a CV. The twin's influences are unlisted because listing is a genre and he is not in one.", S["Td"])],
        [_TP("22:15", S["TdB"]),
         _TP("Goes to bed. The day produces zero bytes. This is the eleventh thousand such day of his life and he has not once thought of it as a streak.", S["TdSer"]),
         _TP("Runs question 2 of the twelve: <i>after all the complexity is acknowledged, what simple sentence about my behaviour remains true?</i> Writes the sentence. Files it in localStorage. It is deleted the next time the browser cache is cleared.", S["Td"])],
    ]
    A(dtable(tuesday, [PW * 0.075, PW * 0.455, PW * 0.47], font_pad=3.0))
    A(P("Table 1. One Tuesday, reconstructed (left) against the vault's own prescribed Tuesday "
        "(right, per README \u00a708 and \u00a709). The left column is <font name='%s'>reconstructed</font>; "
        "the right is <font name='%s'>quoted</font> or <font name='%s'>recomputed</font>. Gap codes "
        "refer to Appendix A." % (MONO, MONO, MONO), "Cap"))

    A(callout("THE ARITHMETIC OF THE RIGHT COLUMN",
              ["The vault's eight strata have the following masses, recomputed here from the "
               "committed files using the vault's own stratum classification in "
               "<font name='%s'>tools/generate_figures.py</font>: identity 3,763.2 KB (10 files), "
               "mythography 1,841.4 KB (20), shadow 1,406.8 KB (4), recursion 582.2 KB (7), evidence "
               "331.8 KB (5), specimens 144.9 KB (4), index 128.7 KB (8) \u2014 and "
               "<b>stewardship, the stage the alchemy is supposed to end in, 5.1 KB across 2 "
               "files.</b>" % SANS,
               "Identity instruments alone outweigh the answer to \u201cwhat do I do on Tuesday?\u201d by "
               "<b>741 to 1</b>. All seven other strata combined outweigh it by <b>1,615 to 1</b>. "
               "The twin's Tuesday weighs nothing and answers the question completely."],
              colour=c_steward))

    # ---- the eight absences ----
    A(P("\u00a76\u2013\u00a713 &nbsp;The eight absences", "H2"))
    A(P(
        "Each of the eight categories the vault says it cannot hold gets a section. Each is "
        "reconstructed from the same negative mould and each carries its gap code. Together they are "
        "not a list of lacks. They are the eight load-bearing walls of a life that never needed "
        "documentation to stand up."))

    eight = [
        ("G-01", "Uneventful days",
         "The archivist has 21 release dates across 8 years. Ten of the 21 fall in March, April, or "
         "May; three more cluster in December. Between them, ordinary time. The vault's Pattern Atlas "
         "turns that distribution into a finding called \u201cthe Winter Ritual\u201d and gives it a "
         "polar chart.",
         "The twin has no release dates, so he has no intervals, so he has no rituals. He has "
         "approximately 7,300 days and they are the same shape. Some of them are good. Two or three "
         "of them, he would tell you if you asked him on the right evening, changed him. None of "
         "them has a chart. The archive cannot preserve an uneventful day and so cannot preserve the "
         "fact that uneventful days are the substrate everything else grows in \u2014 including, in the "
         "archivist's case, the 182 rows."),
        ("G-02", "Routine maintenance",
         "The vault maintains itself: 102 files at the root, 9.74 MB, a figures directory, a "
         "verification JSON, four generator scripts, a receipt console, a colour system with eight "
         "hex codes, a mermaid map with seventeen indexed wires. All of that is maintenance, and all "
         "of it is <i>about</i> maintenance.",
         "The twin maintains a bench, a car, a set of keys, a kettle, a relationship, and a body. He "
         "does it daily, badly in patches, and without ever producing a document about it. The "
         "difference is not effort \u2014 the vault's upkeep is real work. The difference is that his "
         "maintenance ends in a working thing and the archive's ends in more archive."),
        ("G-03", "Embodied experience",
         "The subject's practice is explicitly about listening: binaural technique, spatial audio, a "
         "20.4-channel loudspeaker system at Ars Electronica in 2026, a workshop at CCRMA on virtual "
         "acoustics. All of it is hearing rendered as architecture.",
         "The twin hears the same things in a body that has not been asked to describe them. Cold "
         "water on the wrist. The particular silence after a car door. Tinnitus in one ear on bad "
         "days. A shoulder that aches before rain and is never once correlated with anything. His "
         "hearing has never been an instrument; it is just the way he is present in a room."),
        ("G-04", "Unrecorded conversations",
         "The Deep Gap Audit's own verdict-sample table concedes a finding that the repository "
         "\u201ccontains no fully represented other people,\u201d graded <font name='%s'>moderate as "
         "archive description; weak as life claim</font>. That grading is honest and it is also the "
         "saddest line in the vault: the archive cannot tell whether the absence of other people is a "
         "property of the record or of the life." % MONO,
         "The twin settles the ambiguity from the other side. He talks to people constantly and none "
         "of it survives. Arguments resolved badly and then better. A long phone call about somebody "
         "else's mother. Jokes that only work once and are therefore perfect. The archive loses all "
         "of this. The twin loses it too, and is fine, because the losing was never the point \u2014 "
         "the having was."),
        ("G-05", "Failed ideas too boring to mythologize",
         "The vault publishes <i>Lost Zazie Productions Archive</i>, a two-page catalogue of nine "
         "lost works. Every one of them is magnificent. A reversed seventh iteration of a piano piece "
         "whose spectrogram encodes Morse code reading \u201cZAZIE IS ASLEEP IN THE CLEFT.\u201d A glitchscape "
         "recoverable only from RAM image logs on a defunct forum. An eighteen-minute drone recorded "
         "in a chapel through ceramic bones, abandoned because it was \u201ctoo clean. Too reverent.\u201d",
         "The twin's failures are not magnificent and that is why nobody will ever recover them. A "
         "loop that did not work. A recording ruined because somebody's chair scraped. A piece he "
         "abandoned at minute two because he could hear it was going to be bad. No RAR archive, no "
         "Morse, no bootleg CDr in a Durham bookstore. Part III sets the two catalogues side by side."),
        ("G-06", "Ordinary affection",
         "Affection appears in the vault as material. It appears in a mythographic childhood in which "
         "a mother calls her son \u201cher little revenant\u201d and \u201cI don't think she meant it "
         "sweetly.\u201d It appears in a lost tape composed for a friend in hospice, documented by a "
         "single Polaroid of a TASCAM unit labelled \u201cMIRABEL-FEB99.\u201d",
         "The twin's affection is not material. Somebody puts a hand on the back of his neck as they "
         "pass. He is there when it is bad and does not make it mean anything. He is loved in a way "
         "that generates no artifact, no legend, no Polaroid, and no finding. Part IV takes this up "
         "at length, because it is where the accusation begins."),
        ("G-07", "Unremarkable competence",
         "The vault's competence is exceptional and documented: a commissioned composer at fourteen, "
         "a label founder who curated a 105-track compilation, four open-source instruments, two "
         "published sound libraries, one of them 200+ body-horror effects. All of it verified, all of "
         "it on a CV.",
         "The twin is extremely good at three things nobody would put on a CV. He can find a fault in "
         "a signal path by ear. He can make a frightened person calm. He can cook four meals well. He "
         "has been doing all three for a decade and has never once been credited, because credit is a "
         "filing operation and he does not file."),
        ("G-08", "Actions whose privacy is more important than their legibility",
         "This is the category the vault names last and it is the one that governs this document. The "
         "Deep Gap Audit's own privacy section warns that the repository aggregates legal identity, "
         "city, company, catalogue, psychological self-description, pricing vulnerability, and AI "
         "memory summaries into one place, and that the combination \u201clowers the work required to "
         "create a convincing targeted approach.\u201d",
         "The twin has nothing to aggregate. He has never published a price, a diagnosis, a typology, "
         "or an interior. If a stranger found everything he had ever made, they would find a folder "
         "of date-named audio files and nothing to build a spear from. This document withholds his "
         "address, his telephone, his e-mail, and the name he is called at home, for exactly this "
         "reason \u2014 and in doing so it commits the twin's only unforgivable act: it makes him "
         "legible. He would object. His objection is recorded here and overruled, and Part V will "
         "treat that as a charge against the biographer as well as the archive."),
    ]
    for code, title, archiv, twin in eight:
        inner = Table([
            [Paragraph("IN THE ARCHIVE", ParagraphStyle(
                "x1", fontName=SANS_B, fontSize=6.4, leading=8.4, textColor=c_evidence)),
             Paragraph(archiv, ParagraphStyle(
                 "x2", fontName=SANS, fontSize=7.5, leading=10.4,
                 textColor=c_grey_d, alignment=TA_JUSTIFY))],
            [Paragraph("IN THE TWIN", ParagraphStyle(
                "x3", fontName=SANS_B, fontSize=6.4, leading=8.4, textColor=c_accent)),
             Paragraph(twin, ParagraphStyle(
                 "x4", fontName=SERIF, fontSize=7.9, leading=11.4,
                 textColor=c_ink, alignment=TA_JUSTIFY))],
        ], colWidths=[PW * 0.13, PW * 0.87])
        inner.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBEFORE", (0, 0), (0, -1), 2.0, c_accent),
            ("BACKGROUND", (0, 0), (0, -1), c_wash),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, c_rule),
            ("BOX", (0, 0), (-1, -1), 0.5, c_rule),
        ]))
        A(KeepTogether([
            Paragraph("%s &nbsp;<font color='%s'>\u25a0</font>&nbsp; %s" % (code, INK, title), S["H3"]),
            inner,
            Spacer(1, 7),
        ]))

    A(Spacer(1, 4))
    A(P("\u00a714 &nbsp;The ninth absence: the archive itself", "H2"))
    A(P(
        "The gap audit's list has eight items. The ninth absence is the one the list cannot contain, "
        "because a list is an artifact and the ninth absence is the absence of artifact-making. It "
        "has no gap code in the source and gets one here: <font name='%s'>G-09</font>." % MONO, "Lead"))
    A(P(
        "The twin does not have an archive. He does not have a colour code, a glyph, a stratum, a "
        "mermaid map, a wire register, a claim ledger, a receipt console, a case file, a pattern "
        "atlas, seven generated figures, or a one-line version of himself. He has never run an "
        "adversarial tribunal against himself, never asked a machine what he was hiding, never "
        "assigned a model a jurisdiction and evidentiary rules."))
    A(P(
        "He is not thereby simpler. He is a person of the same intelligence and the same appetites, "
        "carrying the same contradictions, who has never converted any of it into a system. The "
        "contradictions do not resolve. They just get lived. On a bad week he is petty and "
        "competitive and wants to be told he is extraordinary, exactly like the other one \u2014 and "
        "then the week ends and there is no finding."))
    A(Spacer(1, 2))
    A(callout("WHY THE NINTH ABSENCE IS THE ONLY ONE THAT MATTERS",
              ["The first eight absences are things the archive fails to preserve. The ninth is the "
               "reason it fails. An acquisition policy is not a list of omissions; it is a "
               "disposition. The vault prefers material that is text-rich, unusual, categorizable, "
               "aesthetically intense, self-generated, model-readable, publicly verifiable, or "
               "compatible with its themes \u2014 those are the audit's own eight criteria for what "
               "becomes an artifact.",
               "A person who satisfies none of those criteria is not poorly documented. A person who "
               "satisfies none of those criteria <b>is the twin</b>."],
              colour=c_accent))
    A(CondPageBreak(260))

    # ------------------------------------------------------------------
    # PART III
    # ------------------------------------------------------------------
    A(P("PART III \u00b7 THE LOST WORKS", "Part"))
    A(P("Two catalogues of loss, set side by side. One of them has legends. One of them has nothing.", "PartSub"))

    A(P("\u00a715 &nbsp;The mythologised nine", "H2"))
    A(P(
        "The vault publishes a document called <i>Lost Zazie Productions Archive</i>. It catalogues "
        "nine works that never came out. Here is what the archive's idea of a lost work looks like, "
        "verbatim in its apparatus:", "Lead"))
    A(dtable([
        [Paragraph("#", S["Th"]), Paragraph("LOST WORK", S["Th"]), Paragraph("HOW THE ARCHIVE DOCUMENTS ITS LOSS", S["Th"])],
        [Paragraph("1", S["TdB"]), Paragraph("Pineal Cleft (Ver. -7)", S["TdB"]), Paragraph("Seventh reversed iteration of an unreleased piano piece. Electrode-modulated felt piano, custom Max/MSP patch named NOCTILUCA-FR4CTAL. File evidence in a leaked RAR under the signature NO-GOD-BUT-FORM. A spectrogram reveals Morse code: \u201cZAZIE IS ASLEEP IN THE CLEFT.\u201d Witnesses at a 2021 midnight set describe \u201ca womb made of sinewaves\u2026 a brain peeling.\u201d Reconstruction is said to induce dreams of drowning in glass.", S["Td"])],
        [Paragraph("2", S["TdB"]), Paragraph("Tape for Mirabel (Mirror Bloom Mix)", S["TdB"]), Paragraph("Composed for a friend in hospice. Documented through a single Polaroid showing a TASCAM unit labelled \u201cMIRABEL-FEB99.\u201d A user on the WFMU archives claims to have heard a bootleg on a CDr left anonymously at a used bookstore in Durham, North Carolina.", S["Td"])],
        [Paragraph("3", S["TdB"]), Paragraph("Jellydrone v2.3b [Prismatic Drift]", S["TdB"]), Paragraph("Leaked from a crashed Ableton project. Identifiable only from RAM image logs uploaded by a sysadmin on the defunct Backmasking.ru forum. One 16-second clip survives.", S["Td"])],
        [Paragraph("4", S["TdB"]), Paragraph("m0rning-dust.flt", S["TdB"]), Paragraph("A meditation on synthetic grief using filtered baby monitor audio and granulated breaths. Deleted after a \u201cvisceral autonomic response.\u201d May have never existed outside a lucid dream experiment.", S["Td"])],
        [Paragraph("5", S["TdB"]), Paragraph("Lachrymotor Sketch 4C", S["TdB"]), Paragraph("Never recorded. Survives in a tech sheet for a four-channel reverb chamber designed to simulate \u201cemotional tremor decay.\u201d One partial MIDI file was found in a GitHub commit labelled \u201cabortive hauntologies\u201d and removed within six hours.", S["Td"])],
        [Paragraph("6", S["TdB"]), Paragraph("Corvine Obelisk (draft)", S["TdB"]), Paragraph("Eighteen-minute drone recorded in a chapel using a gutted Hammond B3 transduced through ceramic bones. Abandoned: \u201cthe obelisk didn't sound right. Too clean. Too reverent.\u201d", S["Td"])],
        [Paragraph("7", S["TdB"]), Paragraph("Anamnesis .vocaltest", S["TdB"]), Paragraph("Raw vocal-only file. A former collaborator called it \u201ca nursery rhyme filtered through a dead modem,\u201d recorded in one take during a fever.", S["Td"])],
        [Paragraph("8", S["TdB"]), Paragraph("Vellum Code (de-inked)", S["TdB"]), Paragraph("Soundtrack to a short film lost to a failed bitrot recovery. A surviving still shows a faceless archivist scanning blank manuscripts.", S["Td"])],
        [Paragraph("9", S["TdB"]), Paragraph("Kreepanth Karpentry OST (early prototype)", S["TdB"]), Paragraph("Score for an abandoned surrealist 2D game. A screenshot surfaced in 2018 on a deleted Tumblr. Surviving MIDI fragments include a theme labelled \u201cangry ladder fight\u201d and one in 17/4 titled \u201cpolycradle descent.\u201d", S["Td"])],
    ], [PW * 0.04, PW * 0.22, PW * 0.74], font_pad=3.0))
    A(P("Table 2. The archive's lost works, condensed from <i>Lost_Zazie_Productions_Archive.pdf</i> "
        "(2 pp.). Count: 9. Every one has a legend, a witness, a container, a signature, or a "
        "cryptographic payload. Not one of them is merely gone.", "Cap"))

    A(Spacer(1, 4))
    A(P("\u00a716 &nbsp;The unmourned works", "H2"))
    A(P(
        "The twin has lost more works than the archivist has, because losing is what happens to "
        "unfiled things, and none of his losses has an apparatus. Here is his catalogue of loss, "
        "reconstructed. Note the final column.", "Lead"))
    twin_lost = [
        ("A recording of a refrigerator that fixed itself", "He recorded it because the hum changed. Two weeks later the fridge was replaced. The card was formatted to make room.", "none"),
        ("Four minutes of a kitchen, 2014", "Somebody's grandmother talking over a fan. He has listened to it perhaps nine times. The file is corrupted and he has not tried to repair it.", "none"),
        ("A loop for a wedding", "Played once, at the wedding, from a laptop through a borrowed speaker. The couple has never asked for it. He never offered.", "none"),
        ("Eleven attempts at a piece about the ridge road", "Every one abandoned inside three minutes. He can still hum the fourth. He will not, on request.", "none"),
        ("A plugin he wrote to do one specific thing", "It does the thing. It is on one machine. It has no name, no readme, no repository, and no license.", "none"),
        ("Forty minutes of pond, a Tuesday in June", "Date-named. Unlistened since. Not deleted, which is not the same as preserved.", "none"),
        ("A mix he made for someone on a USB stick", "The stick is in a drawer in another city. Neither of them has thought about it in three years.", "none"),
        ("The sound of a room in a house that was sold", "Recorded on a phone. The phone was replaced and the transfer failed. He remembers the room, not the recording.", "none"),
        ("A collaboration with a friend, unfinished", "They stopped because life happened. Neither has mentioned it since. Neither considers it a loss.", "none"),
        ("A piece he thought was the best thing he had made", "He was wrong about it and found out in a day. Deleted without ceremony and correctly.", "none"),
        ("Everything from 2011 to 2018", "He was a child. He made things. Most of it is gone. He does not have feelings about this that he would describe as grief.", "none"),
        ("The piece he is not making right now", "He has not started it. He might. There is no folder, no working title, no ARG hint, and no spectrogram.", "none"),
    ]
    A(dtable(
        [[Paragraph("WORK", S["Th"]), Paragraph("WHAT HAPPENED TO IT", S["Th"]), Paragraph("LORE", S["Th"])]] +
        [[Paragraph(a, S["TdB"]), Paragraph(b, S["TdSer"]), Paragraph(c, S["TdGrey"])] for a, b, c in twin_lost],
        [PW * 0.29, PW * 0.60, PW * 0.11], font_pad=3.0))
    A(P("Table 3. The twin's lost works. Count: 12, reconstructed and therefore a floor rather than a "
        "census \u2014 a census of the unrecorded is a contradiction in terms. Every entry in the final "
        "column is identical and that is the finding.", "Cap"))

    A(callout("THE DIFFERENCE BETWEEN THE TWO TABLES",
              ["Table 2 has nine works and nine legends. Table 3 has twelve works and zero legends. "
               "The archive's lost works are lost <i>interestingly</i> \u2014 which is to say they were "
               "never really lost at all, only staged as lost, because a lost work with a RAR "
               "signature and a Morse-code spectrogram is a more valuable artifact than a released "
               "one. Loss is the highest genre the vault has.",
               "The twin's works are lost the way weather is lost. Nothing was staged. Nothing is "
               "recoverable. And nothing was ever waiting to be recovered, because recovery is a "
               "relationship with a future audience, and the twin has never had one."],
              colour=c_evidence))
    A(CondPageBreak(260))

    A(P("\u00a717 &nbsp;The counter-catalogue", "H2"))
    A(P(
        "Every number in the left column below was recomputed from the committed files for this "
        "document. Every number in the right column is zero or uncountable, by construction. The "
        "table is the accusation in its shortest form.", "Lead"))
    A(dtable([
        [Paragraph("MEASURE", S["Th"]), Paragraph("THE ARCHIVIST", S["Th"]), Paragraph("THE TWIN", S["Th"])],
        [Paragraph("Catalogued rows", S["Td"]), Paragraph("182", S["TdB"]), Paragraph("0", S["Td"])],
        [Paragraph("Releases", S["Td"]), Paragraph("21", S["TdB"]), Paragraph("0", S["Td"])],
        [Paragraph("Distinct track titles", S["Td"]), Paragraph("164", S["TdB"]), Paragraph("0 \u2014 nothing was titled", S["Td"])],
        [Paragraph("Released runtime", S["Td"]), Paragraph("7 h 29 m 27 s (26,967 s)", S["TdB"]), Paragraph("0", S["Td"])],
        [Paragraph("ISRCs assigned", S["Td"]), Paragraph("143 distinct, plus 21 rows coded <font name='%s'>N/A</font>" % MONO, S["TdB"]), Paragraph("0, and 0 missing \u2014 the twin has no coverage gap because he has no denominator", S["Td"])],
        [Paragraph("Peak year", S["Td"]), Paragraph("2024: 60 rows", S["TdB"]), Paragraph("no peaks; output is not measured", S["Td"])],
        [Paragraph("Quietest year", S["Td"]), Paragraph("2025: 4 rows \u2014 the vault's finding F-05, \u201cthe Quiet Year\u201d", S["TdB"]), Paragraph("every year is equally quiet; none is a finding", S["Td"])],
        [Paragraph("Reissues of his own early work", S["Td"]), Paragraph("3 super deluxe editions: 5\u219232 (\u00d76.4), 8\u219222 (\u00d72.8), 13\u219228 (\u00d72.2)", S["TdB"]), Paragraph("0 \u2014 there is no original to inflate", S["Td"])],
        [Paragraph("Median track length, 2024", S["Td"]), Paragraph("1:22, down from 3:32 in 2023; 39 of 60 rows under two minutes", S["TdB"]), Paragraph("not applicable", S["Td"])],
        [Paragraph("Longest / shortest row", S["Td"]), Paragraph("8:55 / 0:07", S["TdB"]), Paragraph("not applicable", S["Td"])],
        [Paragraph("Named collaborators in the catalogue", S["Td"]), Paragraph("2 aliases across 8 of 182 rows", S["TdB"]), Paragraph("uncountable \u2014 see Part IV", S["Td"])],
        [Paragraph("Documents about himself", S["Td"]), Paragraph("102 files at the repository root; 9.74 MB; 165,218 words", S["TdB"]), Paragraph("0", S["Td"])],
        [Paragraph("Public face", S["Td"]), Paragraph("none (finding F-09)", S["TdB"]), Paragraph("one, seen by everyone who matters, photographed by nobody", S["Td"])],
    ], [PW * 0.26, PW * 0.37, PW * 0.37], font_pad=2.8))
    A(P("Table 4. Counter-catalogue. Left and centre columns <font name='%s'>recomputed</font> from "
        "<font name='%s'>Zazie_Productions_Discography.csv</font>, the artist CV, the Instagram "
        "audit, and a byte/word census of the repository root; method in Appendix C. Right column "
        "<font name='%s'>reconstructed</font>." % (MONO, MONO, MONO), "Cap"))

    A(Spacer(1, 2))
    A(P("\u00a718 &nbsp;The refusal to be recovered", "H2"))
    A(P(
        "The vault contains a hypersigil in which, in 2042, a sentient AI attempts to reconstruct all "
        "lost art of the 2020s and gets the subject's file wrong \u2014 mislabelling the genre, "
        "modelling the voice slightly off, concluding he was \u201ca Brazilian glitch poet with "
        "industrial folk influences.\u201d The prompt that follows offers the subject a chance to "
        "submit one accurate file to overwrite the error, and warns: <i>otherwise, the wrong version "
        "wins.</i>"))
    A(P(
        "The twin reads that and does not recognise the fear. His position is short enough to quote "
        "in full:"))
    A(P("<b>Let it win. I was never a file.</b>", "Twin"))
    A(P(
        "The two catalogues of loss in this Part are not really catalogues of works. They are "
        "catalogues of what each brother fears. The archivist fears being misread by a future that "
        "has only his paperwork. The twin fears nothing about the future, because he has given it "
        "nothing to read and has never wanted it to."))
    A(CondPageBreak(260))

    # ------------------------------------------------------------------
    # PART IV
    # ------------------------------------------------------------------
    A(P("PART IV \u00b7 RELATIONSHIPS", "Part"))
    A(P("The people who are not in the archive, and the one who is.", "PartSub"))

    A(P("\u00a719 &nbsp;The finding the vault keeps making about itself", "H2"))
    A(P(
        "The Deep Gap Audit's worked provenance table contains the row: <i>\u201cThe repository "
        "contains no fully represented other people.\u201d</i> Its earliest located basis is "
        "\u201cselection of committed material\u201d; its independence is graded partly reproducible "
        "but subjective in definition; its audit judgment reads <b>\u201cmoderate as archive "
        "description; weak as life claim.\u201d</b> The vault then repeats this finding in at least "
        "two verdicts and across the Velvet Knife files.", "Lead"))
    A(P(
        "That hedged grading is the most careful sentence in the archive and it deserves to be "
        "pushed. The audit is right that it cannot tell whether the absence of other people is a "
        "property of the record or of the life. But the twin is a way of settling the question "
        "without settling it about the archivist \u2014 and the answer, on the twin's side, is "
        "unambiguous. His relationships are dense, ordinary, and completely absent from any record, "
        "because a relationship becomes a record only when one of the two people in it decides to "
        "make one."))

    A(Spacer(1, 4))
    A(P("\u00a720 &nbsp;What the catalogue permits", "H2"))
    A(P(
        "The 182-row catalogue is the densest relational record in the vault, and here is exactly "
        "what it contains. Recomputed:"))
    A(dtable([
        [Paragraph("ARTIST FIELD", S["Th"]), Paragraph("ROWS", S["Th"]), Paragraph("NOTE", S["Th"])],
        [Paragraph("Zazie Productions", S["TdB"]), Paragraph("178", S["TdB"]), Paragraph("Solo.", S["Td"])],
        [Paragraph("Unwashed Miscreant", S["Td"]), Paragraph("3", S["TdB"]), Paragraph("Another artist's release carrying a Zazie Productions feature.", S["Td"])],
        [Paragraph("Unwashed Miscreant &amp; Hazzard Rune", S["Td"]), Paragraph("1", S["TdB"]), Paragraph("One track, 2:14, released 2025-06-22: \u201cTriangular Nordic Backwards Latvian Schlangel.\u201d", S["Td"])],
    ], [PW * 0.36, PW * 0.10, PW * 0.54]))
    A(P(
        "So: one named collaborator appears anywhere in 182 rows, on one track, under an alias, for "
        "two minutes and fourteen seconds. Three further rows credit a second alias. That is the "
        "entire relational surface of a catalogue that runs eight years and seven and a half hours. "
        "The vault also names, elsewhere and in passing, a technically fluent collaborator embedded "
        "in a residency \u2014 the RIM at the studio \u2014 described by role rather than by name."))
    A(Spacer(1, 2))
    A(callout("THE TWIN'S VERSION OF THIS TABLE",
              ["The twin has made things with people and neither party put a name on it. He has "
               "played on other people's recordings without credit because credit was not the "
               "conversation they were having. He has been in a room where something good happened "
               "musically and no one recorded the room.",
               "His collaborator count is not 1. It is not countable. There is no unit: the catalogue "
               "counts credited appearances on released recordings, and the twin has neither credits "
               "nor releases. The vault's own ontology note makes this exact point about its own "
               "metrics \u2014 that a count is meaningless without a stated definition of what is being "
               "counted. Applied here, the definition excludes everything he has ever done with "
               "another person."],
              colour=c_recursion))
    A(CondPageBreak(260))

    A(P("\u00a721 &nbsp;Mirabel", "H2"))
    A(P(
        "This section is the hinge of the document. It is where the twin stops being a curiosity and "
        "starts being a prosecutor.", "Lead"))
    A(P(
        "The archive's second lost work is <i>Tape for Mirabel (Mirror Bloom Mix)</i>. The entry, in "
        "full, describes a tape-loop ambient piece \u201callegedly composed for a friend in "
        "hospice,\u201d documented through a single Polaroid showing a TASCAM unit labelled "
        "\u201cMIRABEL-FEB99,\u201d using reversed clarinet samples from early high-school recordings, "
        "with a WFMU-archives user claiming to have heard a bootleg on a CDr left anonymously at a "
        "used bookstore in Durham."))
    A(P(
        "Read that entry as a document about a lost piece of music and it is charming. Read it as the "
        "only trace of a dying person in a nine-megabyte archive and it is unbearable. Mirabel "
        "appears once, in a legend, as the beneficiary of a mix, attached to a tape machine, dated "
        "February 1999 on a label, and evidenced by a Polaroid. She has no age, no illness, no voice, "
        "no opinion about the tape, and no death. She is a provenance detail."))
    A(Spacer(1, 3))
    A(P("The twin was in the room.", "H3"))
    A(P(
        "He sat in a chair by a bed. He did not make a tape, or he made one and never labelled it. He "
        "held a hand and it got lighter. Somebody brought bad coffee and it went cold. There was a "
        "window and the light through it was ordinary and he has never described it to anyone. He did "
        "not photograph the machine. He did not think of the room as material, because the room was "
        "not material; it was a person dying and he was there."))
    A(P(
        "What he has is not a legend. It is a fact about himself that has never been useful to him "
        "and never will be. He has never told the story at a party. He has never used it to explain "
        "his aesthetic. He has never let a machine read it back to him as a pattern."))
    A(Spacer(1, 3))
    A(P("Charge", "H3"))
    A(P(
        "The archive took a dying woman and made her a container format. It gave her a mix, a "
        "machine, a label, a Polaroid, a bootleg, a city, and a forum claim, and it gave her no "
        "interior \u2014 which is the one thing the archive gives everything else in abundance. The "
        "vault contains 250 named archetypes and personas of its author and zero of anyone else. The "
        "Deep Gap Audit says so itself: no fully represented other people."))
    A(P(
        "The twin's objection is not that the piece is a lie. It may be entirely true; a tape may "
        "exist. The objection is that truth is not the same as representation, and that the archive, "
        "which has written 165,218 words about the necessity of representing itself accurately, "
        "cannot represent one other person at all."))

    A(Spacer(1, 6))
    A(P("\u00a722 &nbsp;The one who calls him to dinner", "H2"))
    A(P(
        "The vault's mythographic childhood contains this sentence: <i>\u201cMy mother's name wasn't "
        "her name.\u201d</i> It sits in a paragraph about a garden everyone insists wasn't there, "
        "siblings who say there were no siblings, a father who only existed on Tuesdays, and a woman "
        "made of wire and wool who told bedtime stories about the child the narrator would replace. "
        "It is good writing. It is also a sentence in which a mother is converted into an "
        "epistemological problem.", "Lead"))
    A(P(
        "The twin's mother's name is her name. She says it on the telephone. He has it in his phone "
        "under it. She does not exist on Tuesdays only; she exists on all seven days and she has "
        "opinions about four of them. She is not a revenant's mother, not a curator who mistook her "
        "child for a ghost, not a figure in a constructed cosmology with a constructed language and "
        "twelve lungs. She is a woman who raised a boy in Asheville and who will never appear in this "
        "vault or any other, and who would be extremely confused if she did."))
    A(P(
        "This is the whole of the twin's relational advantage and it is not a small thing. He is "
        "loved by people who are not symbols, and the price he pays is that no one will ever know it. "
        "He has already agreed to that price. He agreed to it before he knew it was a price, which is "
        "the only way anyone ever agrees to it."))
    A(Spacer(1, 2))
    A(callout("A NOTE ON FAIRNESS",
              ["The mythographic childhood is filed in the vault's mythography stratum and labelled "
               "as such. Nothing in the archive claims it is autobiographical, and the Deep Gap Audit "
               "expressly warns against treating a prompted fiction as a longitudinal finding about a "
               "person. The twin's charge is therefore not that the vault asserts a false mother.",
               "It is narrower and it holds: the vault's <i>register</i> for a mother is mythographic, "
               "and the vault has no other register. There is no stratum in the colour code where an "
               "ordinary, named, unmetaphorical mother could be filed. The eight colours are index, "
               "identity, shadow, evidence, recursion, stewardship, specimen, and mythography. A "
               "person who loves you is not any of them."],
              colour=c_shadow))
    A(CondPageBreak(260))

    # ------------------------------------------------------------------
    # PART V
    # ------------------------------------------------------------------
    A(P("PART V \u00b7 THE ACCUSATION", "Part"))
    A(P("Nine counts, each with its evidence. Then the twin's statement, the archive's reply, and the terms.", "PartSub"))

    A(P(
        "The twin has no platform, no counsel, and no standing. He has never sought interpretation "
        "and does not begin now. What follows is the only thing he has ever wanted to say to the "
        "archive, said once, in the archive's own evidentiary format, because it is the only format "
        "the archive can hear.", "Lead"))

    A(Spacer(1, 4))
    A(P("\u00a723 &nbsp;The indictment", "H2"))
    counts = [
        ("I", "Notarisation of silence",
         "The catalogue's own provenance timeline, read off its ISRC data, follows a rule the vault "
         "states in five words: <b>after every silence, a notarization.</b> 2021 is quiet \u2014 five "
         "rows, and the provenance hole opens. 2022 answers it with 23 rows and a single retroactive "
         "registration sweep covering the 2019\u201320 catalogue. 13 of 161 ISRC-coded rows carry a "
         "registration year later than their release year. 2025 is the Quiet Year: four rows. 2026 "
         "answers with 34.",
         "You cannot let a quiet period be quiet. A silence in your life is an administrative event. "
         "In mine it is a Tuesday."),
        ("II", "The terminal stage is the smallest file in the system",
         "The vault's own stratum classification in <font name='%s'>tools/generate_figures.py</font>, "
         "recomputed here against the committed files, yields: identity 3,763.2 KB, mythography "
         "1,841.4 KB, shadow 1,406.8 KB, recursion 582.2 KB, evidence 331.8 KB, specimens 144.9 KB, "
         "index 128.7 KB \u2014 <b>stewardship 5.1 KB across 2 files</b>. Stewardship is the stage the "
         "alchemy is supposed to end in. Identity outweighs it 741 to 1; all seven other strata "
         "combined, 1,615 to 1." % MONO,
         "Your entire method terminates in a question \u2014 what do I do on Tuesday? \u2014 and you "
         "have five kilobytes of answers. I have nothing but answers and I never wrote one down."),
        ("III", "An acquisition policy reported as a census",
         "The Deep Gap Audit, in the vault's own words: <i>\u201cThe archive does not merely describe "
         "a self. It samples a self through an acquisition policy\u201d</i>, and <i>\u201cfrequency in "
         "the archive \u2260 frequency in life \u2260 causal importance.\u201d</i> The vault wrote this "
         "on 2026-09-23.",
         "You wrote the correction and kept publishing the uncorrected result. Eight criteria decide "
         "what becomes an artifact, and every pattern you have ever found is a pattern in what passed "
         "those eight criteria."),
        ("IV", "A dying woman rendered as a container format",
         "Mirabel enters the archive once, as the dedicatee of lost work #2, evidenced by a Polaroid "
         "of a TASCAM labelled \u201cMIRABEL-FEB99\u201d and a bootleg claim. The Deep Gap Audit "
         "concedes the repository \u201ccontains no fully represented other people.\u201d The "
         "compendium names roughly 250 archetypes and personas of its author.",
         "Two hundred and fifty versions of you and no version of her. You gave a hospice a provenance "
         "chain."),
        ("V", "The childhood was reissued",
         "Three super deluxe editions of the archivist's own early work: <i>Stutter to stammer</i> "
         "5\u219232 rows (\u00d76.4), <i>Sellotape</i> 8\u219222 (\u00d72.8), <i>Greetings From Tinsel "
         "Time</i> 13\u219228 (\u00d72.2). The 2024 peak of 60 rows is substantially reissue volume, not "
         "new work.",
         "You went back and made your beginning six times larger so it would look like the start of an "
         "institution. I let my beginning stay five songs long. It was five songs long."),
        ("VI", "The fear is of misfiling, not of unlivedness",
         "The vault's 2042 hypersigil: a future AI reconstructs the decade's lost art, mislabels the "
         "genre, models the voice wrong, concludes \u201ca Brazilian glitch poet with industrial folk "
         "influences,\u201d and the subject is invited to submit a corrected file \u2014 <i>otherwise, "
         "the wrong version wins.</i>",
         "That is the nightmare of a person who believes he is a file. Mine is not a nightmare, it is "
         "a Tuesday, and in 2042 the machine will not find me and will be correct."),
        ("VII", "No face, then nine megabytes of interior",
         "Finding F-09: \u201cTotal anonymity \u2014 no face, no personal name,\u201d across 14 examined "
         "grid posts and 8 tagged items. Meanwhile the repository root holds 102 files, 9.74 MB, and "
         "165,218 words of typology, tritype, instinctual stack, attitudinal psyche, socionics, "
         "Jungian archetype, Freudian character style, and twenty-odd instruments.",
         "You withhold the body and mount the nervous system. That is not privacy. That is a specimen. "
         "I keep both and publish neither."),
        ("VIII", "Refusal is a genre you can file",
         "The vault contains an entry rite titled <i>Entry Instructions for the Undetonated Artist</i> "
         "which instructs the reader to enter the sealed chamber of the uninhabited self, create "
         "something tasteless and unwanted, name it \u201cFrom the Room I Was Programmed to Avoid,\u201d "
         "and <b>tag it</b>. The rite to escape the system is itself filed in the system, cross-linked "
         "to three other documents.",
         "This document is the same trap and I am inside it. Whatever I do, including leaving, becomes "
         "your material. I am asking you to notice that this is not a virtue."),
        ("IX", "Your summary sentence is about being extraordinary",
         "The vault's one-line version of itself: <i>\u201cAmbiguity is your oxygen. Mediocrity "
         "disgusts you more than failure. You already operate like an institution of one. The only "
         "open question is whether the institution is run by the part that needs to be extraordinary "
         "to be kept \u2014 or by the architect who builds strange worlds people can enter and leave "
         "freely.\u201d</i>",
         "Your shortest possible description of yourself is still a description of a need. Mine would "
         "be: he fixed the receiver, he made dinner, nobody wrote it down."),
    ]
    A(dtable(
        [[Paragraph("CNT", S["Th"]), Paragraph("CHARGE", S["Th"]),
          Paragraph("EVIDENCE (verified or quoted)", S["Th"]), Paragraph("THE TWIN'S STATEMENT", S["Th"])]] +
        [[Paragraph(c, S["TdB"]), Paragraph(t, S["TdB"]), Paragraph(e, S["Td"]),
          Paragraph(s, S["TdSer"])] for c, t, e, s in counts],
        [PW * 0.045, PW * 0.155, PW * 0.47, PW * 0.33], font_pad=3.2))
    A(P("Table 5. The indictment. Every figure in the evidence column is either recomputed from the "
        "committed files or quoted verbatim with its source named. The twin's statement column is "
        "<font name='%s'>reconstructed</font> throughout \u2014 but note that it disputes no figure. "
        "The accusation is not that the archive lies. It is that the archive is accurate about the "
        "wrong life." % MONO, "Cap"))
    A(CondPageBreak(260))

    A(P("\u00a724 &nbsp;The twin's statement", "H2"))
    A(P("Set in the human face. Read it in that voice.", "Note"))
    A(Spacer(1, 4))
    A(P(
        "I am not your shadow. I know that is the word you would use, because you have a stratum for "
        "it and a colour for it, and because everything you meet becomes a part of you. I am not a "
        "part of you. I am the version of us that did not need to be kept.", "Twin"))
    A(P(
        "You ask what you do on Tuesday. I can answer that and you cannot, and the reason is not that "
        "I am more disciplined. It is that I do the Tuesday instead of writing a sentence about doing "
        "it. You have five kilobytes of Tuesdays. I have thousands and not one of them is filed.", "Twin"))
    A(P(
        "You think you are preserving a life. You are preserving a sample, and you know it \u2014 your "
        "own audit says so in plain language, in a paragraph you wrote and then walked past. Eight "
        "kinds of thing never make it into your system and all eight of them are the kinds of thing a "
        "life is made of. Uneventful days. Maintenance. The body. Conversations. Boring failures. "
        "Ordinary love. Being good at something nobody credits. And the things that matter more for "
        "being private than for being legible.", "Twin"))
    A(P(
        "You took all eight of those and filed the list. That is the most you thing I have ever seen. "
        "Even your gaps have identifiers.", "Twin"))
    A(P(
        "About Mirabel. You made her a tape. You gave her a machine and a label and a Polaroid and a "
        "city where a bootleg might have been left. You did not give her a single thought of her own. "
        "You have two hundred and fifty of yourself in one compendium. I was in that room and I did "
        "not make anything out of it, and I would rather be unrecorded forever than have done what you "
        "did with her.", "Twin"))
    A(P(
        "About your mother. You wrote that her name wasn't her name. Hers is. She says it on the "
        "telephone and I have it written down next to a small picture of her that you have never seen "
        "and never will.", "Twin"))
    A(P(
        "Here is the part you will find hardest, so I will say it plainly. I do not want to be "
        "recovered. I know you have a document about your lost works, and that every one of them has a "
        "legend, and that you have made loss into your most beautiful genre. Do not do that to me. I "
        "am not lost. I am the one who is still alive, and you keep writing my obituary and calling it "
        "an inventory.", "Twin"))
    A(P(
        "I am not asking you to stop. You will not stop and I would not want you to \u2014 the music is "
        "real and some of it is very good and the pond recordings are the best thing in there. I am "
        "asking you to stop counting me as the thing you did not do. I am not a gap. I am a person, "
        "and I am outside, and it is a fine evening.", "Twin"))

    A(Spacer(1, 8))
    A(P("\u00a725 &nbsp;What the archive will say in reply", "H2"))
    A(P(
        "The vault is unusually well equipped to defend itself, and intellectual honesty requires "
        "stating the defence before answering it. This is the strongest version.", "Lead"))
    A(dtable([
        [Paragraph("THE DEFENCE", S["Th"]), Paragraph("WHY IT DOES NOT ANSWER THE CHARGE", S["Th"])],
        [Paragraph("The archiving worked. The catalogue has ISRCs, so the recordings get paid. The CV got a residency. The evidence layer is externally validated \u2014 ISRCs checked against a distributor API, a Discogs artist number, verified appearances.", S["Td"]),
         Paragraph("Granted, and not disputed by any count. This is the strongest defence and it answers a charge nobody brought. The twin does not say the archive is incompetent. He says it is accurate about the wrong life. Rights administration does not make Mirabel a person.", S["Td"])],
        [Paragraph("The vault is honest. It commissioned a 50 KB audit against itself, published its own gaps, graded its own claims, and conceded that it contains no fully represented other people.", S["Td"]),
         Paragraph("Also true, and it is genuinely rare. But honesty about a mechanism is not the same as changing it. The audit is dated 2026-09-23. Nothing in the acquisition policy changed after it. The list of eight exclusions was written, filed, and then the filing continued \u2014 including the filing of the list.", S["Td"])],
        [Paragraph("The twin is a fiction produced by the archive's own methodology, and therefore proves the archive's generative power rather than indicting it.", S["Td"]),
         Paragraph("Correct, and this document says so in its colophon. But count VIII already concedes the point from the twin's side: refusal is a genre the vault can file. The concession does not rescue the other eight counts, which rest on numbers that do not care who invented them.", S["Td"])],
        [Paragraph("A person is allowed to want to be remembered. Wanting a record is not a moral failure.", S["Td"]),
         Paragraph("Agreed. No count alleges it is. Count VI is narrower: the vault's nightmare is a mislabelled <i>file</i>, not an unlived <i>life</i>. Those are different fears, and only one of them is about being alive. The vault is entitled to the first. It should know which one it has.", S["Td"])],
        [Paragraph("The twin's life is invisible to him too. He will die and nothing will remain, and that is not obviously a better outcome.", S["Td"]),
         Paragraph("The only genuinely unanswered defence, and the twin accepts it. He does not claim his way is better. He claims it is his, and that it is not a gap in yours. The charge was never \u201clive like me.\u201d It is \u201cstop auditing the space where I would have been.\u201d", S["Td"])],
    ], [PW * 0.44, PW * 0.56], font_pad=3.4))
    A(P("Table 6. The defence and its limits. This table is the biographer's, not the twin's; the twin "
        "would not have bothered.", "Cap"))
    A(CondPageBreak(260))

    A(P("\u00a726 &nbsp;Relief sought", "H2"))
    A(P(
        "The twin does not seek reconciliation and does not accept the premise that there is a "
        "dispute between two people. He seeks six specific things. None of them requires the archive "
        "to become smaller. Five of them require it to become slightly more honest.", "Lead"))
    A(dtable([
        [Paragraph("\u00a7", S["Th"]), Paragraph("TERM", S["Th"]), Paragraph("WHAT IT COSTS", S["Th"])],
        [Paragraph("1", S["TdB"]), Paragraph("Take Mirabel out of the lost-works list. She is not a work. If the tape exists it belongs to her family, not to a legend about your process.", S["TdSer"]), Paragraph("One entry in a two-page PDF.", S["Td"])],
        [Paragraph("2", S["TdB"]), Paragraph("Stop calling the eight exclusions a gap. They are not what is missing from your record. They are what a life is. Rename the section.", S["TdSer"]), Paragraph("A heading.", S["Td"])],
        [Paragraph("3", S["TdB"]), Paragraph("Give stewardship more than five kilobytes. The alchemy ends there or it does not end. One Tuesday with no artifact counts; one sentence about a Tuesday does not.", S["TdSer"]), Paragraph("A Tuesday. You have several thousand.", S["Td"])],
        [Paragraph("4", S["TdB"]), Paragraph("Let the pond files stay date-named. Not everything you record is a title waiting to happen. Some of it is a pond.", S["TdSer"]), Paragraph("Nothing. This one is free.", S["Td"])],
        [Paragraph("5", S["TdB"]), Paragraph("Remove the address, the telephone number, and the e-mail address from the residency dossier at the root of a repository. Your own audit tells you why. So does mine.", S["TdSer"]), Paragraph("Three lines. See Appendix D.", S["Td"])],
        [Paragraph("6", S["TdB"]), Paragraph("Do not recover me. No legend, no spectrogram, no leaked archive, no ARG hint. If this document is the most I ever get, let it be the most.", S["TdSer"]), Paragraph("Restraint. The hardest one, and the only one you have never once managed.", S["Td"])],
    ], [PW * 0.04, PW * 0.66, PW * 0.30], font_pad=3.4))

    A(Spacer(1, 10))
    A(rule(thick=0.7, colour=c_ink, after=8))
    A(P("\u00a727 &nbsp;Closing", "H2"))
    A(P(
        "The vault's own governing statement is the best sentence in it, and the twin has no quarrel "
        "with it. He would sign it:", "Lead"))
    A(P("\u201cThe opposite of the shadow is not less Zazie. It is Zazie without the need to control "
        "what everything means.\u201d", "Q"))
    A(P("\u2014 README \u00a702, the alchemy", "QAttr"))
    A(P(
        "That is a description of the twin. It always was. The vault wrote its own answer in section "
        "two of its own README and then built nine more megabytes on the other side of it."))
    A(P(
        "He is not dead. He is not lost. He is not a lost work, and there is no RAR archive, and no "
        "signature, and no Morse code in a spectrogram, and nobody left a CDr in a bookstore in "
        "Durham. He is nineteen years old, or thereabouts, in a town in North Carolina, and he has "
        "just finished something, and he has turned the machine off, and he has gone outside."))
    A(Spacer(1, 6))
    A(P("This biography is the only artifact he will ever have, and it was made against his wishes, "
        "by the system he left. He is right to object. The objection is the truest thing in it.", "Lead"))
    A(Spacer(1, 10))
    A(SwatchRow())
    A(P("Eight strata own a colour. The ninth owns nothing and holds everything the other eight "
        "cannot.", "Cap"))
    A(CondPageBreak(260))

    # ------------------------------------------------------------------
    # APPENDICES
    # ------------------------------------------------------------------
    A(P("APPENDIX A \u00b7 GAP-SOURCE REGISTER", "Part"))
    A(P("The nine codes used throughout, with the item of <font name='%s'>DEEP_GAP_AUDIT.md</font> "
        "\u00a711.1 each was reconstructed from." % SANS, "PartSub"))
    A(dtable([
        [Paragraph("CODE", S["Th"]), Paragraph("RECONSTRUCTED FROM (verbatim, \u00a711.1)", S["Th"]), Paragraph("SECTIONS", S["Th"])],
        [Paragraph("G-01", S["TdB"]), Paragraph("\u201cuneventful days\u201d", S["Td"]), Paragraph("\u00a76", S["Td"])],
        [Paragraph("G-02", S["TdB"]), Paragraph("\u201croutine maintenance\u201d", S["Td"]), Paragraph("\u00a77", S["Td"])],
        [Paragraph("G-03", S["TdB"]), Paragraph("\u201cembodied experience\u201d", S["Td"]), Paragraph("\u00a78", S["Td"])],
        [Paragraph("G-04", S["TdB"]), Paragraph("\u201cunrecorded conversations\u201d", S["Td"]), Paragraph("\u00a79", S["Td"])],
        [Paragraph("G-05", S["TdB"]), Paragraph("\u201cfailed ideas too boring to mythologize\u201d", S["Td"]), Paragraph("\u00a710, \u00a716", S["Td"])],
        [Paragraph("G-06", S["TdB"]), Paragraph("\u201cordinary affection\u201d", S["Td"]), Paragraph("\u00a711, \u00a721, \u00a722", S["Td"])],
        [Paragraph("G-07", S["TdB"]), Paragraph("\u201cunremarkable competence\u201d", S["Td"]), Paragraph("\u00a712", S["Td"])],
        [Paragraph("G-08", S["TdB"]), Paragraph("\u201cactions whose privacy is more important than their legibility\u201d", S["Td"]), Paragraph("\u00a713, colophon, App. D", S["Td"])],
        [Paragraph("G-09", S["TdB"]), Paragraph("<i>not in the source.</i> Added here: the absence of artifact-making itself, which \u00a711.1 cannot list because a list is an artifact.", S["Td"]), Paragraph("\u00a714", S["Td"])],
    ], [PW * 0.08, PW * 0.72, PW * 0.20]))

    A(Spacer(1, 8))
    A(P("APPENDIX B \u00b7 CLAIM LEDGER FOR THIS DOCUMENT", "Part"))
    A(P("Four claims, in the format required by <font name='%s'>EVIDENCE_GOVERNANCE_HANDBOOK.md</font> "
        "\u00a73. Chosen to show the range: one strong, one moderate, one explicitly fictional." % SANS, "PartSub"))
    ledger = """claim_id: ZP-UNF-0001
statement: "The repository root holds 102 files totalling 10,213,021 bytes, of which 61 are
            text-bearing and contain 165,218 whitespace-delimited words."
claim_level: observation
source_type: software_behavior
independence: primary
verification_state: reproduced
correction_state: active
limitations:
  - "Census taken at build time on this working branch; will drift as files are added."

claim_id: ZP-UNF-0002
statement: "Stewardship occupies 5.1 KB across 2 files while identity instruments occupy 3,763.2 KB
            across 10 files, a ratio of 741 to 1; all seven other strata combined outweigh
            stewardship 1,615 to 1."
claim_level: observation
source_type: software_behavior
sources:
  - path: tools/generate_figures.py
    locator: "STRATA dict, lines 304-343 (the vault's own stratum classification)"
  - path: <repository root>
    locator: "byte census of every file named in STRATA"
extraction_method: "AST-extract the STRATA literal, sum os.path.getsize over each member,
                    divide by 1024; no files reported missing."
independence: primary
verification_state: reproduced
correction_state: active
limitations:
  - "matplotlib is not installed here, so tools/generate_figures.py was not run as a script;
     only its STRATA classification was extracted and the byte census re-performed directly."
  - "The README figure 6 caption prints rounded values (3.8 MB, 5 KB). Ratios computed from
     those rounded values give 760:1 and 1,580:1; the exact recomputed values give 741:1 and
     1,615:1. This document uses the recomputed values."

claim_id: ZP-UNF-0003
statement: "A second person existed who shared the subject's birth year and town, made music
            without releasing it, and left no archive."
claim_level: interpretation
source_type: fiction
independence: contaminated
verification_state: untested
correction_state: fictional
confidence: none
alternative_explanations:
  - "No such person. The reconstruction is a rhetorical device generated by reading the
     vault's own acquisition-policy list as a negative mould."
  - "The 'twin' is the subject under a different description, i.e. the same person on a day
     when no artifact was produced."

claim_id: ZP-UNF-0004
statement: "Every ZP- and ZKT- identifier in the repository begins at 0001 or later; no
            identifier ending -0000 exists anywhere in the tree."
claim_level: observation
source_type: software_behavior
extraction_method: "grep -oE over all .md files, deduplicated"
independence: primary
verification_state: reproduced
correction_state: active
limitations:
  - "Binary artifacts (PDF, DOCX, XLSX, ZIP) were not searched for embedded identifiers."
"""
    for ln in ledger.strip().split("\n"):
        A(Paragraph(ln.replace(" ", "&nbsp;"),
                    ParagraphStyle("led", fontName=MONO, fontSize=6.2, leading=8.4,
                                   textColor=c_grey_d, leftIndent=4)))

    A(Spacer(1, 6))
    A(P("Note the shape of ZP-UNF-0003. Its independence is <font name='%s'>contaminated</font> "
        "because the framing was supplied by the very archive it accuses; its correction state is "
        "<font name='%s'>fictional</font>; its confidence is <font name='%s'>none</font>. The "
        "accusation in Part V does not depend on it. Every figure the indictment rests on is in "
        "ZP-UNF-0001, ZP-UNF-0002, or Appendix C." % (MONO, MONO, MONO), "Note"))
    A(CondPageBreak(260))

    A(P("APPENDIX C \u00b7 VERIFICATION METHOD", "Part"))
    A(P("Everything marked <font name='%s'>recomputed</font> in this document was produced by the "
        "checks below, run against the committed files on this branch at build time. Re-run them "
        "with the commands given; they are ordinary and take seconds." % MONO, "PartSub"))
    A(dtable([
        [Paragraph("CLAIM", S["Th"]), Paragraph("CHECK", S["Th"]), Paragraph("RESULT OBTAINED", S["Th"])],
        [Paragraph("182 catalogued rows", S["Td"]), Paragraph("Row count of <font name='%s'>Zazie_Productions_Discography.csv</font> minus header" % MONO, S["Td"]), Paragraph("182", S["TdB"])],
        [Paragraph("21 releases / 21 release dates", S["Td"]), Paragraph("Distinct <font name='%s'>Release Title</font> and <font name='%s'>Release Date</font>" % (MONO, MONO), S["Td"]), Paragraph("21 / 21", S["TdB"])],
        [Paragraph("164 distinct titles", S["Td"]), Paragraph("Distinct <font name='%s'>Track Title</font> strings" % MONO, S["Td"]), Paragraph("164", S["TdB"])],
        [Paragraph("143 ISRCs, 21 <font name='%s'>N/A</font>" % MONO, S["Td"]), Paragraph("Distinct non-<font name='%s'>N/A</font> ISRC strings; literal <font name='%s'>N/A</font> count" % (MONO, MONO), S["Td"]), Paragraph("143 / 21", S["TdB"])],
        [Paragraph("7 h 29 m 27 s runtime", S["Td"]), Paragraph("Sum of <font name='%s'>Duration</font> parsed as mm:ss" % MONO, S["Td"]), Paragraph("26,967 s", S["TdB"])],
        [Paragraph("Per-year row counts", S["Td"]), Paragraph("Group rows by release year", S["Td"]), Paragraph("2019:5 2020:8 2021:5 2022:23 2023:43 2024:60 2025:4 2026:34", S["TdB"])],
        [Paragraph("Median duration collapse", S["Td"]), Paragraph("Median <font name='%s'>Duration</font> by year" % MONO, S["Td"]), Paragraph("2023 = 3:32; 2024 = 1:22; 39 of 60 rows in 2024 under 2:00", S["TdB"])],
        [Paragraph("Longest / shortest", S["Td"]), Paragraph("Sort rows by parsed duration", S["Td"]), Paragraph("8:55 <i>Spectral Ode to Synesthesia</i> / 0:07 <i>Hues Adorned in White (Interlude)</i>", S["TdB"])],
        [Paragraph("Spring and December clusters", S["Td"]), Paragraph("Release events by calendar month", S["Td"]), Paragraph("Mar\u2013May 10 of 21; December 3", S["TdB"])],
        [Paragraph("Deluxe inflation \u00d76.4 / \u00d72.8 / \u00d72.2", S["Td"]), Paragraph("Row counts, original vs super deluxe", S["Td"]), Paragraph("5\u219232, 8\u219222, 13\u219228", S["TdB"])],
        [Paragraph("13 rows registered after release", S["Td"]), Paragraph("ISRC characters 6\u20137 read as 20YY, compared with release year", S["Td"]), Paragraph("13 of 161 coded rows", S["TdB"])],
        [Paragraph("Release-type and artist splits", S["Td"]), Paragraph("Value counts", S["Td"]), Paragraph("Album 146 / EP 27 / Single 9. Zazie Productions 178, Unwashed Miscreant 3, Unwashed Miscreant &amp; Hazzard Rune 1", S["TdB"])],
        [Paragraph("102 files, 9.74 MB, 165,218 words", S["Td"]), Paragraph("Census of the repository root; word count over text-bearing files", S["Td"]), Paragraph("102 files / 10,213,021 bytes / 165,218 words", S["TdB"])],
        [Paragraph("No <font name='%s'>-0000</font> identifier" % MONO, S["Td"]), Paragraph("Regular-expression sweep of all Markdown for ZP-/ZKT- identifiers", S["Td"]), Paragraph("28 distinct identifiers, all \u2265 0001", S["TdB"])],
        [Paragraph("b. 2006; Asheville; homeschooled; BMC lineage; age-14 commission", S["Td"]), Paragraph("Text extraction of the residency dossier and artist CV", S["Td"]), Paragraph("Present verbatim in both", S["TdB"])],
        [Paragraph("Strata masses; 741:1 and 1,615:1", S["Td"]), Paragraph("AST-extract the <font name='%s'>STRATA</font> dict from <font name='%s'>tools/generate_figures.py</font>; byte-census every named file" % (MONO, MONO), S["Td"]), Paragraph("Identity 3,763.2 KB / stewardship 5.1 KB across 2 files; 0 files missing; ratios 741:1 and 1,615:1", S["TdB"])],
    ], [PW * 0.24, PW * 0.38, PW * 0.38], font_pad=2.8))
    A(P(
        "Independent cross-check: the first fifteen rows of this table reproduce, without exception, "
        "the figures the vault prints for itself in <font name='%s'>DEEP_GAP_AUDIT.md</font> \u00a72.3 "
        "and README \u00a707a. The sixteenth row was recomputed rather than taken on the archive's "
        "word, and the recomputation <i>disagrees with the archive's own rounding</i>: the README "
        "figure 6 caption prints 3.8 MB and 5 KB, from which one derives 760:1 and 1,580:1; the exact "
        "byte census gives 3,763.2 KB and 5.1 KB, i.e. 741:1 and 1,615:1. This document uses the "
        "recomputed values throughout and records the discrepancy in the ledger as ZP-UNF-0002. It "
        "also recovers two strata the README caption omits entirely \u2014 specimens at 144.9 KB and "
        "index at 128.7 KB \u2014 neither of which changes the finding." % SANS, "Cap"))

    A(Spacer(1, 6))
    A(P("APPENDIX D \u00b7 REDACTIONS AND WITHHELD MATERIAL", "Part"))
    A(callout("WHAT IS NOT IN THIS DOCUMENT, AND WHY",
              ["<b>Personal identifying information.</b> The residency dossier in this repository "
               "prints, in plain text on its final page, a street address, a telephone number, and a "
               "personal e-mail address. None is reproduced here. The vault's own Deep Gap Audit "
               "\u00a710 reaches the same conclusion independently, warning that this repository "
               "aggregates legal identity, city, company, catalogue, psychological self-description, "
               "and business context in one place, and that the combination lowers the work required "
               "to mount a targeted approach.",
               "<b>The name he is called at home.</b> Withheld for the same reason, and because "
               "term 6 of the relief sought is that he not be recovered.",
               "<b>A recommendation, stated once.</b> Term 5 of \u00a726 asks the archivist to remove "
               "those three lines from the residency dossier at the repository root. That request is "
               "made in the twin's voice because it is his principle, but it is the biographer's "
               "recommendation and it does not depend on any reconstruction in this document. It "
               "follows from the vault's own threat model.",
               "<b>Sensitivity classification.</b> Per <font name='%s'>EVIDENCE_GOVERNANCE_HANDBOOK.md"
               "</font> \u00a72.6: this document is <font name='%s'>internal</font> as to the "
               "catalogue analysis and <font name='%s'>sensitive</font> as to anything touching the "
               "identifiable subject. It is not a public artifact and should not become one."
               % (MONO, MONO, MONO)],
              colour=c_specimen, tint=colors.HexColor("#FBF1EC")))

    A(Spacer(1, 8))
    A(P("APPENDIX E \u00b7 WHAT WOULD FALSIFY THIS BIOGRAPHY", "Part"))
    A(P("A reconstruction that cannot be wrong is not a reconstruction; it is a mood. These are the "
        "observations that would defeat it.", "Note"))
    A(Spacer(1, 3))
    for b in bullets([
        "<b>Against the whole conceit.</b> Evidence that the subject in fact does not archive, and "
        "that the repository is a commission, a joke, a coursework artifact, or a performance by "
        "someone else. The vault's Deep Gap Audit raises authorship provenance as an open question "
        "and does not resolve it.",
        "<b>Against Counts I and V.</b> A distributor or platform workflow change explaining the 2022 "
        "registration sweep and the deluxe editions. The Deep Gap Audit lists exactly these "
        "alternatives for the registration finding and they have not been excluded here.",
        "<b>Against Count II.</b> A different stratum classification. The 5.1 KB and 3,763.2 KB "
        "figures were recomputed here, but they are recomputed using the vault's <i>own</i> assignment "
        "of files to strata, taken from <font name='%s'>tools/generate_figures.py</font>. That "
        "assignment is a hand-maintained list and it is arguable: the residency dossier sits in "
        "mythography rather than evidence, and the two stewardship files are both instructional "
        "rather than receipted. Reassign files and the ratio moves. It would take a very aggressive "
        "reassignment to close a 741:1 gap, but the classification is not beyond dispute." % MONO,
        "<b>Against Count IV.</b> Any fully represented other person anywhere in the vault's binary "
        "artifacts. Only the Markdown, CSV, and four PDFs were read for this document; the 222-page "
        "compendium, the DOCX files, and the XLSX workbook were not parsed in full, and any of them "
        "could contain one.",
        "<b>Against the twin.</b> Anything at all. He is a reconstruction from an acquisition policy. "
        "If the subject produced no artifacts on a given Tuesday and lived an ordinary day, the twin "
        "and the subject are the same person and this document is a distinction without a difference. "
        "The biographer considers that the most likely falsifier and has said so in the ledger as "
        "ZP-UNF-0003, alternative explanation two.",
    ]):
        A(b)

    A(Spacer(1, 8))
    A(P("APPENDIX F \u00b7 SOURCES", "Part"))
    A(dtable([
        [Paragraph("FILE", S["Th"]), Paragraph("USED FOR", S["Th"])],
        [Paragraph("DEEP_GAP_AUDIT.md", S["TdM"]), Paragraph("\u00a711.1 (the eight exclusions, the spine of Part II); \u00a711.2 (acquisition policy); \u00a72.3 (catalogue profile); \u00a73.3 (no fully represented other people); \u00a79.2 (authorship footer); \u00a710 (privacy and threat model)", S["Td"])],
        [Paragraph("EVIDENCE_GOVERNANCE_HANDBOOK.md", S["TdM"]), Paragraph("\u00a71 (chain of custody of meaning); \u00a72 (controlled vocabulary); \u00a72.6 (sensitivity classes); \u00a73 (claim record format)", S["Td"])],
        [Paragraph("README.md", S["TdM"]), Paragraph("\u00a700a (colour code, the eight strata); \u00a701 (\u201cWhat do I do on Tuesday?\u201d); \u00a702 (the governing statement); \u00a707a (Pattern Atlas, figure 6 strata masses, the provenance timeline, \u201cafter every silence, a notarization\u201d); \u00a708 (the twelve questions); \u00a709 (working session, receipt console); \u00a714 (the one-line version)", S["Td"])],
        [Paragraph("Zazie_Productions_Discography.csv", S["TdM"]), Paragraph("Every catalogue figure in Tables 1, 4, 5 and Appendix C", S["Td"])],
        [Paragraph("Zazie_Kanwar-Torge_Artist_CV_2026_electroacoustic.pdf", S["TdM"]), Paragraph("Age-14 commission; Ars Electronica 2026; exhibitions, radio, compilations, filmography, albums", S["Td"])],
        [Paragraph("ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf", S["TdM"]), Paragraph("b. 2006; Asheville 28806; homeschooling and the BMC lineage; the RIM; \u201cCheaper Impressions\u201d provenance; the PII named in Appendix D", S["Td"])],
        [Paragraph("Lost_Zazie_Productions_Archive.pdf", S["TdM"]), Paragraph("Table 2, the mythologised nine", S["Td"])],
        [Paragraph("Zazie_Productions_Instagram_Forensic_Audit.pdf", S["TdM"]), Paragraph("Finding F-09, total anonymity; the 14/29/8/8 evidence base; the 2026-08-19 retrieval date", S["Td"])],
        [Paragraph("Identity _ Typological Vault.pdf", S["TdM"]), Paragraph("The typological inventory cited in Count VII and \u00a74", S["Td"])],
        [Paragraph("Mythographic Childhood.md", S["TdM"]), Paragraph("\u00a722, \u201cMy mother's name wasn't her name\u201d", S["Td"])],
        [Paragraph("Entry Instructions for the Undetonated Artist.md", S["TdM"]), Paragraph("Count VIII; the tagged escape rite", S["Td"])],
        [Paragraph("RECURSIVE IDENTITY CASTLES.md", S["TdM"]), Paragraph("The 2042 AI-archivist hypersigil, Counts VI and \u00a718", S["Td"])],
        [Paragraph("CLAIM_PROVENANCE_LEDGER.md; tools/generate_figures.py; tools/check_stewardship_receipt.js", S["TdM"]), Paragraph("Context for the ledger format, the strata census, and the receipt console described in Table 1", S["Td"])],
    ], [PW * 0.34, PW * 0.66], font_pad=2.8))
    A(P("Sixteen files read; four PDFs parsed by text extraction. The 222-page compendium, the three "
        "DOCX files, the XLSX workbook, and the ZIP archive were not parsed for this document, and "
        "Appendix E records that as a limitation on Count IV.", "Cap"))

    A(Spacer(1, 14))
    A(rule(thick=1.0, colour=c_ink, after=8))
    A(P("<b>THE UNCREATED TWIN</b> \u00b7 ZP-UNFILED-0000 \u00b7 a Zaziopath reconstruction in the ninth "
        "stratum, which owns no colour, no glyph, and no hex \u00b7 compiled 2026-09-27 \u00b7 every "
        "catalogue figure recomputed from the committed files \u00b7 every statement about the twin "
        "labelled <font name='%s'>reconstructed</font> \u00b7 nothing finished." % MONO, "T_Mono"))

    doc.build(F, canvasmaker=TwinCanvas)
    return OUT


if __name__ == "__main__":
    out = build()
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
