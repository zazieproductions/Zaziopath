#!/usr/bin/env python3
"""Render README §00c as a publication-ready systems map.

The old §00c Mermaid graph asked an automatic layout engine to place 91 verbose
nodes and their cross-links.  The result was technically complete but visually
untraceable.  This renderer uses an editorial layout instead:

* the operating loop is shown once, left to right;
* nested lists encode containment without redundant connector lines;
* the five supporting systems share one aligned row;
* all 17 non-terminal “strange wires” are preserved in an indexed register.

The SVG is the canonical, zoomable figure.  When a compatible rasterizer is
available, a PNG preview is emitted for dependable rendering in GitHub's README.

Run:  python3 tools/generate_complex_map.py
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
SVG_PATH = OUT / "fig00c_complex_map.svg"
PNG_PATH = OUT / "fig00c_complex_map.png"

W, H = 2400, 2300

C = {
    "INDEX": "#231F20",
    "IDENTITY": "#0072B2",
    "SHADOW": "#CC79A7",
    "EVIDENCE": "#E69F00",
    "RECURSION": "#009E73",
    "STEWARDSHIP": "#56B4E9",
    "SPECIMENS": "#D55E00",
    "MYTHOGRAPHY": "#F0E442",
    "PRACTICE": "#FFFFFF",
    "PAPER": "#F7F6F2",
    "WHITE": "#FFFFFF",
    "INK": "#231F20",
    "MUTED": "#68635E",
    "RULE": "#CDC8BF",
}

GLYPH = {
    "INDEX": "◈",
    "IDENTITY": "◉",
    "SHADOW": "◐",
    "EVIDENCE": "▤",
    "RECURSION": "∞",
    "STEWARDSHIP": "△",
    "SPECIMENS": "⚠",
    "MYTHOGRAPHY": "☾",
    "PRACTICE": "◇",
}


def e(value: object) -> str:
    return escape(str(value), {'"': "&quot;"})


class SVG:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, raw: str) -> None:
        self.parts.append(raw)

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             stroke: str = "none", sw: float = 0, rx: float = 0,
             extra: str = "") -> None:
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'
        )

    def line(self, x1: float, y1: float, x2: float, y2: float, *,
             stroke: str, sw: float = 2, dash: str | None = None,
             marker: str | None = None, opacity: float = 1) -> None:
        attrs = []
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" '
            f'opacity="{opacity}" {" ".join(attrs)}/>'
        )

    def path(self, d: str, *, stroke: str, sw: float = 2,
             fill: str = "none", dash: str | None = None,
             marker: str | None = None, opacity: float = 1) -> None:
        attrs = []
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        self.add(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}" '
            f'{" ".join(attrs)}/>'
        )

    def circle(self, cx: float, cy: float, r: float, *, fill: str,
               stroke: str = "none", sw: float = 0) -> None:
        self.add(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(self, x: float, y: float, value: str, *, cls: str = "body",
             fill: str | None = None, anchor: str = "start",
             extra: str = "") -> None:
        # A CSS ``text { fill: … }`` rule outranks an SVG presentation
        # attribute.  Use an inline style so white-on-ink labels survive every
        # renderer (GitHub, librsvg, Sharp, and browsers).
        color = f' style="fill:{fill}"' if fill else ""
        self.add(
            f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"'
            f'{color} {extra}>{e(value)}</text>'
        )

    def render(self) -> str:
        return "\n".join(self.parts)


svg = SVG()

svg.add(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img"
     aria-labelledby="map-title map-description">
<title id="map-title">The Complex — Zaziopath systems map</title>
<desc id="map-description">A professionally typeset systems map of the Zaziopath vault. The top row traces self through the shadow engine and stewardship. Five supporting systems—practice, specimens, mythography, recursion, and evidence—feed a single convergence. An indexed register preserves seventeen non-terminal wires without crossing lines.</desc>
<defs>
  <marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="10" markerHeight="10" orient="auto-start-reverse">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="{C['INK']}"/>
  </marker>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#231F20" flood-opacity="0.08"/>
  </filter>
  <style>
    text {{ font-family: "DejaVu Sans", Arial, sans-serif; fill: {C['INK']}; }}
    .display {{ font-size: 72px; font-weight: 700; letter-spacing: -2px; }}
    .subtitle {{ font-size: 24px; font-weight: 400; fill: {C['MUTED']}; }}
    .eyebrow {{ font-family: "DejaVu Sans Mono", monospace; font-size: 17px; font-weight: 700; letter-spacing: 2.4px; }}
    .micro {{ font-family: "DejaVu Sans Mono", monospace; font-size: 15px; font-weight: 400; letter-spacing: 0.8px; fill: {C['MUTED']}; }}
    .section {{ font-size: 28px; font-weight: 700; letter-spacing: -0.3px; }}
    .card-title {{ font-size: 31px; font-weight: 700; letter-spacing: -0.5px; }}
    .card-copy {{ font-size: 19px; font-weight: 400; }}
    .card-key {{ font-family: "DejaVu Sans Mono", monospace; font-size: 15px; font-weight: 700; letter-spacing: 1.2px; }}
    .body {{ font-size: 20px; font-weight: 400; }}
    .body-bold {{ font-size: 20px; font-weight: 700; }}
    .wire-title {{ font-size: 18px; font-weight: 700; }}
    .wire-copy {{ font-size: 16px; font-weight: 400; fill: {C['MUTED']}; }}
    .wire-num {{ font-family: "DejaVu Sans Mono", monospace; font-size: 15px; font-weight: 700; }}
    .convergence {{ font-size: 43px; font-weight: 700; letter-spacing: -0.8px; }}
    .convergence-copy {{ font-size: 21px; font-weight: 400; }}
  </style>
</defs>''')

# Paper and a restrained registration grid.
svg.rect(0, 0, W, H, fill=C["PAPER"])
for x in (72, 552, 1032, 1512, 1992, 2328):
    svg.line(x, 36, x, H - 42, stroke=C["RULE"], sw=1, opacity=0.18)

# Header.
svg.text(72, 72, "§00C  /  SYSTEM TOPOLOGY", cls="eyebrow")
svg.text(72, 157, "THE COMPLEX", cls="display")
svg.text(72, 205, "Every wire, one legible map — from interior system to observable behaviour.", cls="subtitle")
svg.text(2328, 72, "ZAZIOPATH  ·  MAP 02", cls="eyebrow", anchor="end")
svg.text(2328, 106, "DRAWN 2026-09-02  /  EDITORIAL LAYOUT", cls="micro", anchor="end")

# Small count chips.
def count_chip(x: float, y: float, w: float, label: str, value: str) -> None:
    svg.rect(x, y, w, 44, fill=C["WHITE"], stroke=C["RULE"], sw=1, rx=22)
    svg.text(x + 18, y + 28, value, cls="card-key")
    svg.text(x + w - 18, y + 28, label, cls="micro", anchor="end")

count_chip(1402, 146, 196, "STRATA", "08")
count_chip(1614, 146, 226, "INDEXED WIRES", "17")
count_chip(1856, 146, 246, "TERMINAL FEEDS", "08")
count_chip(2118, 146, 210, "FEEDBACK LOOP", "01")

# Reading key.
svg.line(72, 248, 160, 248, stroke=C["INK"], sw=3, marker="arrow")
svg.text(178, 254, "OPERATING FLOW", cls="micro")
svg.line(386, 248, 474, 248, stroke=C["INK"], sw=2, dash="8 9")
svg.text(492, 254, "INDEXED WIRE", cls="micro")
svg.path("M 760 250 C 800 218, 844 218, 884 250", stroke=C["MUTED"], sw=2,
         dash="3 8", marker="arrow")
svg.text(904, 254, "FEEDBACK", cls="micro")
svg.text(2328, 254, "COLOUR + GLYPH ALWAYS TRAVEL TOGETHER", cls="micro", anchor="end")

# Main operating cards.
CARD_Y, CARD_H, CARD_W = 314, 302, 720
CARD_X = [72, 840, 1608]


def main_card(x: int, key: str, stage: str, title: str,
              kicker: str, rows: list[tuple[str, str]]) -> None:
    svg.rect(x, CARD_Y, CARD_W, CARD_H, fill=C["WHITE"], stroke=C["RULE"], sw=1,
             rx=12, extra='filter="url(#shadow)"')
    svg.rect(x, CARD_Y, 12, CARD_H, fill=C[key], rx=6)
    svg.text(x + 34, CARD_Y + 36, f"{stage}  /  {GLYPH[key]} {key}", cls="card-key",
             fill=C[key] if key != "STEWARDSHIP" else C["IDENTITY"])
    svg.text(x + 34, CARD_Y + 84, title, cls="card-title")
    svg.text(x + CARD_W - 30, CARD_Y + 82, kicker, cls="micro", anchor="end")
    svg.line(x + 34, CARD_Y + 108, x + CARD_W - 30, CARD_Y + 108,
             stroke=C["RULE"], sw=1)
    y = CARD_Y + 145
    for label, value in rows:
        svg.text(x + 34, y, label, cls="card-key", fill=C["MUTED"])
        svg.text(x + 192, y, value, cls="card-copy")
        y += 39


main_card(CARD_X[0], "IDENTITY", "01 · INPUT", "The person under the lens", "SUBJECT = ANALYST", [
    ("TYPOLOGY", "INFP-T · 4w5/458 · EII · ELVF"),
    ("COGNITION", "pattern + symbolic thinking · ambiguity tolerance"),
    ("PRESSURE", "avoidance · perfectionism · rumination · shame"),
    ("INNER CAST", "Hubris · Tweak Tweak · Babyheart · Tuffy"),
])
main_card(CARD_X[1], "SHADOW", "02 · EXCAVATE", "The shadow engine", "COMPENDIUM CH. 2–18", [
    ("FORMS", "30 shadow selves · 35 dark alternate selves"),
    ("OPERATORS", "88 incoming operators + alluring figures"),
    ("MECHANICS", "quiet rhetorics · distortions · money scams"),
    ("TEST", "when insight becomes control of meaning"),
])
main_card(CARD_X[2], "STEWARDSHIP", "03 · ACT", "The Tuesday self", "PIVOT > INSIGHT", [
    ("CROSSWALK", "shadow ↔ light · chapters 20 + 22"),
    ("EXECUTE", "twelve questions before sending or signing"),
    ("CALIBRATE", "false-positive discipline · anti-paranoia"),
    ("ENDPOINT", "the Strange Humane Architect"),
])

# Main flow connectors, drawn prominently across gutters.
svg.line(792, 465, 834, 465, stroke=C["INK"], sw=4, marker="arrow")
svg.line(1560, 465, 1602, 465, stroke=C["INK"], sw=4, marker="arrow")
svg.text(816, 438, "NAME", cls="micro", anchor="middle")
svg.text(1584, 438, "PIVOT", cls="micro", anchor="middle")

# Supporting systems.
svg.text(72, 684, "THE FIVE SUPPORTING SYSTEMS", cls="section")
svg.text(1780, 684, "CONTAINMENT = NESTING  /  RELATIONSHIPS = REGISTER BELOW", cls="micro", anchor="end")

SUP_Y, SUP_H, SUP_W, GAP = 718, 346, 432, 24
SUP_X = [72 + i * (SUP_W + GAP) for i in range(5)]


def support_card(x: int, key: str, title: str, subtitle: str,
                 items: list[tuple[str, str]]) -> None:
    svg.rect(x, SUP_Y, SUP_W, SUP_H, fill=C["WHITE"], stroke=C["RULE"], sw=1, rx=10)
    svg.rect(x, SUP_Y, SUP_W, 9, fill=C[key])
    svg.text(x + 24, SUP_Y + 42, f"{GLYPH[key]}  {title.upper()}", cls="card-key",
             fill=C[key] if key not in ("MYTHOGRAPHY", "PRACTICE") else C["INK"])
    svg.text(x + 24, SUP_Y + 72, subtitle, cls="micro")
    svg.line(x + 24, SUP_Y + 92, x + SUP_W - 24, SUP_Y + 92, stroke=C["RULE"], sw=1)
    y = SUP_Y + 125
    for label, value in items:
        svg.circle(x + 29, y - 5, 5, fill=C[key], stroke=C["INK"] if key == "PRACTICE" else "none", sw=1)
        svg.text(x + 44, y, label, cls="body-bold")
        svg.text(x + 44, y + 25, value, cls="wire-copy")
        y += 52


support_card(SUP_X[0], "PRACTICE", "Practice", "the engine's material", [
    ("Music", "methods · set theory · 4×3 modules"),
    ("Film", "horror scoring · cues · delivery"),
    ("Systems", "local AI · creative code · archive glue"),
    ("Work", "curation · rates · collaboration · next act"),
])
support_card(SUP_X[1], "SPECIMENS", "Specimens", "read-only / defence", [
    ("Infiltration", "neuroviral + infoparasite models"),
    ("Social engineering", "six annotated outreach postures"),
    ("Wealth blueprints", "scarcity-alchemist economics"),
    ("Omnivisionary", "cascaded leverage, filed under glass"),
])
support_card(SUP_X[2], "MYTHOGRAPHY", "Mythography", "worldbuilding arm", [
    ("Specificity", "MSS-E · Vespertine · constructed tongues"),
    ("Permutation", "Identity Castles · Hypostasis"),
    ("Sovereignty", "Matrix protocol · branding Psy-Ops"),
    ("Tender horror", "Munnytown · Signal Rot Atlas"),
])
support_card(SUP_X[3], "RECURSION", "Recursion lab", "machines on the self", [
    ("Tribunal", "jurisdiction · evidence · report format"),
    ("Memory", "GPT 7.7-t ↔ 604-line export"),
    ("Counterference", "the answer before the question"),
    ("Safety interlock", "recursion depth ≤ 3, then surface"),
])
support_card(SUP_X[4], "EVIDENCE", "Evidence", "record > mood", [
    ("Discography", "200 tracks · 165 ISRCs · 82.5%"),
    ("Media census", "133 verified URL-level records"),
    ("Surface audit", "Instagram report ZP-IG-2026-0819"),
    ("Case file", "10 findings · FIG 0–7 · one palette"),
])

# Terminal bus: each system has an explicit, aligned feed rather than diagonal spaghetti.
BUS_Y = 1100
for x, key in zip(SUP_X, ("PRACTICE", "SPECIMENS", "MYTHOGRAPHY", "RECURSION", "EVIDENCE")):
    cx = x + SUP_W / 2
    svg.line(cx, SUP_Y + SUP_H, cx, BUS_Y, stroke=C[key], sw=4)
    svg.circle(cx, BUS_Y, 8, fill=C[key], stroke=C["INK"], sw=1)
svg.line(SUP_X[0] + SUP_W / 2, BUS_Y, SUP_X[-1] + SUP_W / 2, BUS_Y,
         stroke=C["INK"], sw=3)
svg.text(72, BUS_Y + 6, "TERMINAL FEEDS", cls="micro")

# Convergence panel.
CONV_Y, CONV_H = 1140, 228
svg.rect(72, CONV_Y, 2256, CONV_H, fill=C["INK"], rx=12)
svg.text(108, CONV_Y + 49, "◈  THE CONVERGENCE", cls="card-key", fill=C["WHITE"])
svg.text(108, CONV_Y + 109, "SHADOW  →  SIGNAL  →  STEWARDSHIP", cls="convergence", fill=C["WHITE"])
svg.text(108, CONV_Y + 153,
         "Traits crosswalked · schemes under glass · worlds entered and left freely.",
         cls="convergence-copy", fill=C["WHITE"])
svg.text(108, CONV_Y + 191, "OPEN QUESTION", cls="card-key", fill=C["RULE"])
svg.text(304, CONV_Y + 191, "Which part runs the institution?", cls="convergence-copy", fill=C["WHITE"])

# Eight labelled terminal feeds make the convergence semantics explicit.  The
# former graph hid these phrases on long diagonals; here they read as a small
# connection schedule inside the destination itself.
feed_specs = [
    ("IDENTITY", "examined under every lens"),
    ("SHADOW", "the governing question"),
    ("PRACTICE", "worlds entered + left freely"),
    ("SPECIMENS", "filed, never used"),
    ("MYTHOGRAPHY", "raw material / evidence-checked"),
    ("RECURSION", "dated loop artifact"),
    ("EVIDENCE", "record outlives mood"),
    ("STEWARDSHIP", "behaviour, dated + filed"),
]
feed_x0, feed_y0, feed_w, feed_h, feed_gap = 1132, CONV_Y + 28, 278, 68, 16
for i, (key, description) in enumerate(feed_specs):
    col, row = i % 4, i // 4
    fx = feed_x0 + col * (feed_w + feed_gap)
    fy = feed_y0 + row * (feed_h + 12)
    svg.rect(fx, fy, feed_w, feed_h, fill="#302D2E", stroke="#625D5F", sw=1, rx=7)
    svg.rect(fx, fy, 7, feed_h, fill=C[key], rx=3)
    svg.text(fx + 20, fy + 25, f"{GLYPH[key]}  {key}", cls="card-key", fill=C["WHITE"])
    svg.text(fx + 20, fy + 51, description, cls="micro", fill=C["RULE"])

# Main stewardship arrow into convergence.  Its origin is aligned to the
# gutter between Recursion and Evidence, so it never strikes through a card.
gutter_x = SUP_X[3] + SUP_W + GAP / 2
svg.line(gutter_x, CARD_Y + CARD_H, gutter_x, CONV_Y - 10,
         stroke=C["STEWARDSHIP"], sw=4, marker="arrow")
# The one feedback route sits outside the content grid and returns to the
# shadow engine.  A dotted line is therefore functional, not decorative.
svg.path(
    f"M 2312 {CONV_Y + 112} C 2370 {CONV_Y + 112}, 2370 286, 2268 286 "
    f"L 1240 286 C 1218 286, 1200 298, 1200 314",
    stroke=C["MUTED"], sw=2.5, dash="4 9", marker="arrow"
)
svg.rect(1768, 266, 344, 38, fill=C["PAPER"], rx=19)
svg.text(1940, 291, "NEXT PATTERN  /  LOOP RESTARTS", cls="micro", anchor="middle")

# Indexed relationship-wire register.
WIRE_TOP = 1450
svg.text(72, WIRE_TOP, "INDEXED WIRE REGISTER", cls="section")
svg.text(72, WIRE_TOP + 35,
         "All 17 non-terminal strange wires, indexed instead of overprinted. Read source → mechanism → destination.",
         cls="subtitle")
svg.text(2328, WIRE_TOP + 35, "17 / 17 ACCOUNTED FOR", cls="eyebrow", anchor="end")

wires = [
    ("IDENTITY", "SHADOW PROFILE", "defines the exact attack surface", "SHADOW", "MONEY-SCAM MODELS"),
    ("IDENTITY", "ARMOURED PERFORMANCE", "recruits insight as rank", "SHADOW", "SHADOW ENGINE"),
    ("IDENTITY", "META-LEVEL ADDICTION", "meets the depth-three safety cap", "RECURSION", "RECURSION STAIRCASE"),
    ("IDENTITY", "TUFFY BUNNYTOWN", "turns inner parts into holdable lore", "MYTHOGRAPHY", "MYTHOGRAPHIC CHILDHOOD"),
    ("IDENTITY", "SOVEREIGN ANARCHISM", "dramatizes the inversion finding", "MYTHOGRAPHY", "MATRIX PROTOCOL"),
    ("STEWARDSHIP", "SHADOW/LIGHT CROSSWALK", "reappears as production structure", "PRACTICE", "4 × 3 ALBUM MODULES"),
    ("STEWARDSHIP", "SHADOW/LIGHT CROSSWALK", "turns pivots into executable code", "STEWARDSHIP", "TWELVE QUESTIONS"),
    ("SHADOW", "SHADOW ENGINE", "turns quiet rhetorics outward as tools", "SPECIMENS", "COGNITIVE INFILTRATION"),
    ("SHADOW", "TEN MONEY SCAMS", "reappears annotated and under glass", "SPECIMENS", "SOCIAL-ENGINEERING TEMPLATES"),
    ("PRACTICE", "Z-RELATED COMPOSITION", "permutes identical material into new selves", "MYTHOGRAPHY", "IDENTITY CASTLES"),
    ("PRACTICE", "DECAY STUDIES", "aestheticizes entropy as the medium", "MYTHOGRAPHY", "SIGNAL ROT ATLAS"),
    ("PRACTICE", "DECAY STUDIES", "fights entropy with administration", "EVIDENCE", "ISRC CATALOG"),
    ("SPECIMENS", "SOCIAL-ENGINEERING TEMPLATES", "uses the same craft, aimed outward", "MYTHOGRAPHY", "BRANDING PSY-OPS"),
    ("MYTHOGRAPHY", "IDENTITY CASTLES", "is statistically refuted by identifiers", "EVIDENCE", "CATALOG EVIDENCE"),
    ("MYTHOGRAPHY", "MYTH WORKSHOP", "fuels the tribunal that reads it back", "RECURSION", "AI TRIBUNAL"),
    ("RECURSION", "GPT 7.7-T", "holds machine memory in two directions", "RECURSION", "MEMORY EXPORT"),
    ("EVIDENCE", "EVIDENCE BENCH", "replaces self-claims with counts", "STEWARDSHIP", "THE TUESDAY SELF"),
]

COL_X = [72, 840, 1608]
ROW_Y0, ROW_H, ROW_GAP = 1538, 105, 10


def wire_item(index: int, x: int, y: int, source_key: str, source: str,
              relation: str, target_key: str, target: str) -> None:
    w = 720
    svg.rect(x, y, w, ROW_H, fill=C["WHITE"], stroke=C["RULE"], sw=1, rx=8)
    svg.rect(x, y, 8, ROW_H, fill=C[source_key], rx=4)
    svg.circle(x + 38, y + 31, 18, fill=C["INK"])
    svg.text(x + 38, y + 36, f"{index:02d}", cls="wire-num", fill=C["WHITE"], anchor="middle")
    svg.circle(x + 72, y + 27, 7, fill=C[source_key], stroke=C["INK"], sw=1)
    svg.text(x + 88, y + 33, source, cls="wire-title")
    # A compact three-line connection schedule scales to long names without
    # collisions: source, mechanism, then destination.
    svg.text(x + 88, y + 61, relation, cls="wire-copy")
    svg.circle(x + 92, y + 84, 6, fill=C[target_key], stroke=C["INK"], sw=1)
    svg.text(x + 108, y + 90, f"→  {target}", cls="wire-title")

for idx, wire in enumerate(wires, start=1):
    col = (idx - 1) // 6
    row = (idx - 1) % 6
    wire_item(idx, COL_X[col], ROW_Y0 + row * (ROW_H + ROW_GAP), *wire)

# Footer and provenance.
footer_y = 2254
svg.line(72, footer_y - 29, 2328, footer_y - 29, stroke=C["RULE"], sw=1)
svg.text(72, footer_y, "ZAZIOPATH  ·  §00C  ·  SYSTEMS MAP", cls="eyebrow")
svg.text(1200, footer_y, "SOURCE: README §00C + ⚡ UNEXPECTED CONNECTIONS", cls="micro", anchor="middle")
svg.text(2328, footer_y, "OKABE–ITO  /  COLOUR NEVER ENCODES ALONE", cls="micro", anchor="end")

svg.add("</svg>")

OUT.mkdir(parents=True, exist_ok=True)
SVG_PATH.write_text(svg.render(), encoding="utf-8")
print(f"wrote {SVG_PATH.relative_to(ROOT)}")

def run_quiet(command: list[str]) -> bool:
    """Run a rasterizer without making SVG generation depend on it."""
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


rasterized = False
rsvg = shutil.which("rsvg-convert")
if rsvg:
    rasterized = run_quiet([
        rsvg, "--background-color", C["PAPER"], "--width", str(W),
        "--height", str(H), "--output", str(PNG_PATH), str(SVG_PATH),
    ])

# ImageMagick installations sometimes advertise an SVG delegate that is not
# actually present, so failure here is deliberately non-fatal.
convert = shutil.which("convert") or shutil.which("magick")
if not rasterized and convert:
    rasterized = run_quiet([
        convert, "-background", C["PAPER"], "-density", "96",
        str(SVG_PATH), "-strip", f"PNG24:{PNG_PATH}",
    ])

# Sharp bundles its own SVG renderer and is the portable final fallback.  npx
# may download it on the first run; the generated artifact itself has no JS or
# network dependency.
npx = shutil.which("npx")
if not rasterized and npx:
    rasterized = run_quiet([
        npx, "--yes", "sharp-cli", "-i", str(SVG_PATH), "-o",
        str(PNG_PATH), "--format", "png",
    ])

if rasterized:
    print(f"wrote {PNG_PATH.relative_to(ROOT)}")
else:
    print("PNG rasterizer unavailable; SVG is complete. See the module docstring.")
