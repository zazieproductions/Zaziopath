#!/usr/bin/env python3
"""
Zaziopath — diagram generator.

Renders the PNG charts in this folder from the numbers in the README and the
files actually committed at the repo root.  Re-run after the vault changes:

    python3 diagrams/generate_diagrams.py

Requires matplotlib (pip install matplotlib).
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

OUT = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# palette — "Information Gothic" / alchemical
# --------------------------------------------------------------------------
BG        = "#0d0d0f"
PANEL     = "#151518"
INK       = "#d8cfb8"   # bone
MUTED     = "#8f897c"
FAINT     = "#5a564e"
GRID      = "#27272c"

NIGREDO    = "#2a2a2e"  # blackening
ALBEDO     = "#d9d4c7"  # whitening
CITRINITAS = "#c8a14a"  # yellowing  (gold)
RUBEDO     = "#a23b3b"  # reddening  (crimson)
ASH        = "#6f8383"  # dusty teal
GOLD_HI    = "#e2cb80"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": GRID,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "savefig.dpi": 200,
    "font.size": 10,
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("wrote", path)


def title(ax, text, sub=None, x=0.0, y=1.02, size=13):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=size,
            fontweight="bold", color=INK, va="bottom", ha="left")
    if sub:
        ax.text(x, y - 0.09, sub, transform=ax.transAxes, fontsize=8.5,
                color=MUTED, va="top", ha="left", style="italic")


def footer(fig, text):
    fig.text(0.99, 0.01, text, ha="right", va="bottom", fontsize=7.5,
             color=FAINT, style="italic")


def stage_swatch(ax, x=0.0, y=1.0):
    """A four-colour alchemy key along the top of a panel."""
    steps = [("NIGREDO", NIGREDO), ("ALBEDO", ALBEDO),
             ("CITRINITAS", CITRINITAS), ("RUBEDO", RUBEDO)]
    for i, (name, col) in enumerate(steps):
        dx = x + i * 0.25
        ax.plot([dx, dx + 0.21], [y, y], color=col, lw=4,
                transform=ax.transAxes, solid_capstyle="butt")
        ax.text(dx + 0.105, y - 0.03, name, transform=ax.transAxes,
                fontsize=6.5, color=col, ha="center", va="top")


# ==========================================================================
# 1 · VAULT MAP — what is actually committed, grouped by category
# ==========================================================================
def vault_map():
    fig, (axL, axR) = plt.subplots(
        1, 2, figsize=(12.6, 6.2),
        gridspec_kw={"width_ratios": [1.32, 1.0], "wspace": 0.34})

    groups = [
        ("CORE · the spine", CITRINITAS, [
            ("Shadow / Signal / Stewardship\n  Mega Compendium", 222),
            ("Shadow Journal Observations", 20),
            ("Ideological Inversion Audit", 12),
            ("Identity · Typological Vault", 6),
        ]),
        ("RECURSIVE A.I. · the experiments", ASH, [
            ("THE OMNIVISIONARY GROK OUTPUT", 19),
            ("GPT 7.7-t Surveillance Subroutine", 9),
            ("Discoveries · Genius / Hybrid", 7),
            ("Counterference Engine", 6),
        ]),
        ("CASE STUDY · the evidence", RUBEDO, [
            ("Instagram Forensic Audit", 21),
            ("Media Master · public census", 14),
        ]),
    ]

    # left panel — PDFs by page count --------------------------------------
    rows = []
    for gname, gcol, items in groups:
        for label, pages in items:
            rows.append((label, pages, gcol))
    n = len(rows)
    ys = list(range(n))[::-1]
    bars = axL.barh(ys, [r[1] for r in rows],
                    color=[r[2] for r in rows], height=0.62,
                    edgecolor=BG, linewidth=0)
    for y, (label, pages, _col) in zip(ys, rows):
        axL.text(pages - 6, y, f"{pages}", va="center", ha="right",
                 fontsize=9, color=INK, fontweight="bold")
    axL.set_yticks(ys)
    axL.set_yticklabels([r[0] for r in rows], fontsize=8.4)
    axL.set_xlim(0, 250)
    axL.set_xticks([0, 50, 100, 150, 200])
    axL.tick_params(axis="x", labelsize=8)
    axL.set_xlabel("pages", fontsize=8)
    axL.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        axL.spines[spine].set_visible(False)

    # group separators + labels
    ycursor = n
    for gname, gcol, items in groups:
        ytop = ycursor - 0.5
        ybot = ycursor - len(items) + 0.5
        axL.plot([0, 250], [ybot - 0.55, ybot - 0.55], color=GRID, lw=0.8)
        axL.text(250, (ytop + ybot) / 2, gname, va="center", ha="right",
                 fontsize=7.5, color=gcol, fontweight="bold", rotation=0)
        ycursor -= len(items)
    axL.text(0.0, 1.06, "VAULT MAP — 10 PDFs · 336 pages",
             transform=axL.transAxes, fontsize=13, fontweight="bold", color=INK)
    axL.text(0.0, 0.975, "what is actually committed at the repo root, by page count",
             transform=axL.transAxes, fontsize=8.5, color=MUTED, style="italic")

    # right panel — the rest, by measure -----------------------------------
    artifacts = [
        ("JSON memory re-export", 604, "lines", ALBEDO),
        ("Discography workbook", 200, "tracks", CITRINITAS),
        ("Social Engineering Templates", 92, "lines", ASH),
        ("greyhat · profile layer", 81, "lines", FAINT),
    ]
    ays = list(range(len(artifacts)))[::-1]
    cols = [a[3] for a in artifacts]
    axR.barh(ays, [a[1] for a in artifacts], color=cols, height=0.62,
             edgecolor=BG)
    for y, (name, val, unit, _c) in zip(ays, artifacts):
        axR.text(val + 12, y, f"{val} {unit}", va="center", ha="left",
                 fontsize=9, color=INK, fontweight="bold")
    axR.set_yticks(ays)
    axR.set_yticklabels([a[0] for a in artifacts], fontsize=8.4)
    axR.set_xlim(0, 660)
    axR.set_xticks([0, 200, 400, 600])
    axR.tick_params(axis="x", labelsize=8)
    axR.set_xlabel("count", fontsize=8)
    axR.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        axR.spines[spine].set_visible(False)
    axR.text(0.0, 1.06, "THE REST — by measure",
             transform=axR.transAxes, fontsize=13, fontweight="bold", color=INK)
    axR.text(0.0, 0.975, "spreadsheet, memory export, templates, profile layer",
             transform=axR.transAxes, fontsize=8.5, color=MUTED, style="italic")

    footer(fig, "ZAZIOPATH · every count dated, every finding tiered")
    save(fig, "vault-map.png")


# ==========================================================================
# 2 · ARCHETYPE COSMOLOGY — ~250 named archetypes, by compendium chapter
# ==========================================================================
def cosmology():
    fig, ax = plt.subplots(figsize=(11.4, 6.6))
    data = [
        ("ch. 2 · shadow-Zazie forms + 3 composites", 33, NIGREDO),
        ("ch. 6–8 · incoming operators", 49, RUBEDO),
        ("ch. 9–10 · alluring figures + Milo Grey", 39, RUBEDO),
        ("ch. 15 · deeper distortions", 26, NIGREDO),
        ("ch. 17 · shadow archetypes no test measures", 18, NIGREDO),
        ("ch. 20 · light-triad counter-archetypes", 17, ALBEDO),
        ("ch. 14 · Zazie's own shadow rhetorics", 17, NIGREDO),
        ("ch. 4 · sociopathic AUs", 12, NIGREDO),
        ("ch. 5 · malicious-online AUs", 12, NIGREDO),
        ("ch. 3 · high-psychopathy AUs", 11, NIGREDO),
        ("ch. 12 · money scams", 10, RUBEDO),
        ("ch. 18 · the six parts beneath the rhetoric", 6, ALBEDO),
    ]
    data.sort(key=lambda d: d[1])
    labels = [d[0] for d in data]
    vals = [d[1] for d in data]
    cols = [d[2] for d in data]
    ys = range(len(data))
    ax.barh(list(ys), vals, color=cols, height=0.66, edgecolor=BG)
    for y, v in zip(ys, vals):
        ax.text(v + 1, y, str(v), va="center", ha="left", fontsize=9,
                color=INK, fontweight="bold")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=8.2)
    ax.set_xlim(0, 56)
    ax.set_xticks(range(0, 56, 10))
    ax.tick_params(axis="x", labelsize=8)
    ax.set_xlabel("named archetypes / personas", fontsize=8.5)
    ax.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)

    title(ax, "THE SHADOW COSMOLOGY — ≈250 named archetypes",
          sub="counted from the compendium table of contents · dark forms in black, operators in crimson, light counterparts in white")
    footer(fig, "ZAZIOPATH · the single move: every dark archetype has a light counterpart")
    save(fig, "archetype-cosmology.png")


# ==========================================================================
# 3 · THE SUBJECT — Big Five radar + shadow-profile bars
# ==========================================================================
def typology():
    fig = plt.figure(figsize=(12.6, 5.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.25], wspace=0.16)

    # --- Big Five radar ---------------------------------------------------
    ax = fig.add_subplot(gs[0], projection="polar")
    traits = ["Openness", "Neuroticism", "Conscientiousness",
              "Agreeableness", "Extraversion"]
    scores = [90, 90, 60, 55, 30]     # very high / very high / moderate / moderate / low
    qual   = ["very high", "very high", "moderate", "moderate", "low"]
    N = len(traits)
    theta = [i * 2 * math.pi / N for i in range(N)]
    theta += theta[:1]
    scores_c = scores + scores[:1]
    ax.plot(theta, scores_c, color=CITRINITAS, lw=2)
    ax.fill(theta, scores_c, color=CITRINITAS, alpha=0.18)
    ax.set_xticks(theta[:-1])
    ax.set_xticklabels([f"{t}\n({q})" for t, q in zip(traits, qual)],
                       fontsize=8.2, color=INK)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=6.5, color=MUTED)
    ax.grid(color=GRID, lw=0.6, alpha=0.8)
    ax.spines["polar"].set_color(GRID)
    ax.set_facecolor(BG)
    ax.text(0.5, 1.12, "BIG FIVE — self-report", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=INK, ha="center")
    ax.text(0.5, 1.03, "0–100 scale · qualitative labels from the vault",
            transform=ax.transAxes, fontsize=7.5, color=MUTED, ha="center",
            style="italic")

    # --- Shadow profile bars ---------------------------------------------
    ax2 = fig.add_subplot(gs[1])
    prof = [
        ("Self-criticism", 100, "extremely high", RUBEDO),
        ("Rumination", 90, "very high", ASH),
        ("Perfectionism", 90, "very high", ASH),
        ("Schizotypal traits", 90, "very high", ASH),
        ("Avoidant traits", 90, "very high", ASH),
        ("Vulnerable narcissism", 90, "very high", RUBEDO),
        ("Light Triad", 80, "high", CITRINITAS),
        ("Peter Pan Complex", 65, "65%", ASH),
        ("Grandiose narcissism", 40, "moderate-low", RUBEDO),
        ("Sadism", 20, "low", RUBEDO),
        ("Dark Triad", 20, "low", RUBEDO),
    ]
    ys = list(range(len(prof)))[::-1]
    ax2.barh(ys, [p[1] for p in prof], color=[p[3] for p in prof],
             height=0.62, edgecolor=BG)
    for y, (name, val, q, _c) in zip(ys, prof):
        ax2.text(val + 2.5, y, f"{q}", va="center", ha="left",
                 fontsize=8.4, color=INK)
    ax2.set_yticks(ys)
    ax2.set_yticklabels([p[0] for p in prof], fontsize=8.6)
    ax2.set_xlim(0, 130)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.tick_params(axis="x", labelsize=8)
    ax2.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        ax2.spines[spine].set_visible(False)
    ax2.text(0.0, 1.06, "SHADOW PROFILE — the load-bearing traits",
             transform=ax2.transAxes, fontsize=12, fontweight="bold", color=INK)
    ax2.text(0.0, 0.985, "crimson = dark-triad family · gold = light triad · ash = regulatory load",
             transform=ax2.transAxes, fontsize=7.6, color=MUTED, style="italic")

    footer(fig, "ZAZIOPATH · self-report and observation, not diagnosis · Identity · Typological Vault")
    save(fig, "subject-typology.png")


# ==========================================================================
# 4 · CASE-STUDY FLOOR — the evidence that cannot be argued away
# ==========================================================================
def case_study():
    fig = plt.figure(figsize=(13.0, 4.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 0.95], wspace=0.18)

    # --- ISRC coverage donut ---------------------------------------------
    ax = fig.add_subplot(gs[0])
    verified, unverified = 165, 35
    ax.pie([verified, unverified], colors=[CITRINITAS, GRID],
           startangle=90, counterclock=False,
           wedgeprops={"width": 0.42, "edgecolor": BG, "linewidth": 1.5})
    ax.text(0, 0.12, "82.5%", ha="center", va="center", fontsize=22,
            fontweight="bold", color=GOLD_HI)
    ax.text(0, -0.22, "of 200 tracks\ncarry a verified ISRC", ha="center",
            va="center", fontsize=8.4, color=MUTED)
    ax.text(0.5, 1.16, "OUTPUT — the discography", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=INK, ha="center")
    ax.text(0.5, 1.06, "165 verified · 2019–2026 · 58 Discogs appearances",
            transform=ax.transAxes, fontsize=7.6, color=MUTED, ha="center",
            style="italic")

    # --- Media-master priority tiers -------------------------------------
    ax2 = fig.add_subplot(gs[1])
    tiers = [("A · core editorial / film", 23, CITRINITAS),
             ("B · secondary press", 26, ALBEDO),
             ("C · compilations / profiles", 84, ASH)]
    tys = [2, 1, 0]
    ax2.barh(tys, [t[1] for t in tiers], color=[t[2] for t in tiers],
             height=0.6, edgecolor=BG)
    for y, (name, val, _c) in zip(tys, tiers):
        ax2.text(val + 2, y, f"{val}", va="center", ha="left", fontsize=10,
                 color=INK, fontweight="bold")
    ax2.set_yticks(tys)
    ax2.set_yticklabels([t[0] for t in tiers], fontsize=8.6)
    ax2.set_xlim(0, 96)
    ax2.set_xticks([0, 25, 50, 75])
    ax2.tick_params(axis="x", labelsize=8)
    ax2.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        ax2.spines[spine].set_visible(False)
    ax2.text(0.0, 1.16, "RECORD — the public census", transform=ax2.transAxes,
             fontsize=12, fontweight="bold", color=INK)
    ax2.text(0.0, 1.05, "133 verified records · 15 unverified leads held out",
             transform=ax2.transAxes, fontsize=7.6, color=MUTED, style="italic")

    # --- Instagram audit coverage ----------------------------------------
    ax3 = fig.add_subplot(gs[2])
    ig = [("grid posts evidenced", 14, 29),
          ("tagged-tab items", 8, None),
          ("public comments", 8, None)]
    iys = [2, 1, 0]
    for y, (name, val, tot) in zip(iys, ig):
        if tot:
            ax3.barh(y, tot, color=GRID, height=0.6, edgecolor=BG)
            ax3.barh(y, val, color=RUBEDO, height=0.6, edgecolor=BG)
            ax3.text(tot + 2, y, f"{val}/{tot}", va="center", ha="left",
                     fontsize=10, color=INK, fontweight="bold")
        else:
            ax3.barh(y, val, color=RUBEDO, height=0.6, edgecolor=BG)
            ax3.text(val + 0.8, y, f"{val}", va="center", ha="left",
                     fontsize=10, color=INK, fontweight="bold")
    ax3.set_yticks(iys)
    ax3.set_yticklabels([i[0] for i in ig], fontsize=8.6)
    ax3.set_xlim(0, 36)
    ax3.set_xticks([0, 10, 20, 30])
    ax3.tick_params(axis="x", labelsize=8)
    ax3.grid(axis="x", color=GRID, lw=0.6, alpha=0.7)
    for spine in ("top", "right", "left"):
        ax3.spines[spine].set_visible(False)
    ax3.text(0.0, 1.16, "SURFACE — the IG audit", transform=ax3.transAxes,
             fontsize=12, fontweight="bold", color=INK)
    ax3.text(0.0, 1.05, "logged-out public-surface review · evidence-graded",
             transform=ax3.transAxes, fontsize=7.6, color=MUTED, style="italic")

    footer(fig, "ZAZIOPATH · the record exists because the feeling does not arrive on its own")
    save(fig, "case-study-floor.png")


# ==========================================================================
# 5 · SHADOW → LIGHT CROSSWALK — every dark archetype has a counterpart
# ==========================================================================
def crosswalk():
    pairs = [
        ("Interpretation Sovereign", "Interpretive Steward"),
        ("Credibility Alchemist", "Unimpressive Accountant of Truth"),
        ("Self-Awareness Prestige Trap", "Uncredentialed Confessor"),
        ("Tenderness Monopolist", "Nonpossessive Witness"),
        ("Rescue Architect", "Systems Gardener"),
        ("Boutique Propagandist", "Honest Strategist"),
        ("Shame-to-Superiority Converter", "Envy Translator"),
        ("Curator-King", "Humane Curator"),
        ("Reparative Auteur", "Repair Worker"),
    ]
    fig, ax = plt.subplots(figsize=(12.0, 7.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n = len(pairs)
    top, bottom = 0.895, 0.075
    for i, (shadow, light) in enumerate(pairs):
        y = top - i * (top - bottom) / (n - 1)
        ax.text(0.395, y, shadow, ha="right", va="center", fontsize=10.5,
                color=INK, fontweight="bold")
        ax.text(0.605, y, light, ha="left", va="center", fontsize=10.5,
                color=GOLD_HI, fontweight="bold")
        rad = 0.18 if i % 2 == 0 else -0.18
        arrow = FancyArrowPatch((0.42, y), (0.58, y),
                                connectionstyle=f"arc3,rad={rad}",
                                arrowstyle="-|>", mutation_scale=12,
                                lw=1.2, color=GRID, alpha=0.85)
        ax.add_patch(arrow)

    ax.plot([0.5, 0.5], [bottom - 0.03, top + 0.03], color=GRID, lw=1,
            ls=(0, (4, 4)), alpha=0.6)
    ax.text(0.5, 0.99, "THE CROSSWALK · ch. 22", ha="center", va="top",
            fontsize=15, fontweight="bold", color=INK)
    ax.text(0.5, 0.945, "shadow archetype  →  light counterpart  →  one behavioural pivot",
            ha="center", va="top", fontsize=9, color=MUTED, style="italic")
    ax.text(0.395, 0.015, "SHADOW\n(nigredo)", ha="right", va="bottom",
            fontsize=8.5, color=RUBEDO, fontweight="bold")
    ax.text(0.605, 0.015, "LIGHT\n(albedo)", ha="left", va="bottom",
            fontsize=8.5, color=ALBEDO, fontweight="bold")

    footer(fig, "ZAZIOPATH · read a dark pattern beside its light counterpart, look for behaviour")
    save(fig, "shadow-light-crosswalk.png")


# ==========================================================================
# 6 · PATTERN REGISTER — the 14 recurring patterns around one inference
# ==========================================================================
def pattern_wheel():
    patterns = [
        "hidden mechanisms",          # 1
        "visibility & envy",          # 2
        "low-cost upside + skepticism",  # 3
        "grand ambition ↔ invisibility",  # 4
        "personas metabolize shame",  # 5
        "discounts achievements",     # 6
        "emotion → creative prompt",  # 7
        "others' secrets",            # 8
        "automate, keep taste",       # 9
        "horror & decay ↔ play",      # 10
        "underprices, overoffers",    # 11
        "tests adjacent identities",  # 12
        "obscure-example loop",       # 13
        "suspicious systems, then audit",  # 14
    ]
    fig, ax = plt.subplots(figsize=(11.6, 10.2))
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.55, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    n = len(patterns)
    for i, p in enumerate(patterns):
        ang = math.radians(90 - i * 360 / n)
        x, y = math.cos(ang), math.sin(ang)
        ax.plot([0, x], [0, y], color=GRID, lw=0.8, alpha=0.8, zorder=1)
        ax.scatter([x], [y], s=120, color=RUBEDO if i % 3 == 0 else CITRINITAS,
                   zorder=3, edgecolor=BG, linewidth=1)
        lx, ly = x * 1.16, y * 1.16
        ha = "center"
        if x > 0.35:
            ha = "left"
        elif x < -0.35:
            ha = "right"
        ax.text(lx, ly, f"{i+1:02d} · {p}", ha=ha, va="center",
                fontsize=8.6, color=INK)

    # centre
    center = FancyBboxPatch((-0.62, -0.16), 1.24, 0.32,
                            boxstyle="round,pad=0.03,rounding_size=0.05",
                            fc=PANEL, ec=CITRINITAS, lw=1.2, zorder=4)
    ax.add_patch(center)
    ax.text(0, 0.045, "see the machinery", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color=GOLD_HI, zorder=5)
    ax.text(0, -0.06, "behind appearances", ha="center", va="center",
            fontsize=12.5, fontweight="bold", color=GOLD_HI, zorder=5)

    ax.text(0, 1.47, "THE HIDDEN PATTERN REGISTER · §07", ha="center",
            va="center", fontsize=15, fontweight="bold", color=INK)
    ax.text(0, 1.37, "fourteen recurring patterns, one unifying inference — "
            "the subject wants gatekeepers unable to define reality unchallenged",
            ha="center", va="center", fontsize=8.6, color=MUTED, style="italic")
    footer(fig, "ZAZIOPATH · extracted from the longitudinal memory export")
    save(fig, "pattern-register.png")


if __name__ == "__main__":
    vault_map()
    cosmology()
    typology()
    case_study()
    crosswalk()
    pattern_wheel()
    print("done.")
