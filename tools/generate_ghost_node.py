#!/usr/bin/env python3
"""Render the ghost figure for ``👻 X — The Missing Variable.md``.

Two figures, both hand-laid SVG in the §00a Okabe–Ito palette:

* ``figx_ghost_node.svg``   — the empty node and its neighbourhood: ten anomalies
  wired in, four consequence-lines out, ten candidate identities tethered but
  never admitted.
* ``figx_ghost_in_graph.svg`` — the vault's own knowledge graph with the same
  empty node inserted, so the blank sits inside the map rather than beside it.

The node is drawn with an intentionally empty interior: no glyph, no word, no
watermark. Its edges carry all the information; its contents carry none.

A PNG preview is emitted when ImageMagick is available in this environment.

Run:  python3 tools/generate_ghost_node.py
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"

# §00a palette
INK = "#231F20"
IDENTITY = "#0072B2"
SHADOW = "#CC79A7"
EVIDENCE = "#E69F00"
RECURSION = "#009E73"
STEWARD = "#56B4E9"
SPECIMEN = "#D55E00"
MYTH = "#F0E442"
PAPER = "#FBFAF7"
DIM = "#6E6A66"

SANS = "Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'Courier New', Courier, monospace"

# anomaly → (class, headline, measurement)
CLASS_COLOURS = {"INSTRUMENT": (STEWARD, "⚙"), "RECORD": (EVIDENCE, "▤"), "WORLD": (SPECIMEN, "⚑")}

ANOMALIES = [
    ("A1", "RECORD", "Two records of one catalogue",
     "200-row workbook / 182-row CSV · each omits what the other holds"),
    ("A2", "RECORD", "The count includes its own bookkeeping",
     "'200 tracks' contains 4 rows that are not tracks"),
    ("A3", "INSTRUMENT", "Identifiers move in both directions in time",
     "13 codes assigned after release (+2/+3) · 20 codes carried forward (−1/−2/−4)"),
    ("A4", "INSTRUMENT", "Missingness is platform-shaped",
     "'—' means 'not found on Deezer', not 'no ISRC' · 35/200 rows"),
    ("A5", "RECORD", "The miniaturisation is a packaging artefact",
     "2024: 60 rows, 100% deluxe, median 82 s · deluxe 104 s vs non-deluxe 160 s"),
    ("A6", "RECORD", "The quiet year flips with the metric",
     "2025 = 4 rows but 3 release events; 2024 = 60 rows but 0 new non-deluxe rows"),
    ("A7", "INSTRUMENT", "The zero that cannot be observed",
     "ledger: 0 network calls, 2 localStorage refs · empty and full repos byte-identical"),
    ("A8", "RECORD", "The archive is mostly made of names",
     "382/414 wikilink targets dangle · the Inventory resolves 2/336 notes"),
    ("A9", "RECORD", "No person appears as a person",
     "178/182 rows solo · collaborators appear as artist strings only"),
    ("A10", "INSTRUMENT", "Audience is measured only where it is not yours",
     "≈32k playlist followers recorded · 0 audience figures for any own release"),
]

# candidate → (score/20, tag, note)
CANDIDATES = [
    ("audience", 7, "motivational", "explains the role asymmetry, not the records"),
    ("boredom", 2, "motivational", "no state series anywhere to test it"),
    ("novelty", 3, "motivational", "predicts exploration; visible only in titles"),
    ("economic pressure", 9, "motivational", "best motivational fit; untested — no income series"),
    ("technological affordance", 14, "instrumental", "explains 6 anomalies as primary cause"),
    ("developmental change", 4, "motivational", "one step-change (2022) is its only footprint"),
    ("chance", 2, "null model", "cannot be rejected at n=21 events; explains no structure"),
    ("the unit of account", 17, "instrumental", "dissolves 4 anomalies, explains 6 more"),
    ("the unlogged world", 9, "container", "unfalsifiable in-repo by construction"),
    ("the withheld register", 5, "container", "redaction is visible; its contents are not auditable"),
]

CONSEQUENCES = [
    (IDENTITY, "◉", "IDENTITY", "which self-description survives subtraction"),
    (SHADOW, "◐", "SHADOW", "which pattern is a state and which a by-product"),
    (EVIDENCE, "▤", "EVIDENCE", "what the catalogues actually record"),
    (STEWARD, "△", "STEWARDSHIP", "whether a line is ever emitted"),
    (SPECIMEN, "⚑", "THE RESIDUAL", "one question nothing here measures"),
]


def head(w: int, h: int, title: str, subtitle: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}: {escape(subtitle)}">
<rect x="0" y="0" width="{w}" height="{h}" fill="{PAPER}"/>
<rect x="18" y="18" width="{w-36}" height="{h-36}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.35"/>
<text x="60" y="86" font-family="{SERIF}" font-size="42" fill="{INK}" letter-spacing="1.5">{escape(title)}</text>
<text x="60" y="120" font-family="{MONO}" font-size="15" fill="{DIM}">{escape(subtitle)}</text>
<line x1="60" y1="140" x2="{w-60}" y2="140" stroke="{INK}" stroke-width="1" opacity="0.25"/>
"""


def chip(x: float, y: float, cls: str) -> str:
    colour, glyph = CLASS_COLOURS[cls]
    w = 26 + 8 * len(cls)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" fill="none" stroke="{colour}" stroke-width="1.4"/>'
            f'<text x="{x+9}" y="{y+16}" font-family="{MONO}" font-size="12" fill="{colour}">{glyph} {cls}</text>'), w


def node_block(x: float, y: float, w: float, h: float) -> str:
    """The empty node: dashed boundary, empty interior, label outside the box."""
    return f"""<g>
<text x="{x + w/2}" y="{y - 70}" text-anchor="middle" font-family="{SERIF}" font-size="54" fill="{INK}">👻 X</text>
<text x="{x + w/2}" y="{y - 38}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{DIM}">the missing variable · interior blank · identity withheld</text>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#FFFFFF" stroke="{INK}" stroke-width="2.6" stroke-dasharray="16 11"/>
<text x="{x + w/2}" y="{y + h + 30}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}">edges legible · contents unassigned</text>
</g>
"""


def ghost_glyph(x: float, y: float, scale: float = 1.0, colour: str = INK) -> str:
    """A drawn ghost, so the figure survives environments without an emoji font."""
    k = scale
    return f"""<g transform="translate({x},{y}) scale({k})" fill="none" stroke="{colour}" stroke-width="2.4" stroke-linejoin="round">
<path d="M 0 34 C 0 6 12 -6 24 -6 C 36 -6 48 6 48 34 L 48 60 C 44 56 40 62 36 60 C 32 58 30 62 26 60 C 22 58 20 62 16 60 C 12 58 10 62 6 60 C 3 58 1 60 0 58 Z"/>
<circle cx="17" cy="24" r="3.4" fill="{colour}" stroke="none"/>
<circle cx="33" cy="24" r="3.4" fill="{colour}" stroke="none"/>
</g>"""


def fig_node(path: Path) -> None:
    W, H = 2600, 2060
    s = [head(W, H, "X — THE MISSING VARIABLE",
              "ZP-GV-2026-0930 · ten anomalies measured from committed artefacts · ten candidate identities tested · X left unnamed")]
    s.append(ghost_glyph(742, 44, 0.78, INK))

    # ── anomaly cards: two rows of five ────────────────────────────────────
    card_w, card_h, gap_x, gap_y = 470, 208, 20, 22
    x0, y0 = 60, 178
    for i, (code, cls, headline, measure) in enumerate(ANOMALIES):
        row, col = divmod(i, 5)
        x = x0 + col * (card_w + gap_x)
        y = y0 + row * (card_h + gap_y)
        colour, _ = CLASS_COLOURS[cls]
        s.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.1"/>')
        s.append(f'<rect x="{x}" y="{y}" width="6" height="{card_h}" fill="{colour}"/>')
        s.append(f'<text x="{x+22}" y="{y+34}" font-family="{MONO}" font-size="19" fill="{INK}">{code}</text>')
        c, cw = chip(x + 66, y + 16, cls)
        s.append(c)
        for k, line in enumerate(_wrap(headline, 34)[:3]):
            s.append(f'<text x="{x+22}" y="{y+76+k*25}" font-family="{SANS}" font-size="20" fill="{INK}" font-weight="bold">{escape(line)}</text>')
        for k, line in enumerate(_wrap(measure, 56)[:3]):
            s.append(f'<text x="{x+22}" y="{y+152+k*20}" font-family="{MONO}" font-size="12.5" fill="{DIM}">{escape(line)}</text>')
        # wire into the node
        cx = x + card_w / 2
        cy = y + card_h
        tx = 1040 + (i % 5) * 122 + (0 if i < 5 else 44)
        s.append(f'<path d="M {cx} {cy} C {cx} {cy+110} {tx} {820-110} {tx} 820" fill="none" stroke="{colour}" stroke-width="1.5" opacity="0.55"/>')

    # ── the empty node ─────────────────────────────────────────────────────
    nx, ny, nw, nh = 1000, 820, 600, 700
    s.append(ghost_glyph(nx + nw/2 - 60, ny - 138, 0.85, INK))
    s.append(f'<text x="{nx + nw/2 + 16}" y="{ny - 96}" text-anchor="middle" font-family="{SERIF}" font-size="46" fill="{INK}">X</text>')
    s.append(f'<text x="{nx + nw/2}" y="{ny - 62}" text-anchor="middle" font-family="{MONO}" font-size="13.5" fill="{DIM}">the missing variable · interior blank · identity withheld</text>')
    s.append(f'<text x="{nx + nw/2}" y="{ny - 34}" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{DIM}">&#9660; ten anomalies enter</text>')
    s.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="#FFFFFF" stroke="{INK}" stroke-width="2.6" stroke-dasharray="16 11"/>')
    s.append(f'<text x="{nx + nw/2}" y="{ny + nh + 34}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}">edges legible · contents unassigned</text>')
    s.append(f'<text x="{nx + nw/2}" y="{ny + nh + 62}" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{DIM}">&#9660; what a named X would determine</text>')

    # ── candidate panels, tethered but not admitted ────────────────────────
    s.append(f'<text x="60" y="{ny-34}" font-family="{MONO}" font-size="13.5" fill="{DIM}">CANDIDATE IDENTITIES TESTED — none admitted to the interior</text>')
    s.append(f'<text x="2540" y="{ny-34}" text-anchor="end" font-family="{MONO}" font-size="13.5" fill="{DIM}">CANDIDATE IDENTITIES TESTED — none admitted to the interior</text>')
    for i, (name, score, tag, note) in enumerate(CANDIDATES):
        left = i < 5
        bx = 60 if left else 1700
        by = ny + 26 + (i % 5) * 134
        bw, bh = 840, 118
        s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#FFFFFF" stroke="{DIM}" stroke-width="1.1" stroke-dasharray="7 6"/>')
        s.append(f'<text x="{bx+20}" y="{by+32}" font-family="{SERIF}" font-size="23" fill="{INK}">X = {escape(name)}</text>')
        s.append(f'<text x="{bx+bw-20}" y="{by+32}" text-anchor="end" font-family="{MONO}" font-size="14.5" fill="{DIM}">{score}/20 · {escape(tag)}</text>')
        s.append(f'<rect x="{bx+20}" y="{by+46}" width="{bw-40}" height="8" fill="none" stroke="{INK}" stroke-width="0.7" opacity="0.4"/>')
        s.append(f'<rect x="{bx+20}" y="{by+46}" width="{(bw-40)*score/20:.0f}" height="8" fill="{EVIDENCE if score>=14 else DIM}" opacity="{0.9 if score>=14 else 0.45}"/>')
        s.append(f'<text x="{bx+20}" y="{by+78}" font-family="{MONO}" font-size="12.5" fill="{DIM}">{escape(note)}</text>')
        verdict = ("closest fit — instrumental: dissolves anomalies rather than naming X" if score >= 14
                   else "fails the threshold (&#8805;14/20 with a unit-invariant target)")
        s.append(f'<text x="{bx+20}" y="{by+100}" font-family="{MONO}" font-size="12.5" fill="{DIM}">{verdict}</text>')
        sx = bx + bw if left else bx
        sy = by + bh / 2
        ex = nx - 30 if left else nx + nw + 30
        mx = (sx + ex) / 2
        s.append(f'<path d="M {sx} {sy} C {mx} {sy} {mx} {ny+nh/2} {ex} {ny+nh/2}" fill="none" stroke="{DIM}" stroke-width="0.9" stroke-dasharray="3 7" opacity="0.55"/>')
        s.append(f'<text x="{ex + (-10 if left else 10)}" y="{ny+nh/2+5}" text-anchor="{"end" if left else "start"}" font-family="{MONO}" font-size="15" fill="{DIM}">&#10005;</text>')

    # ── outgoing edges ─────────────────────────────────────────────────────
    out_y = ny + nh + 120
    for i, (colour, glyph, label, note) in enumerate(CONSEQUENCES):
        x = 200 + i * 470
        w = 420
        s.append(f'<path d="M {nx + nw/2} {ny + nh} C {nx + nw/2} {out_y-90} {x+w/2} {out_y-70} {x+w/2} {out_y}" fill="none" stroke="{colour}" stroke-width="1.6" opacity="0.6"/>')
        s.append(f'<rect x="{x}" y="{out_y}" width="{w}" height="150" fill="#FFFFFF" stroke="{colour}" stroke-width="1.4"/>')
        s.append(f'<text x="{x+22}" y="{out_y+44}" font-family="{MONO}" font-size="19" fill="{colour}">{glyph} {escape(label)}</text>')
        for k, line in enumerate(_wrap(note, 44)):
            s.append(f'<text x="{x+22}" y="{out_y+80+k*22}" font-family="{SANS}" font-size="16" fill="{DIM}">{escape(line)}</text>')

    # residual question card
    ry = out_y + 196
    s.append(f'<rect x="200" y="{ry}" width="2200" height="124" fill="#FFFFFF" stroke="{SPECIMEN}" stroke-width="1.6"/>')
    s.append(f'<text x="230" y="{ry+42}" font-family="{MONO}" font-size="18" fill="{SPECIMEN}">&#9873; RESIDUAL AFTER APPARATUS SUBTRACTION — the only question that needs a world-side X</text>')
    s.append(f'<text x="230" y="{ry+76}" font-family="{SANS}" font-size="18" fill="{INK}">Why did new own-name output stop in 2024 (0 non-deluxe rows) and return in 2025 as curation (3 release events, 4 rows, 2 features)?</text>')
    s.append(f'<text x="230" y="{ry+102}" font-family="{MONO}" font-size="12.5" fill="{DIM}">the repository records the packaging, the credits and the audits — nothing it holds can decide this question</text>')

    # legend / footer
    ly = ry + 190
    s.append(f'<line x1="60" y1="{ly-40}" x2="2540" y2="{ly-40}" stroke="{INK}" stroke-width="1" opacity="0.25"/>')
    lx = 60
    for cls in ("INSTRUMENT", "RECORD", "WORLD"):
        colour, glyph = CLASS_COLOURS[cls]
        s.append(f'<text x="{lx}" y="{ly}" font-family="{MONO}" font-size="14" fill="{colour}">{glyph} {cls}</text>')
        lx += 220
    s.append(f'<text x="{lx+40}" y="{ly}" font-family="{MONO}" font-size="14" fill="{DIM}">incoming edge colour = class of apparatus that generates the anomaly</text>')
    s.append(f'<text x="60" y="{ly+46}" font-family="{MONO}" font-size="12.5" fill="{DIM}">measured by tools/probe_missing_variable.py · machine-readable log docs/ghost-x/verification.json · palette README §00a (Okabe–Ito)</text>')
    s.append(f'<text x="60" y="{ly+76}" font-family="{MONO}" font-size="12.5" fill="{DIM}">the node is empty on purpose: a name would have to be earned by a measurement this repository does not contain</text>')
    s.append('</svg>\n')
    path.write_text("\n".join(s), encoding="utf-8")


def fig_graph(path: Path) -> None:
    """The vault's major knowledge graph, with the ghost node inserted and a
    numbered wire register in the manner of README §00c."""
    W, H = 2400, 2100
    s = [head(W, H, "THE MAJOR KNOWLEDGE GRAPH — WITH X INSERTED",
              "the same map as the Major Knowledge Graph note, plus one node · one dashed node added · seven numbered wires · dashed edges are the strange ones")]
    boxes: dict[str, tuple[float, float, float, float]] = {}
    pins: dict[str, tuple[float, float]] = {}

    def box(key, x, y, w, h, label, colour, dashed=False, blank=False, fs=18):
        boxes[key] = (x, y, w, h)
        dash = ' stroke-dasharray="12 8"' if dashed else ""
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#FFFFFF" stroke="{colour}" stroke-width="{2.4 if dashed else 1.3}"{dash}/>')
        if not blank:
            lines = label.split("|")
            for k, line in enumerate(lines):
                s.append(f'<text x="{x+w/2}" y="{y+h/2 + (k-(len(lines)-1)/2)*22 + 7}" text-anchor="middle" font-family="{SANS}" font-size="{fs}" fill="{INK}">{escape(line)}</text>')

    def wire(num, a, b, label, colour=None, side="right", label_side="above", dashed=True, lx=None, ly=None, anchor="middle"):
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        if side == "right":
            p1, p2 = (ax+aw, ay+ah/2), (bx, by+bh/2)
            c1, c2 = (p1[0]+120, p1[1]), (p2[0]-120, p2[1])
        elif side == "left":
            p1, p2 = (ax, ay+ah/2), (bx+bw, by+bh/2)
            c1, c2 = (p1[0]-120, p1[1]), (p2[0]+120, p2[1])
        else:
            p1, p2 = (ax+aw/2, ay+ah), (bx+bw/2, by)
            c1, c2 = (p1[0], p1[1]+80), (p2[0], p2[1]-80)
        col = colour or DIM
        d = ' stroke-dasharray="9 7"' if dashed else ""
        s.append(f'<path d="M {p1[0]} {p1[1]} C {c1[0]} {c1[1]} {c2[0]} {c2[1]} {p2[0]} {p2[1]}" fill="none" stroke="{col}" stroke-width="1.8"{d} opacity="0.9"/>')
        mx = (p1[0]+p2[0])/2 if lx is None else lx
        my = (p1[1]+p2[1])/2 if ly is None else ly
        pw = 13 + 8.2*len(label)
        s.append(f'<rect x="{mx-pw/2}" y="{my-19}" width="{pw}" height="26" fill="{PAPER}" opacity="0.94"/>')
        s.append(f'<text x="{mx}" y="{my}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{DIM}">{num} · {escape(label)}</text>')

    # ── band 1 · the practice ──────────────────────────────────────────────
    box("CP", 80, 760, 250, 110, "Creative|Practice", INK)
    children = ["Psychological System", "Music & Sonic Projects", "Film & Audiovisual",
                "Technology & Creative Systems", "Collaboration Systems", "Business & Curation",
                "Thought Experiments", "Goals, Workflows|& Open Questions"]
    keys = ["PSY", "MUSIC", "FILM", "TECH", "COLLAB", "BIZ", "THINK", "GOALS"]
    for i, (k, lab) in enumerate(zip(keys, children)):
        box(k, 380, 250 + i*146, 320, 106, lab, IDENTITY, fs=17)
        s.append(f'<path d="M 330 {760+55} C 356 {760+55} {352} {250+i*146+53} {380} {250+i*146+53}" fill="none" stroke="{INK}" stroke-width="1.1" opacity="0.75"/>')

    # ── band 2 · the ghost ─────────────────────────────────────────────────
    nx, ny, nw, nh = 940, 470, 520, 660
    s.append(ghost_glyph(nx + nw/2 - 74, ny - 128, 0.78, INK))
    s.append(f'<text x="{nx + nw/2 + 10}" y="{ny - 88}" text-anchor="middle" font-family="{SERIF}" font-size="42" fill="{INK}">X</text>')
    s.append(f'<text x="{nx + nw - 20}" y="{ny - 56}" text-anchor="end" font-family="{MONO}" font-size="13.5" fill="{DIM}">interior blank · identity withheld</text>')
    s.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="#FFFFFF" stroke="{INK}" stroke-width="2.6" stroke-dasharray="16 11"/>')
    boxes["X"] = (nx, ny, nw, nh)
    s.append(f'<text x="{nx + nw/2}" y="{ny + nh/2 - 6}" text-anchor="middle" font-family="{MONO}" font-size="13.5" fill="{DIM}">no glyph · no word</text>')
    s.append(f'<text x="{nx + nw/2}" y="{ny + nh/2 + 22}" text-anchor="middle" font-family="{MONO}" font-size="13.5" fill="{DIM}">no watermark</text>')
    s.append(f'<text x="{nx + nw/2}" y="{ny + nh + 36}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}">edges only — the blank node is the only element in this map with no contents</text>')

    # ── band 3 · the vault ─────────────────────────────────────────────────
    box("VAULT", 1760, 560, 330, 110, "Zaziopath Vault", INK)
    strata = [("REC", "AI Recursion Lab", RECURSION), ("SPEC", "Specimen Cabinet", SPECIMEN),
              ("MYTH", "Mythography", MYTH), ("EVID", "Evidence Audits", EVIDENCE),
              ("INDEX", "Indexes", "#B9B4AC")]
    for i, (k, lab, col) in enumerate(strata):
        box(k, 1760, 724 + i*138, 330, 108, lab, col, fs=17)
        s.append(f'<path d="M 1925 {560+110} L 1925 {724+i*138}" fill="none" stroke="{INK}" stroke-width="1.1" opacity="0.6"/>')
    box("LEDGER", 1760, 1450, 330, 120, "Stewardship Ledger|0 lines · no outbox", STEWARD, dashed=True, fs=17)

    # ── the numbered wires ─────────────────────────────────────────────────
    wire("①", "CP", "X", "systems, not receptions", dashed=False, lx=800, ly=866)
    wire("②", "MUSIC", "X", "which year counts as active (A6)", side="left", lx=800, ly=568)
    wire("③", "GOALS", "X", "why the ledger stays empty (A7)", side="left", lx=700, ly=1150)
    wire("④", "VAULT", "X", "five registers · no measurement", side="left", lx=1610, ly=980)
    wire("⑤", "EVID", "X", "compiled these anomalies", side="left", lx=1640, ly=1130, colour=EVIDENCE)
    wire("⑥", "X", "LEDGER", "the line that never arrives", colour=STEWARD, lx=1700, ly=1610)
    wire("⑦", "X", "INDEX", "the manifest names 336 · 2 present", side="left", lx=1560, ly=772, colour="#B9B4AC")

    # ── the register ───────────────────────────────────────────────────────
    ry = 1700
    s.append(f'<line x1="80" y1="{ry-40}" x2="2320" y2="{ry-40}" stroke="{INK}" stroke-width="1" opacity="0.3"/>')
    s.append(f'<text x="80" y="{ry}" font-family="{MONO}" font-size="15" fill="{INK}">WIRE REGISTER — source · mechanism · destination (README §00c convention, continued)</text>')
    rows = [
        ("①", "Creative Practice → X", "the practice is modelled as eight systems; none of them carries a reception term", "solid"),
        ("②", "Music & Sonic Projects → X", "the only series in the repo is packaging counts, which are properties of releases", "dashed"),
        ("③", "Goals, Workflows & Open Questions → X", "the terminal stratum has names for behaviour and no instrument that could record one", "dashed"),
        ("④", "Zaziopath Vault → X", "five strata re-describe the unknown in five registers; none measures it", "dashed"),
        ("⑤", "Evidence Audits → X", "the audits derive the anomalies and then classify them as psychology", "dashed"),
        ("⑥", "X → Stewardship Ledger", "every receipt format is defined; what a receipt would be filed about is unassigned", "dashed"),
        ("⑦", "X → Indexes", "the Inventory names 336 notes; two resolve here; the absent 334 are of a piece with X", "dashed"),
    ]
    for i, (num, path_, mech, style) in enumerate(rows):
        y = ry + 38 + i*34
        s.append(f'<text x="80" y="{y}" font-family="{MONO}" font-size="15" fill="{INK}">{num}</text>')
        s.append(f'<text x="130" y="{y}" font-family="{SANS}" font-size="16" fill="{INK}">{escape(path_)}</text>')
        s.append(f'<text x="620" y="{y}" font-family="{MONO}" font-size="14" fill="{DIM}">{escape(mech)}</text>')
        s.append(f'<text x="2280" y="{y}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">{style}</text>')
    s.append(f'<text x="80" y="{ry+300}" font-family="{MONO}" font-size="13" fill="{DIM}">full reading: the Major Knowledge Graph note · this node added by the X dossier · regenerate: python3 tools/generate_ghost_node.py</text>')
    s.append(f'<text x="80" y="{ry+330}" font-family="{MONO}" font-size="13" fill="{DIM}">the node is empty on purpose: naming X would require a measurement the repository does not contain, and inventing one would be the exact error the audits document</text>')
    s.append('</svg>\n')
    path.write_text("\n".join(s), encoding="utf-8")


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def rasterise(svg: Path) -> None:
    """Best-effort PNG preview. The SVG is canonical."""
    png = svg.with_suffix(".png")
    for cmd in (
        ["rsvg-convert", "-w", "2600", "-o", str(png), str(svg)],
        ["inkscape", str(svg), "--export-filename", str(png), "--export-width=2600"],
        ["convert", "-density", "144", str(svg), str(png)],
    ):
        exe = shutil.which(cmd[0])
        if not exe:
            continue
        r = subprocess.run([exe] + cmd[1:], capture_output=True, text=True)
        if r.returncode == 0 and png.exists():
            print(f"  wrote {png.relative_to(ROOT)}")
            return
    # @resvg/resvg-js, if a copy is reachable from the environment
    node = shutil.which("node")
    if node:
        script = (
            "const fs=require('fs');const p=process.argv[1];"
            "const {Resvg}=require(process.env.RESVG_PATH||'@resvg/resvg-js');"
            "const r=new Resvg(fs.readFileSync(process.argv[2]),{fitTo:{mode:'width',value:2600},font:{loadSystemFonts:true}});"
            "fs.writeFileSync(p,r.render().asPng());"
        )
        for mod in ("@resvg/resvg-js", "/tmp/rast/node_modules/@resvg/resvg-js"):
            r = subprocess.run([node, "-e", script, str(png), str(svg)],
                               capture_output=True, text=True,
                               env={**__import__("os").environ, "RESVG_PATH": mod})
            if r.returncode == 0 and png.exists():
                print(f"  wrote {png.relative_to(ROOT)} (resvg)")
                return
    print(f"  no rasteriser available — {svg.name} is canonical (browsers render it natively)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a = OUT / "figx_ghost_node.svg"
    b = OUT / "figx_ghost_in_graph.svg"
    fig_node(a)
    fig_graph(b)
    for p in (a, b):
        print(f"wrote {p.relative_to(ROOT)}")
        rasterise(p)


if __name__ == "__main__":
    main()
