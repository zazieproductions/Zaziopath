#!/usr/bin/env python3
"""
ZAZIOPATH figure engine.
Reads Zazie_Productions_Discography.csv + the repo root census and renders the
Pattern Atlas figures into docs/figures/.

Colour system: Okabe–Ito colourblind-safe palette, one colour per vault stratum.
Colour is never the only encoding — every series also carries a glyph, a hatch,
or a direct label. All figures ship with white backgrounds for legibility in
both light and dark GitHub themes.

Run:  python3 tools/generate_figures.py
"""

import csv
import os
import re
import statistics
import collections
import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT, exist_ok=True)

# ───────────────────────── Okabe–Ito stratum palette ─────────────────────────
C = {
    "INDEX":       "#231F20",  # ⬛ index / meta
    "IDENTITY":    "#0072B2",  # 🟦 identity & typology
    "SHADOW":      "#CC79A7",  # 🟪 shadow work
    "EVIDENCE":    "#E69F00",  # 🟧 signal / evidence audits
    "RECURSION":   "#009E73",  # 🟩 AI recursion lab
    "STEWARDSHIP": "#56B4E9",  # 🔷 stewardship protocols
    "SPECIMENS":   "#D55E00",  # 🟥 specimen cabinet
    "MYTHOGRAPHY": "#F0E442",  # 🟨 mythography
    "GRID":        "#B9B4AA",
    "INK":         "#231F20",
    "PAPER":       "#FFFFFF",
}

plt.rcParams.update({
    "figure.facecolor": C["PAPER"],
    "axes.facecolor":   C["PAPER"],
    "savefig.facecolor": C["PAPER"],
    "font.family": "DejaVu Sans",
    "axes.edgecolor": C["INK"],
    "axes.labelcolor": C["INK"],
    "text.color": C["INK"],
    "xtick.color": C["INK"],
    "ytick.color": C["INK"],
    "axes.grid": True,
    "grid.color": C["GRID"],
    "grid.linewidth": 0.5,
    "grid.alpha": 0.55,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
})


def stamp(fig, tag):
    fig.text(0.995, 0.006, f"ZAZIOPATH · Pattern Atlas · {tag} · palette: Okabe–Ito",
             ha="right", va="bottom", fontsize=6.5, color="#6b6560")


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


# ───────────────────────────── load the catalog ──────────────────────────────
with open(os.path.join(ROOT, "Zazie_Productions_Discography.csv"),
          encoding="utf-8-sig") as fh:
    rows = list(csv.DictReader(fh))

for r in rows:
    m, s = r["Duration"].split(":")
    r["secs"] = int(m) * 60 + int(s)
    r["date"] = datetime.date.fromisoformat(r["Release Date"])
    r["year"] = r["date"].year

releases = {}
for r in rows:
    releases.setdefault((r["Release Date"], r["Release Title"], r["Release Type"]),
                        []).append(r)

TYPE_COLOR = {"Album": C["IDENTITY"], "EP": C["EVIDENCE"], "Single": C["RECURSION"]}
TYPE_HATCH = {"Album": "",            "EP": "//",           "Single": "xx"}
TYPE_GLYPH = {"Album": "■ Album", "EP": "▨ EP", "Single": "▩ Single"}

YEARS = list(range(2019, 2027))

# ══════════════════════ FIG 1 · the catalog pulse ════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5.2))
bottom = np.zeros(len(YEARS))
for t in ["Album", "EP", "Single"]:
    vals = [sum(1 for r in rows if r["year"] == y and r["Release Type"] == t)
            for y in YEARS]
    ax.bar(YEARS, vals, bottom=bottom, color=TYPE_COLOR[t], hatch=TYPE_HATCH[t],
           edgecolor="white", linewidth=0.8, label=TYPE_GLYPH[t], width=0.72)
    bottom += np.array(vals)

for x, tot in zip(YEARS, bottom):
    if tot:
        ax.text(x, tot + 1.2, str(int(tot)), ha="center", fontweight="bold", fontsize=11)

ann = dict(fontsize=8.5, ha="center",
           bbox=dict(boxstyle="round,pad=0.35", fc="#FFF8E7", ec=C["EVIDENCE"], lw=1.2))
ax.annotate("EXHIBIT: deluxe-edition\narchive inflation\n(32 + 28 reissue tracks)",
            xy=(2024, 60), xytext=(2022.0, 55),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)
ax.annotate("EXHIBIT: the quiet year —\n4 tracks, all singles,\nhalf on another artist's release",
            xy=(2025, 4), xytext=(2025.2, 30),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)
ax.annotate("audits begin\n(Jul–Aug 2026)", xy=(2026, 34), xytext=(2026.2, 48),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)

ax.set_title("FIG 1 · THE CATALOG PULSE — tracks released per year, 2019–2026",
             fontweight="bold", loc="left", fontsize=12)
ax.set_ylabel("tracks released")
ax.set_xticks(YEARS)
ax.set_ylim(0, 72)
ax.legend(frameon=False, loc="upper left")
stamp(fig, "FIG 1")
save(fig, "fig1_catalog_pulse.png")

# ══════════════════════ FIG 2 · the miniaturization event ════════════════════
fig, ax = plt.subplots(figsize=(10, 5.4))
x = [r["date"] for r in rows]
y = [r["secs"] for r in rows]
ax.axhspan(0, 120, color=C["SHADOW"], alpha=0.13, zorder=0)
ax.text(datetime.date(2019, 7, 1), 8, "MINIATURE ZONE (< 2:00)",
        fontsize=8, color=C["SHADOW"], fontweight="bold")
ax.scatter(x, y, s=26, c=C["IDENTITY"], alpha=0.55, edgecolors="none", zorder=3,
           label="○ one track")

med_x, med_y = [], []
for yv in YEARS:
    vals = [r["secs"] for r in rows if r["year"] == yv]
    if vals:
        med_x.append(datetime.date(yv, 7, 1))
        med_y.append(statistics.median(vals))
ax.plot(med_x, med_y, color=C["SPECIMENS"], lw=2.5, marker="D", ms=6,
        zorder=4, label="◆ yearly median")
for xx, yy in zip(med_x, med_y):
    ax.text(xx, yy + 14, f"{int(yy // 60)}:{int(yy % 60):02d}", ha="center",
            fontsize=8, fontweight="bold", color=C["SPECIMENS"],
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])

ann = dict(fontsize=8.5, bbox=dict(boxstyle="round,pad=0.35", fc="#FFF8E7",
                                   ec=C["EVIDENCE"], lw=1.2))
ax.annotate("Spectral Ode to Synesthesia — 8:55\nlongest statement in the catalog",
            xy=(datetime.date(2025, 3, 5), 535), xytext=(datetime.date(2021, 9, 1), 500),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)
ax.annotate("2024: median collapses to 1:22 —\n39 of 60 tracks under two minutes",
            xy=(datetime.date(2024, 7, 1), 82), xytext=(datetime.date(2022, 3, 1), 300),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)
ax.annotate("0:07 — Hues Adorned in White (Interlude)",
            xy=(datetime.date(2024, 12, 23), 7), xytext=(datetime.date(2019, 8, 1), 48),
            arrowprops=dict(arrowstyle="->", color=C["INK"]), **ann)

ax.set_title("FIG 2 · THE MINIATURIZATION EVENT — track duration vs. release date",
             fontweight="bold", loc="left", fontsize=12)
ax.set_ylabel("track duration (seconds)")
ax.set_ylim(0, 580)
ax.legend(frameon=False, loc="upper right")
stamp(fig, "FIG 2")
save(fig, "fig2_miniaturization.png")

# ══════════════════════ FIG 3 · ISRC forensics ═══════════════════════════════
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.2),
                              gridspec_kw={"width_ratios": [1.35, 1]})
pairs = collections.Counter()
for r in rows:
    i = r["ISRC"]
    if i and i != "N/A":
        pairs[(r["year"], 2000 + int(i[5:7]))] += 1

for (ry, iy), n in pairs.items():
    backfill = iy > ry
    reuse = iy < ry
    col = C["SPECIMENS"] if backfill else (C["STEWARDSHIP"] if reuse else C["RECURSION"])
    mk = "s" if backfill else ("^" if reuse else "o")
    ax.scatter(ry, iy, s=48 + n * 26, c=col, marker=mk, edgecolors=C["INK"],
               linewidths=0.7, zorder=3)
    ax.text(ry, iy, str(n), ha="center", va="center", fontsize=7.5,
            fontweight="bold", color="white" if n > 4 else C["INK"], zorder=4,
            path_effects=[pe.withStroke(linewidth=2, foreground=col)])

ax.plot([2018.5, 2026.5], [2018.5, 2026.5], ls=":", color=C["GRID"], zorder=1)
ax.text(2019.1, 2019.45, "same-year registration ⌀", rotation=38, fontsize=7.5,
        color="#6b6560")
ax.annotate("THE 2022 REGISTRATION EVENT\n2019 + 2020 catalog retro-registered\nin a single administrative sweep",
            xy=(2019.5, 2022), xytext=(2019.0, 2025.4), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=C["INK"]),
            bbox=dict(boxstyle="round,pad=0.35", fc="#FFF8E7", ec=C["EVIDENCE"], lw=1.2))
ax.annotate("deluxe editions carry\ntheir old ISRCs forward\n(relics inside reissues)",
            xy=(2026, 2022), xytext=(2021.3, 2019.35), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=C["INK"]),
            bbox=dict(boxstyle="round,pad=0.35", fc="#FFF8E7", ec=C["EVIDENCE"], lw=1.2))

ax.set_xlabel("release year")
ax.set_ylabel("year embedded in ISRC (registration)")
ax.set_title("FIG 3a · WHEN THE PAPERWORK HAPPENED\nISRC registration year vs. release year",
             fontweight="bold", loc="left", fontsize=11)
ax.set_xticks(YEARS)
ax.set_yticks(range(2022, 2027))
from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([], [], marker="s", ls="", mfc=C["SPECIMENS"], mec=C["INK"], label="■ backfilled later"),
    Line2D([], [], marker="o", ls="", mfc=C["RECURSION"], mec=C["INK"], label="● same year"),
    Line2D([], [], marker="^", ls="", mfc=C["STEWARDSHIP"], mec=C["INK"], label="▲ old code reused"),
], frameon=True, framealpha=0.95, edgecolor="#B9B4AA", loc="upper left", bbox_to_anchor=(0.66, 0.34), fontsize=8)

# 3b — the provenance hole
labels, missing, totals = [], [], []
for (d, t, ty), trs in sorted(releases.items()):
    na = sum(1 for r in trs if r["ISRC"] in ("", "N/A"))
    if na:
        labels.append(f"{t[:34]} · {d[:4]}")
        missing.append(na)
        totals.append(len(trs))
ypos = np.arange(len(labels))
ax2.barh(ypos, totals, color="#E8E4DC", edgecolor=C["INK"], lw=0.5, label="tracks on release")
ax2.barh(ypos, missing, color=C["SHADOW"], hatch="//", edgecolor="white",
         label="tracks with NO ISRC")
for i, (m, t) in enumerate(zip(missing, totals)):
    ax2.text(t + 0.3, i, f"{m}/{t}", va="center", fontsize=8, fontweight="bold")
ax2.set_yticks(ypos, labels, fontsize=8)
ax2.invert_yaxis()
ax2.set_title("FIG 3b · THE PROVENANCE HOLE\n21 unregistered tracks cluster in 2021–2022",
              fontweight="bold", loc="left", fontsize=11)
ax2.set_xlabel("tracks")
ax2.legend(frameon=True, framealpha=0.95, edgecolor="#B9B4AA", fontsize=8, loc="upper right")
stamp(fig, "FIG 3")
fig.tight_layout()
save(fig, "fig3_isrc_forensics.png")

# ══════════════════════ FIG 4 · deluxe inflation ═════════════════════════════
fig, ax = plt.subplots(figsize=(9, 3.6))
items = [
    ("Stutter to stammer", 2019, 5, 2024, 32),
    ("Sellotape", 2020, 8, 2026, 22),
    ("Greetings From Tinsel Time", 2023, 13, 2024, 28),
]
for i, (name, y0, n0, y1, n1) in enumerate(items):
    ax.plot([n0, n1], [i, i], color=C["GRID"], lw=3, zorder=1)
    ax.scatter([n0], [i], s=180, color=C["IDENTITY"], zorder=3, marker="o",
               edgecolors=C["INK"])
    ax.scatter([n1], [i], s=260, color=C["SPECIMENS"], zorder=3, marker="D",
               edgecolors=C["INK"])
    ax.text(n0, i + 0.22, f"● original ({y0}): {n0}", fontsize=8.5, ha="center")
    ax.text(n1, i + 0.22, f"◆ super deluxe ({y1}): {n1}", fontsize=8.5, ha="center")
    ax.text((n0 + n1) / 2, i - 0.3, f"×{n1 / n0:.1f} inflation", ha="center",
            fontsize=9, fontweight="bold", color=C["SPECIMENS"])
ax.set_yticks(range(len(items)), [n for n, *_ in items], fontsize=10)
ax.set_ylim(-0.75, 2.6)
ax.set_xlim(0, 38)
ax.invert_yaxis()
ax.set_xlabel("tracks on edition")
ax.set_title("FIG 4 · THE ARCHIVE THAT RE-OPENS ITS OWN PAST — reissue track inflation",
              fontweight="bold", loc="left", fontsize=12)
stamp(fig, "FIG 4")
save(fig, "fig4_deluxe_inflation.png")

# ══════════════════════ FIG 5 · seasonality ══════════════════════════════════
fig = plt.figure(figsize=(6.4, 6.4))
ax = fig.add_subplot(projection="polar")
mon = collections.Counter(int(d[5:7]) for (d, _, _) in releases)
theta = np.array([(m - 1) / 12 * 2 * np.pi for m in range(1, 13)])
vals = np.array([mon.get(m, 0) for m in range(1, 13)])
winter = {12, 1, 2, 3}
cols = [C["STEWARDSHIP"] if m in winter else C["EVIDENCE"] for m in range(1, 13)]
hat = ["//" if m in winter else "" for m in range(1, 13)]
bars = ax.bar(theta, vals, width=2 * np.pi / 12 * 0.86, bottom=0.15,
              color=cols, edgecolor="white", linewidth=1)
for b, h in zip(bars, hat):
    b.set_hatch(h)
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_xticks(theta)
ax.set_xticklabels(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG",
                    "SEP", "OCT", "NOV", "DEC"], fontsize=9)
ax.set_yticks([1, 2, 3, 4])
ax.set_yticklabels(["1", "2", "3", "4"], fontsize=7)
ax.set_title("FIG 5 · RELEASE SEASONALITY — 21 release events by month\n"
             "▨ blue = winter-adjacent (Dec–Mar) · ■ orange = rest of year",
             fontsize=11, fontweight="bold", pad=22)
ax.text(0, -0.16, "Spring (Mar–May) is the workshop: 10 of 21 releases.\n"
        "December is the ritual: the holiday album, its deluxe resurrection, an opaline lament.",
        transform=ax.transAxes, ha="left", fontsize=8, color="#5a544e")
stamp(fig, "FIG 5")
save(fig, "fig5_seasonality.png")

# ══════════════════════ FIG 6 · vault strata census ══════════════════════════
STRATA = {
    "INDEX": ["README.md", "🕸 Major Knowledge Graph.md", "⚡ Unexpected Connections.md",
              "🗄 Stub Registry.md", "🧾 Inventory of Distinct Things.md",
              "create a link.md", "text.txt", "zazie_mindmap.html"],
    "IDENTITY": ["Identity _ Typological Vault.pdf", "JSON file re-export ChatGPT Memory .md",
                 "Archetype Test.pdf", "Avoidant Personality Spectrum Test.pdf",
                 "Borderline Spectrum Test 5.pdf", "Brainrot Spectrum Test.pdf",
                 "Moral Outrage Test (MOT).pdf",
                 "Philosopher Personality Test Presocratics Edition.pdf",
                 "Discoveries - Genius _ Hybrid _TE.pdf", "6Foundations 2.pdf"],
    "SHADOW": ["Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
               "Shadow Journal Observations .pdf", "Ideological Inversion Audit.pdf",
               "The Black Book II.pdf"],
    "EVIDENCE": ["Zazie_Productions_Complete_Discography.xlsx",
                 "Zazie_Productions_Discography.csv", "Zazie_Media_Master (1).pdf",
                 "Zazie_Productions_Instagram_Forensic_Audit.pdf",
                 "Lost_Zazie_Productions_Archive.pdf"],
    "RECURSION": ["GPT Model 7.7-t Surveillance Subroutine.pdf",
                  "THE OMNIVISIONARY GROK OUTPUT .pdf", "Counterference Engine.pdf",
                  "greyhat", "meta-experiment", "verdict_from_A.i",
                  "OmniCipher_Signal_Codex_v1.0.pdf"],
    "STEWARDSHIP": ["Anti-Perfectionism Brain Hacks.md",
                    "Entry Instructions for the Undetonated Artist.md"],
    "SPECIMENS": ["Social Engineering Email Templates .md",
                  "Blueprints for Quiet, Horrifying Wealth.md",
                  "Cognitive Infiltration Blueprints.md",
                  "Personal Branding as Class War Psy-Ops.md"],
    "MYTHOGRAPHY": ["MAXIMAL SYMBOLIC SPECIFICITY ENGINE (MSS-E).md",
                    "Dr. Caligo Vespertine in the Negative Observatory.md",
                    "GIBBERETIC SEED SPIRAL — glocht.md",
                    "Twelve-Lung Grammar of the Forgotten Species.md",
                    "Hypostasis in Amber (Palindromic-image cascade).md",
                    "RECURSIVE IDENTITY CASTLES.md",
                    "Sovereign Interface Protocol (The Matrix).md",
                    "Mythographic Childhood.md", "Anémone Crottin-Foufflée Identity.md",
                    "UNEXPLAINED AERIAL PHENOMENA REPORT.md",
                    "THE SPALLED VESTIBULE, OR_ WHERE THE BYLAWS GO TO ROT by Zazie Productions.pdf",
                    "The_God_in_the_Syntax_Machine_Zazie_Productions_Expanded.docx",
                    "The_Sound_That_Swallowed_April.docx",
                    "Whispers_from_Unit_G19_FinalSubmission.docx",
                    "ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf",
                    "Zazie Productions - MEGA-UNIVERSE.md",
                    "ALBUM STRUCTURE - 4×3 FRACTAL MODULES.md",
                    "TEXTUAL_EXHUMATIONS_UNICODE.pdf", "INDEX ORGANICA.zip",
                    "conspiracy-tier-list-full.png"],
}
CHIP = {"INDEX": "⬛", "IDENTITY": "🟦", "SHADOW": "🟪", "EVIDENCE": "🟧",
        "RECURSION": "🟩", "STEWARDSHIP": "🔷", "SPECIMENS": "🟥", "MYTHOGRAPHY": "🟨"}
GLYPH = {"INDEX": "◈", "IDENTITY": "◉", "SHADOW": "◐", "EVIDENCE": "▤",
         "RECURSION": "∞", "STEWARDSHIP": "△", "SPECIMENS": "⚠", "MYTHOGRAPHY": "☾"}

import unicodedata
_norm = {unicodedata.normalize("NFC", f): f for f in os.listdir(ROOT)}

sizes, counts = {}, {}
for s, files in STRATA.items():
    tot = 0
    n = 0
    for f in files:
        f = _norm.get(unicodedata.normalize("NFC", f), f)
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            tot += os.path.getsize(p)
            n += 1
        else:
            print("  [census warning] missing:", f)
    sizes[s] = tot / 1024.0
    counts[s] = n

order = sorted(sizes, key=sizes.get, reverse=True)
fig, ax = plt.subplots(figsize=(10, 5))
ypos = np.arange(len(order))
vals = [sizes[s] for s in order]
ax.barh(ypos, vals, color=[C[s] for s in order], edgecolor=C["INK"], lw=0.6)
for i, s in enumerate(order):
    ax.text(vals[i] * 1.06, i, f"{GLYPH[s]} {sizes[s]:,.0f} KB · {counts[s]} files",
            va="center", fontsize=9, fontweight="bold")
ax.set_yticks(ypos, [f"{GLYPH[s]}  {s}" for s in order], fontsize=10)
ax.invert_yaxis()
ax.set_xscale("log")
ax.set_xlim(3, 40000)
ax.set_xlabel("stratum mass at repo root (KB, log scale)")
ax.set_title("FIG 6 · THE VAULT STRATA CENSUS — what the repository is made of",
             fontweight="bold", loc="left", fontsize=12)
ax.text(0.995, 0.02, "identity instruments outweigh everything —\n"
        "the vault spends 3.7 MB measuring one person\nand 5 KB telling them what to do about it",
        transform=ax.transAxes, ha="right", fontsize=8.5, style="italic",
        color="#5a544e")
stamp(fig, "FIG 6")
save(fig, "fig6_strata_census.png")

# ══════════════════════ FIG 7 · title lexicon autopsy ════════════════════════
THEMES = {
    "❄ winter & frost": ["snow", "frost", "ice", "iceberg", "winter", "sleigh", "tinsel",
                          "xmas", "christmas", "yuletide", "reindeer", "holly", "jingle",
                          "avalanche", "blizzard", "hyperthermia", "frozen", "brumal",
                          "hail", "cold"],
    "⚗ science & mathematics": ["ulam", "spiral", "quark", "dna", "phenyl", "carbon",
                                 "vacuum", "expansion", "sphere", "gravity", "metric",
                                 "fragment", "signal", "static", "crt", "synesthesia",
                                 "hyperlink", "erhu", "meridian", "pyrogenesis",
                                 "dichloroarsine", "klerkdorp", "simulation", "immolation"],
    "† death, decay & lament": ["dead", "death", "requiem", "mausoleum", "catacombs",
                                  "lament", "elegy", "grave", "mummified", "impaler",
                                  "slaughter", "rot", "bone", "skeleton", "poltergeist",
                                  "spectral", "ghost", "haunt", "dismal", "hollow",
                                  "discarded", "deleted", "unfinished", "lost", "epilogue",
                                  "farewell", "goodnight"],
    "✚ ritual & the sacred": ["hymn", "ritual", "baptism", "communion", "angels",
                                "steeple", "cathedral", "sacred", "gloria", "ode",
                                "nocturne", "waltz", "rhapsody", "serfdom", "monachopsis"],
    "▤ bureaucracy & media": ["archive", "wikipedia", "list", "tracking", "ups",
                                "broadcast", "leak", "interference", "subliminal",
                                "impressions", "movie", "scene", "tape", "remastered",
                                "editorial", "capacity", "concessions", "outro",
                                "interlude", "demo", "bonus"],
}
theme_counts = collections.Counter()
title_words = []
for r in rows:
    ws = set(re.findall(r"[a-z]+", r["Track Title"].lower()))
    title_words.append(ws)
for tset in title_words:
    for theme, kws in THEMES.items():
        if tset & set(kws):
            theme_counts[theme] += 1

fig, ax = plt.subplots(figsize=(9.5, 4.2))
tlabels = list(THEMES.keys())
tvals = [theme_counts[t] for t in tlabels]
tcols = [C["STEWARDSHIP"], C["RECURSION"], C["SHADOW"], C["EVIDENCE"], C["INDEX"]]
srt = sorted(range(len(tlabels)), key=lambda i: tvals[i], reverse=True)
ypos = np.arange(len(tlabels))
ax.barh(ypos, [tvals[i] for i in srt], color=[tcols[i] for i in srt],
        edgecolor=C["INK"], lw=0.6)
for j, i in enumerate(srt):
    ax.text(tvals[i] + 1, j, f"{tvals[i]} tracks ({tvals[i] / len(rows) * 100:.0f}%)",
            va="center", fontsize=9, fontweight="bold")
ax.set_yticks(ypos, [tlabels[i] for i in srt], fontsize=10)
ax.invert_yaxis()
ax.set_xlim(0, 75)
ax.set_xlabel("tracks whose titles touch the theme (n=182; themes overlap)")
ax.set_title("FIG 7 · TITLE LEXICON AUTOPSY — what 182 track titles keep returning to",
             fontweight="bold", loc="left", fontsize=12)
ax.text(0.995, 0.03,
        "the catalog and the vault share one vocabulary:\ndecay, ritual, archives, and cold precision",
        transform=ax.transAxes, ha="right", fontsize=8.5, style="italic", color="#5a544e")
stamp(fig, "FIG 7")
save(fig, "fig7_title_lexicon.png")

# ══════════════════════ FIG 0 · the colour legend card ═══════════════════════
fig, ax = plt.subplots(figsize=(10, 3.9))
ax.axis("off")
strata_desc = [
    ("INDEX",       "◈",  "index & meta", "maps, registries, this README"),
    ("IDENTITY",    "◉", "identity",      "typology, tests, memory export"),
    ("SHADOW",      "◐", "shadow",        "compendium, journals, inversions"),
    ("EVIDENCE",    "▤", "signal",        "discography, media, IG audits"),
    ("RECURSION",   "∞",  "recursion lab", "AI tribunals, loop artifacts"),
    ("STEWARDSHIP", "△", "stewardship",   "protocols, behavioural pivots"),
    ("SPECIMENS",   "⚠",  "specimens",     "offensive-grade, read-only"),
    ("MYTHOGRAPHY", "☾", "mythography",   "worldbuilding, constructed lore"),
]
for i, (k, g, name, desc) in enumerate(strata_desc):
    x = (i % 4) * 0.25
    yrow = 0.46 if i < 4 else 0.08
    ax.add_patch(plt.Rectangle((x + 0.005, yrow + 0.08), 0.042, 0.15,
                               facecolor=C[k], edgecolor=C["INK"], lw=0.8,
                               transform=ax.transAxes, clip_on=False))
    ax.text(x + 0.058, yrow + 0.19, f"{g}  {name.upper()}", transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="center")
    ax.text(x + 0.058, yrow + 0.10, C[k], transform=ax.transAxes, fontsize=8,
            family="monospace", va="center", color="#5a544e")
    ax.text(x + 0.005, yrow - 0.015, desc, transform=ax.transAxes, fontsize=7.8,
            va="center", color="#5a544e")
ax.text(0, 1.04, "FIG 0 · THE VAULT COLOUR SYSTEM — Okabe–Ito colourblind-safe palette",
        transform=ax.transAxes, fontsize=12.5, fontweight="bold", va="top")
ax.text(0, 0.90, "one colour per stratum, everywhere: README chips, Mermaid graphs, atlas figures.\n"
        "Colour never encodes alone — every use is paired with a glyph and a text label.",
        transform=ax.transAxes, fontsize=8.5, va="top", color="#5a544e")
stamp(fig, "FIG 0")
save(fig, "fig0_colour_legend.png")

print("\nAll figures rendered to", OUT)
