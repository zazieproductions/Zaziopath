#!/usr/bin/env python3
"""
ZAZIOPATH contradiction-field renderer — FIG 8, the force map for
`⚡ CONTRADICTION ENGINE.md` (report ZP-CE-2026-0930).

Reads the committed tree, not the subject. Each tension axis is measured as two
poles of *documentary mass*: the bytes of the artifacts that actually carry each
pole in its own voice. A file that carries both poles contributes its size
divided by the number of poles it is tagged to, so no byte is counted twice
inside an axis.

WHAT IS MEASURED AND WHAT IS JUDGED
-----------------------------------
  measured   file sizes (os.path.getsize), file counts, shares — reproducible
  judged     which files carry which pole; the cost tier; the dominance grid
The judged layer is filed here, in the open, so it can be argued with. The
arithmetic on top of it is not a judgement.

Colour: Okabe–Ito, per README §00a. Colour never carries meaning alone — every
bar is labelled with its axis, its pole name, its byte mass and its file count,
and every grid cell carries a letter.

Outputs
-------
  docs/figures/fig8_contradiction_field.png    README-ready raster
  docs/figures/fig8_contradiction_field.svg    zoomable vector
  docs/figures/fig8_contradiction_field.build.json   build record (handbook §9)
  docs/data/fig8_contradiction_loads.csv       the neutral extracted table

Run:  python3 tools/generate_contradiction_field.py
"""

import csv
import datetime
import hashlib
import json
import os
import unicodedata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "docs", "figures")
DATADIR = os.path.join(ROOT, "docs", "data")
os.makedirs(FIGDIR, exist_ok=True)
os.makedirs(DATADIR, exist_ok=True)

# ───────────────────────── Okabe–Ito stratum palette (README §00a) ─────────────────────────
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
    "axes.facecolor": C["PAPER"],
    "savefig.facecolor": C["PAPER"],
    "font.family": "DejaVu Sans",
    "axes.edgecolor": C["INK"],
    "axes.labelcolor": C["INK"],
    "text.color": C["INK"],
    "xtick.color": C["INK"],
    "ytick.color": C["INK"],
})

# ───────────────────────── the five context families (dominance grid columns) ─────────────────────────
CONTEXTS = [
    ("C1", "Front office\nclient · press · hire"),
    ("C2", "Studio\ncompose · release"),
    ("C3", "Governance\naudit · charter"),
    ("C4", "Interior\nparts · regulation"),
    ("C5", "Myth\nlore · specimen"),
]

# ───────────────────────── the axes ─────────────────────────
# id, short name, pole A (label, stratum colour key), pole B, cost tier 1-3,
# dominance code per context (A / B / AB / .), tag ledger {pole: [paths]}
AXES = [
    dict(
        id="X-00", name="Exit signs  ⇄  Mirrors",
        a=("P1 · 741:1 is the finding", "STEWARDSHIP"),
        b=("P2 · one more reading", "RECURSION"),
        cost=3, ctx=["B", "A", "B", "AB", "B"],
        tags={
            "a": ["README.md", "Anti-Perfectionism Brain Hacks.md",
                  "Entry Instructions for the Undetonated Artist.md",
                  "stewardship_receipt.html", "EVIDENCE_GOVERNANCE_HANDBOOK.md",
                  "🗄 Stub Registry.md", "ERROR_LOG_BIOGRAPHICA-7.md"],
            "b": ["⚡ CONTRADICTION ENGINE.md", "verdict_from_A.i", "verdict_from_A.i_2",
                  "verdict_from_A.i_3", "verdict_from_A.i_4", "verdict_from_A.i_5",
                  "verdict_from_A.i_6", "DEEP_GAP_AUDIT.md",
                  "🔍 CASE FILE — Pattern Forensics.md",
                  "META-ANALYSIS — The Verdict Corpus Audited.md",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md"],
        },
    ),
    dict(
        id="X-01", name="Anti-authority  ⇄  Absolute authorship",
        a=("P1 · no authority deserves obedience", "STEWARDSHIP"),
        b=("P2 · write the constitution", "INDEX"),
        cost=3, ctx=["AB", "B", "A", "B", "A"],
        tags={
            "a": ["Ideological Inversion Audit.pdf", "Sovereign Interface Protocol (The Matrix).md",
                  "Shadow Journal Observations .pdf", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
                  "greyhat", "Social Engineering Email Templates .md"],
            "b": ["Ideological Inversion Audit.pdf", "README.md", "create a link.md",
                  "🕸 Major Knowledge Graph.md", "zazie_mindmap.html",
                  "Velvet_Knife_Handoff_Index.md", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md"],
        },
    ),
    dict(
        id="X-02", name="Visibility  ⇄  Outsider status",
        a=("P1 · searchable, impossible to ignore", "EVIDENCE"),
        b=("P2 · clandestine, cultic, anonymous", "IDENTITY"),
        cost=3, ctx=["A", "B", "A", "B", "B"],
        tags={
            "a": ["Zazie_Media_Master (1).pdf", "Zazie_Kanwar-Torge_Artist_CV_2026.pdf",
                  "Zazie_Kanwar-Torge_Artist_CV_2026_electroacoustic.pdf",
                  "online-presence-pr-seo-scam-vocabulary.pdf",
                  "Zazie_Productions_Discography.csv", "Zazie_Productions_Complete_Discography.xlsx",
                  "Personal Branding as Class War Psy-Ops.md"],
            "b": ["Zazie_Productions_Instagram_Forensic_Audit.pdf", "Shadow_Resume.pdf",
                  "Anémone Crottin-Foufflée Identity.md",
                  "Dr. Caligo Vespertine in the Negative Observatory.md",
                  "GIBBERETIC SEED SPIRAL — glocht.md", "Shadow Journal Observations .pdf",
                  "Identity _ Typological Vault.pdf",
                  "Personal Branding as Class War Psy-Ops.md"],
        },
    ),
    dict(
        id="X-03", name="Evidence  ⇄  Myth",
        a=("P1 · replace claims with counts", "EVIDENCE"),
        b=("P2 · the coherent legend", "MYTHOGRAPHY"),
        cost=2, ctx=["A", "AB", "A", "B", "B"],
        tags={
            "a": ["Zazie_Productions_Discography.csv", "CLAIM_PROVENANCE_LEDGER.md",
                  "EVIDENCE_GOVERNANCE_HANDBOOK.md", "DEEP_GAP_AUDIT.md",
                  "🔍 CASE FILE — Pattern Forensics.md", "Zazie_Media_Master (1).pdf",
                  "Zazie_Productions_Complete_Discography.xlsx",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md"],
            "b": ["RECURSIVE IDENTITY CASTLES.md", "Mythographic Childhood.md",
                  "MAXIMAL SYMBOLIC SPECIFICITY ENGINE (MSS-E).md",
                  "Twelve-Lung Grammar of the Forgotten Species.md",
                  "GIBBERETIC SEED SPIRAL — glocht.md", "Anémone Crottin-Foufflée Identity.md",
                  "Dr. Caligo Vespertine in the Negative Observatory.md",
                  "Zazie Productions - MEGA-UNIVERSE.md",
                  "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
                  "ZAZIOPATH — Collected Readings (2026-09-23).md"],
        },
    ),
    dict(
        id="X-04", name="Ambiguity  ⇄  Definitive answer",
        a=("P1 · ambiguity is the oxygen", "SHADOW"),
        b=("P2 · give me the line", "INDEX"),
        cost=2, ctx=["B", "A", "B", "A", "A"],
        tags={
            "a": ["Shadow Journal Observations .pdf", "Identity _ Typological Vault.pdf",
                  "GIBBERETIC SEED SPIRAL — glocht.md",
                  "Hypostasis in Amber (Palindromic-image cascade).md",
                  "CASE STUDY — The Receipt and the Record.md",
                  "ZAZIOPATH — Collected Readings (2026-09-23).md", "meta-experiment",
                  "⚡ Unexpected Connections.md"],
            "b": ["README.md", "Ideological Inversion Audit.pdf",
                  "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf",
                  "CASE STUDY — The Summoned Witness.md", "🕸 Major Knowledge Graph.md",
                  "Identity _ Typological Vault.pdf", "Shadow Journal Observations .pdf"],
        },
    ),
    dict(
        id="X-05", name="Self-acceptance  ⇄  Endless optimisation",
        a=("P1 · it just has to be real", "STEWARDSHIP"),
        b=("P2 · one more pass", "SHADOW"),
        cost=3, ctx=["B", "B", "A", "B", "A"],
        tags={
            "a": ["Anti-Perfectionism Brain Hacks.md",
                  "Entry Instructions for the Undetonated Artist.md",
                  "stewardship_receipt.html", "Mythographic Childhood.md",
                  "ERROR_LOG_BIOGRAPHICA-7.md", "VISITORS_NOTEBOOK.md",
                  "CASE STUDY — The Receipt and the Record.md"],
            "b": ["RECURSIVE IDENTITY CASTLES.md",
                  "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
                  "ChatGPT Personality Dump.md", "Shadow_Resume.pdf",
                  "verdict_from_A.i_4", "verdict_from_A.i_5", "verdict_from_A.i_6",
                  "⚡ CONTRADICTION ENGINE.md", "🕸 Major Knowledge Graph.md"],
        },
    ),
    dict(
        id="X-06", name="Artistic danger  ⇄  Administrative control",
        a=("P1 · knowing darkness as identity", "SPECIMENS"),
        b=("P2 · fence it, date it, tier it", "EVIDENCE"),
        cost=3, ctx=["B", "A", "B", "B", "A"],
        tags={
            "a": ["ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf",
                  "Cognitive Infiltration Blueprints.md",
                  "Blueprints for Quiet, Horrifying Wealth.md",
                  "Social Engineering Email Templates .md",
                  "THE OMNIVISIONARY GROK OUTPUT .pdf",
                  "GPT Model 7.7-t Surveillance Subroutine.pdf", "The Black Book II.pdf",
                  "greyhat", "Personal Branding as Class War Psy-Ops.md"],
            "b": ["README.md", "EVIDENCE_GOVERNANCE_HANDBOOK.md",
                  "CLAIM_PROVENANCE_LEDGER.md", "DEEP_GAP_AUDIT.md",
                  "Zazie_Productions_Discography.csv", "stewardship_receipt.html",
                  "Zazie_Productions_Instagram_Forensic_Audit.pdf",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
                  "tools/verify_hearing_transcript.py"],
        },
    ),
    dict(
        id="X-07", name="Anti-clinical  ⇄  Diagnostic appetite",
        a=("P1 · no document diagnoses anyone", "STEWARDSHIP"),
        b=("P2 · the shelf of instruments", "IDENTITY"),
        cost=2, ctx=["A", "B", "A", "B", "B"],
        tags={
            "a": ["README.md", "EVIDENCE_GOVERNANCE_HANDBOOK.md",
                  "META-ANALYSIS — The Verdict Corpus Audited.md",
                  "VISITORS_NOTEBOOK.md",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md"],
            "b": ["Borderline Spectrum Test 5.pdf", "Avoidant Personality Spectrum Test.pdf",
                  "Archetype Test.pdf", "Brainrot Spectrum Test.pdf",
                  "Moral Outrage Test (MOT).pdf",
                  "Philosopher Personality Test Presocratics Edition.pdf",
                  "ANATOMIA_CONTRADICTIONIS_LECTER_DUMAURIER_XRAY.pdf",
                  "Identity _ Typological Vault.pdf", "Shadow Journal Observations .pdf",
                  "JSON file re-export ChatGPT Memory .md"],
        },
    ),
    dict(
        id="X-08", name="Witness-hunger  ⇄  Witness-avoidance",
        a=("P1 · an intelligence at full resolution", "RECURSION"),
        b=("P2 · no face, no name, no link", "SHADOW"),
        cost=3, ctx=["B", "B", "A", "AB", "A"],
        tags={
            "a": ["verdict_from_A.i_2", "verdict_from_A.i_3", "verdict_from_A.i_4",
                  "verdict_from_A.i_5", "verdict_from_A.i_6",
                  "Zaziopath_The_Analyst_Becomes_Evidence.pdf",
                  "HOSTILE_BIOGRAPHER_DOSSIER.md", "Zaziopath_XRay_Two_Voices.pdf",
                  "Velvet_Knife_Report.md", "CASE STUDY — The Summoned Witness.md"],
            "b": ["Avoidant Personality Spectrum Test.pdf", "Shadow_Resume.pdf",
                  "Zazie_Productions_Instagram_Forensic_Audit.pdf",
                  "🧾 Inventory of Distinct Things.md", "Velvet_Knife_Handoff_Index.md",
                  "Identity _ Typological Vault.pdf"],
        },
    ),
    dict(
        id="X-09", name="Curatorial deletion  ⇄  Archival hoarding",
        a=("P1 · 92 stubs removed, indexed", "INDEX"),
        b=("P2 · nothing lost to history", "EVIDENCE"),
        cost=2, ctx=["B", "A", "A", "B", "B"],
        tags={
            "a": ["🗄 Stub Registry.md", "⚡ Unexpected Connections.md",
                  "🕸 Major Knowledge Graph.md", "🧾 Inventory of Distinct Things.md",
                  "create a link.md", "Zazie_Productions_Instagram_Forensic_Audit.pdf"],
            "b": ["Zazie_Productions_Complete_Discography.xlsx",
                  "Zazie_Productions_Discography.csv", "Zazie_Media_Master (1).pdf",
                  "JSON file re-export ChatGPT Memory .md", "Shadow Journal Observations .pdf",
                  "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
                  "CASE_REPORT_THE_UNFILED_RECEIPT.pdf",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md"],
        },
    ),
    dict(
        id="X-10", name="Record frame  ⇄  Art frame",
        a=("P1 · dated, hashed, tiered", "EVIDENCE"),
        b=("P2 · the doubleness is the medium", "MYTHOGRAPHY"),
        cost=3, ctx=["A", "B", "A", "B", "B"],
        tags={
            "a": ["CLAIM_PROVENANCE_LEDGER.md", "EVIDENCE_GOVERNANCE_HANDBOOK.md",
                  "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
                  "DEEP_GAP_AUDIT.md", "docs/hearing/exhibit_verification.json",
                  "HOSTILE_BIOGRAPHER_DOSSIER.md",
                  "🔍 CASE FILE — Pattern Forensics.md", "verdict_from_A.i_6"],
            "b": ["Anémone Crottin-Foufflée Identity.md",
                  "Lost_Zazie_Productions_Archive.pdf", "Mythographic Childhood.md",
                  "RECURSIVE IDENTITY CASTLES.md",
                  "THE SPALLED VESTIBULE, OR_ WHERE THE BYLAWS GO TO ROT by Zazie Productions.pdf",
                  "The_God_in_the_Syntax_Machine_Zazie_Productions_Expanded.docx",
                  "Whispers_from_Unit_G19_FinalSubmission.docx",
                  "Zaziopath_The_Uncreated_Twin.pdf",
                  "TEXTUAL_EXHUMATIONS_UNICODE.pdf",
                  "GIBBERETIC SEED SPIRAL — glocht.md", "INDEX ORGANICA.zip"],
        },
    ),
]


def nfc(s):
    return unicodedata.normalize("NFC", s)


def build_index():
    """Map NFC-normalised filename -> absolute path, so NFD-on-disk names resolve."""
    idx = {}
    for dirpath, _dirs, files in os.walk(ROOT):
        if ".git" in dirpath.replace("\\", "/").split("/"):
            continue
        for f in files:
            idx.setdefault(nfc(f), os.path.join(dirpath, f))
    return idx


SELF = "⚡ CONTRADICTION ENGINE.md"


def measure(include_self=False):
    """Measure axis loads. The engine's own file is excluded by default — a
    document that feeds its own bars invites inflation, and its mass is reported
    instead as a disclosed counterfactual (see main())."""
    idx = build_index()
    rows, missing = [], []
    for ax in AXES:
        # count how many poles each file serves inside this axis
        serving = {}
        for pole, paths in ax["tags"].items():
            for p in paths:
                key = nfc(os.path.basename(p))
                serving.setdefault(key, []).append(pole)
        masses = {"a": 0.0, "b": 0.0}
        counts = {"a": 0, "b": 0}
        for key, poles in serving.items():
            if key == nfc(SELF) and not include_self:
                continue
            path = idx.get(key)
            if path is None:
                missing.append((ax["id"], key))
                continue
            size = os.path.getsize(path)
            share = size / len(poles)
            for pole in poles:
                masses[pole] += share
                counts[pole] += 1
        rows.append(dict(ax=ax, a_bytes=masses["a"], b_bytes=masses["b"],
                         a_files=counts["a"], b_files=counts["b"]))
    return rows, missing


def draw(rows, out_png, out_svg):
    order = sorted(rows, key=lambda r: (r["b_bytes"] - r["a_bytes"]) / max(1.0, r["a_bytes"] + r["b_bytes"]))
    n = len(order)
    fig = plt.figure(figsize=(18.5, 12.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.34, 1.0], wspace=0.30,
                          left=0.245, right=0.985, top=0.775, bottom=0.095)

    # ── Panel A · the field ledger (diverging bars) ─────────────────────────────
    axA = fig.add_subplot(gs[0, 0])
    y = np.arange(n)
    total_max = max((r["a_bytes"] + r["b_bytes"]) for r in order)
    for i, r in enumerate(order):
        a, b = r["a_bytes"], r["b_bytes"]
        colA, colB = C[r["ax"]["a"][1]], C[r["ax"]["b"][1]]
        axA.barh(i, -a, height=0.62, color=colA, edgecolor=C["INK"], linewidth=0.7, zorder=3)
        axA.barh(i, b, height=0.62, color=colB, edgecolor=C["INK"], linewidth=0.7, zorder=3)
        axA.text(-a - total_max * 0.014, i, f"{a/1024:,.0f} KB · {r['a_files']}f",
                 ha="right", va="center", fontsize=7.6, color=C["INK"])
        axA.text(b + total_max * 0.014, i, f"{b/1024:,.0f} KB · {r['b_files']}f",
                 ha="left", va="center", fontsize=7.6, color=C["INK"])
        # net-lean arrow: points to the pole that holds more of the axis
        span = total_max * 0.075
        if b > a:
            axA.annotate("", xy=(span, i), xytext=(0, i),
                         arrowprops=dict(arrowstyle="-|>", color=C["INK"], lw=1.1), zorder=5)
        elif a > b:
            axA.annotate("", xy=(-span, i), xytext=(0, i),
                         arrowprops=dict(arrowstyle="-|>", color=C["INK"], lw=1.1), zorder=5)
        # cost tier as glyphs, never as colour alone
        axA.text(total_max * 1.44, i, "▲" * r["ax"]["cost"], ha="center", va="center",
                 fontsize=8.4, color=C["INK"])

    axA.axvline(0, color=C["INK"], lw=1.4, zorder=4)
    axA.set_yticks(y)
    axA.set_yticklabels(
        [f"{r['ax']['id']}  {r['ax']['name']}\n"
         f"P1 {r['ax']['a'][0].split('· ')[-1]}  |  P2 {r['ax']['b'][0].split('· ')[-1]}"
         for r in order], fontsize=8.2)
    lim = total_max * 1.56
    axA.set_xlim(-lim, lim)
    axA.set_ylim(-0.8, n - 0.2)
    axA.invert_yaxis()
    ticks = np.linspace(-lim, lim, 7)
    axA.set_xticks(ticks)
    axA.set_xticklabels([f"{abs(t)/1024:,.0f}" for t in ticks], fontsize=7.5)
    axA.set_xlabel("◀ pole 1 — committed kilobytes per pole — pole 2 ▶   (bar label: KB · files tagged)",
                   fontsize=8.8, labelpad=8)
    axA.set_title("A · THE FIELD LEDGER\nmeasured documentary mass, eleven axes, sorted by net lean",
                  fontsize=10.8, loc="left", fontweight="bold", pad=16)
    for s in ("top", "right", "left"):
        axA.spines[s].set_visible(False)
    axA.grid(axis="x", color=C["GRID"], lw=0.5, alpha=0.5, zorder=0)
    axA.text(total_max * 1.44, n - 0.55, "cost\n1–3", fontsize=7.2, color=C["INK"],
             va="center", ha="center")

    # ── Panel B · the dominance grid ────────────────────────────────────────────
    axB = fig.add_subplot(gs[0, 1])
    for j, (code, label) in enumerate(CONTEXTS):
        axB.text(j + 0.5, n + 0.30, label, ha="center", va="bottom", fontsize=7.6,
                 linespacing=1.45)
        axB.text(j + 0.5, -0.85, code, ha="center", va="center", fontsize=7.4)
    for i, r in enumerate(order):
        colA, colB = C[r["ax"]["a"][1]], C[r["ax"]["b"][1]]
        for j, code in enumerate(r["ax"]["ctx"]):
            x, yy = j, i
            if code == "A":
                axB.add_patch(Rectangle((x + 0.06, yy - 0.40), 0.88, 0.80, facecolor=colA,
                                        edgecolor=C["INK"], lw=0.6, alpha=0.95, zorder=3))
                axB.text(x + 0.5, yy, "A", ha="center", va="center", fontsize=8.6,
                         color=C["INK"], fontweight="bold", zorder=4)
            elif code == "B":
                axB.add_patch(Rectangle((x + 0.06, yy - 0.40), 0.88, 0.80, facecolor=colB,
                                        edgecolor=C["INK"], lw=0.6, alpha=0.95, zorder=3))
                axB.text(x + 0.5, yy, "B", ha="center", va="center", fontsize=8.6,
                         color=C["INK"], fontweight="bold", zorder=4)
            elif code == "AB":
                axB.add_patch(Rectangle((x + 0.06, yy - 0.40), 0.88, 0.80, facecolor="none",
                                        edgecolor=C["INK"], lw=0.6, zorder=3))
                axB.add_patch(Rectangle((x + 0.06, yy), 0.88, 0.40, facecolor=colA,
                                        edgecolor="none", alpha=0.9, zorder=3))
                axB.add_patch(Rectangle((x + 0.06, yy - 0.40), 0.88, 0.40, facecolor=colB,
                                        edgecolor="none", alpha=0.9, zorder=3))
                axB.text(x + 0.5, yy + 0.20, "A", ha="center", va="center", fontsize=7.6,
                         color=C["INK"], fontweight="bold", zorder=4)
                axB.text(x + 0.5, yy - 0.20, "B", ha="center", va="center", fontsize=7.6,
                         color=C["INK"], fontweight="bold", zorder=4)
            else:
                axB.add_patch(Rectangle((x + 0.06, yy - 0.40), 0.88, 0.80, facecolor=C["PAPER"],
                                        edgecolor=C["GRID"], lw=0.6, zorder=3))
                axB.text(x + 0.5, yy, "·", ha="center", va="center", fontsize=10,
                         color=C["GRID"], zorder=4)
    axB.set_xlim(0, len(CONTEXTS))
    axB.set_ylim(-1.15, n + 1.55)
    axB.invert_yaxis()
    axB.set_xticks([])
    axB.set_yticks([])
    for s in ("top", "right", "left", "bottom"):
        axB.spines[s].set_visible(False)
    axB.set_title("B · WHERE EACH POLE HOLDS THE FIELD\njudged layer, same row order\nA = pole 1  ·  B = pole 2  ·  split cell = both",
                  fontsize=10.4, loc="left", x=-0.005, fontweight="bold", pad=16)

    # ── figure furniture ────────────────────────────────────────────────────────
    fig.suptitle("FIG 8 · THE CONTRADICTION FIELD — eleven axes, two poles each, none resolved",
                 fontsize=15.5, x=0.012, ha="left", y=0.975, fontweight="bold")
    fig.text(0.012, 0.912,
             "Bars measure committed bytes — the vault's own unit of account (FIG 6, §00a). "
             "A file carrying both poles of one axis contributes half its size to each, so no count is double-spent.\n"
             "Panel A is arithmetic on a filed tag ledger; panel B is a curator's judgement, filed in "
             "tools/generate_contradiction_field.py. An axis with a long bar and a short bar is not a flaw; it is a lean.",
             fontsize=8.4, va="top", linespacing=1.6)
    fig.text(0.012, 0.018,
             "⚡ CONTRADICTION ENGINE · ZP-CE-2026-0930 · regenerate: python3 tools/generate_contradiction_field.py · "
             "palette: Okabe–Ito, README §00a · colour never carries meaning alone — every bar and cell is lettered",
             fontsize=7.4)

    fig.savefig(out_png, dpi=200)
    fig.savefig(out_svg)
    plt.close(fig)


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["axis_id", "axis_name", "pole", "pole_label", "stratum",
                    "files_tagged", "bytes", "kb", "share_of_axis",
                    "cost_tier", "status"])
        for r in rows:
            tot = r["a_bytes"] + r["b_bytes"]
            for pole, key in (("1", "a"), ("2", "b")):
                lab, strat = r["ax"][key]
                w.writerow([r["ax"]["id"], r["ax"]["name"], pole, lab, strat,
                            r[f"{key}_files"], round(r[f"{key}_bytes"]),
                            round(r[f"{key}_bytes"] / 1024, 1),
                            round(r[f"{key}_bytes"] / tot, 4) if tot else "",
                            r["ax"]["cost"], "open"])


def main():
    rows, missing = measure(include_self=False)
    rows_self, _ = measure(include_self=True)
    self_size = os.path.getsize(os.path.join(ROOT, SELF))
    self_delta = {}
    for r, r2 in zip(sorted(rows, key=lambda x: x["ax"]["id"]),
                     sorted(rows_self, key=lambda x: x["ax"]["id"])):
        if r["ax"]["id"] in ("X-00", "X-05"):
            ta = r["a_bytes"] + r["b_bytes"]
            tb = r2["a_bytes"] + r2["b_bytes"]
            self_delta[r["ax"]["id"]] = {
                "pole2_share_without_self": round(r["b_bytes"] / ta, 4),
                "pole2_share_with_self": round(r2["b_bytes"] / tb, 4),
                "shift_points": round(100 * (r2["b_bytes"] / tb - r["b_bytes"] / ta), 1),
            }
    out_png = os.path.join(FIGDIR, "fig8_contradiction_field.png")
    out_svg = os.path.join(FIGDIR, "fig8_contradiction_field.svg")
    csv_path = os.path.join(DATADIR, "fig8_contradiction_loads.csv")
    draw(rows, out_png, out_svg)
    write_csv(rows, csv_path)

    build = {
        "artifact": "docs/figures/fig8_contradiction_field.png",
        "generator": "tools/generate_contradiction_field.py",
        "report": "ZP-CE-2026-0930",
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "inputs": [{"path": "committed tree (per-axis tag ledger embedded in the generator)",
                    "files_resolved": sum(r["a_files"] + r["b_files"] for r in rows),
                    "files_unresolved": [f"{a}:{k}" for a, k in missing]}],
        "environment": {"python": ".".join(map(str, __import__("sys").version_info[:3])),
                        "matplotlib": matplotlib.__version__,
                        "numpy": np.__version__},
        "self_reference": {
            "excluded_from_bars": SELF,
            "note": "the engine is not tagged into its own measured bars; including it would shift "
                    "X-00 and X-05 pole 2 by the amounts below, because it is a twelfth mirror and a "
                    "twelfth pass over old material",
            "document_bytes": self_size,
            "counterfactual": self_delta,
        },
        "contains_interpretive_annotations": True,
        "interpretive_layer": ["pole tagging", "cost tier", "panel B dominance grid"],
        "measured_layer": ["file sizes", "file counts", "shares", "net lean"],
        "outputs": {},
    }
    for p in (out_png, out_svg, csv_path):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        build["outputs"][os.path.relpath(p, ROOT)] = {"sha256": h, "bytes": os.path.getsize(p)}
    with open(os.path.join(FIGDIR, "fig8_contradiction_field.build.json"), "w", encoding="utf-8") as fh:
        json.dump(build, fh, indent=2, ensure_ascii=False)

    print("FIG 8 written.")
    print(f"  self-reference: {SELF} = {self_size/1024:.1f} KB, excluded from the bars; "
          f"counterfactual shift {self_delta}")
    for r in sorted(rows, key=lambda r: r["b_bytes"] - r["a_bytes"]):
        a, b = r["a_bytes"], r["b_bytes"]
        lean = "→B" if b > a else ("→A" if a > b else "=")
        print(f"  {r['ax']['id']}  A {a/1024:8.1f} KB ({r['a_files']:2d}f)  "
              f"B {b/1024:8.1f} KB ({r['b_files']:2d}f)  {lean}")
    if missing:
        print(f"  ⚠ unresolved tag(s): {missing}")


if __name__ == "__main__":
    main()
