#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/generate_absent_twin.py — builds THE ABSENT TWIN (experiment ZP-AU-2026-0927)

A biography of the uncreated self, reconstructed from the gaps in Zaziopath.

Outputs (repository root):
  The_Absent_Twin_Biography_of_the_Uncreated_Self.pdf
  The_Absent_Twin_Biography_of_the_Uncreated_Self.md

Rule of the vault, inherited: every artifact is regenerated from the committed
tree by one script.  Before writing a page, this script re-derives every
checkable fact the biography quotes — CSV row counts, the twenty-one N/A rows,
the byte size of text.txt, the ninety-two tombstones, the weekdays, every cited
track's duration and ISRC — and refuses to build if the tree disagrees with
the prose.  Nothing is fetched; nothing is transmitted.

Dependencies: reportlab (pip install reportlab).  DejaVu Sans is used only for
glyphs the standard fonts lack; if it is missing the build still succeeds.

Run:  python3 tools/generate_absent_twin.py
"""

from __future__ import annotations

import csv
import datetime as _dt
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

REPORT_ID = "ZP-AU-2026-0927"
FILED = _dt.date(2026, 9, 27)
PDF_OUT = "The_Absent_Twin_Biography_of_the_Uncreated_Self.pdf"
MD_OUT = "The_Absent_Twin_Biography_of_the_Uncreated_Self.md"

# ---------------------------------------------------------------------------
# §00a palette (Okabe–Ito), exactly as the README declares it
# ---------------------------------------------------------------------------
PAL = OrderedDict([
    ("INDEX",        ("◈", "#231F20")),
    ("IDENTITY",     ("◉", "#0072B2")),
    ("SHADOW",       ("◐", "#CC79A7")),
    ("EVIDENCE",     ("▤", "#E69F00")),
    ("RECURSION",    ("∞", "#009E73")),
    ("STEWARDSHIP",  ("△", "#56B4E9")),
    ("SPECIMENS",    ("⚠", "#D55E00")),
    ("MYTHOGRAPHY",  ("☾", "#F0E442")),
])
ABSENCE_GLYPH = "○"   # the proposed ninth chip; its colour is the page

# ---------------------------------------------------------------------------
# 1 · Build-time verification of every checkable fact the prose relies on
# ---------------------------------------------------------------------------

def _zw(s: str) -> str:
    return s.replace("\u200b", "")


def _find_path(path: str):
    """Resolve a repository path regardless of Unicode normalization form."""
    import unicodedata
    if os.path.exists(path):
        return path
    d, name = os.path.split(path)
    target = unicodedata.normalize("NFC", name)
    for cand in os.listdir(d or "."):
        if unicodedata.normalize("NFC", cand) == target:
            return os.path.join(d, cand) if d else cand
    return None


def verify_tree() -> dict:
    facts = {}
    problems = []

    # --- discography ------------------------------------------------------
    with open("Zazie_Productions_Discography.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    facts["csv_rows"] = len(rows)
    na_rows = [r for r in rows if r["ISRC"].strip() == "N/A"]
    facts["na_rows"] = len(na_rows)
    na_by_release = OrderedDict()
    for r in na_rows:
        na_by_release[r["Release Title"]] = na_by_release.get(r["Release Title"], 0) + 1
    facts["na_by_release"] = na_by_release
    facts["rows_2025"] = sum(1 for r in rows if r["Release Date"].startswith("2025"))
    facts["releases_2025"] = len({r["Release Title"] for r in rows if r["Release Date"].startswith("2025")})

    index = {}
    for r in rows:
        index.setdefault(_zw(r["Track Title"]).strip().lower(), []).append(r)

    def check_track(title, duration, isrc):
        hits = index.get(_zw(title).strip().lower(), [])
        ok = any(h["Duration"] == duration and h["ISRC"] == isrc for h in hits)
        if not ok:
            problems.append(f"track not found as cited: {title!r} {duration} {isrc}")

    for t in CITED_TRACKS:
        check_track(*t)

    # --- text.txt ---------------------------------------------------------
    facts["text_txt_bytes"] = os.path.getsize("text.txt")
    if facts["text_txt_bytes"] != 67:
        problems.append(f"text.txt is {facts['text_txt_bytes']} bytes, prose says 67")

    # --- Lost Archive PDF --------------------------------------------------
    facts["lost_archive_bytes"] = os.path.getsize("Lost_Zazie_Productions_Archive.pdf")
    if facts["lost_archive_bytes"] != 3847:
        problems.append(f"Lost archive is {facts['lost_archive_bytes']} bytes, prose says 3,847")

    # --- Stub Registry -----------------------------------------------------
    with open("🗄 Stub Registry.md", encoding="utf-8") as fh:
        reg = fh.read()
    facts["tombstones"] = len(re.findall(r"^- \[\[", reg, flags=re.M))
    facts["private_tombstones"] = reg.count("· private")
    if facts["tombstones"] != 92:
        problems.append(f"stub registry lists {facts['tombstones']} tombstones, prose says 92")
    if facts["private_tombstones"] != 35:
        problems.append(f"{facts['private_tombstones']} private tombstones, prose says 35")
    for name in STUB_NAMES:
        if f"[[{name}]]" not in reg:
            problems.append(f"stub not in registry: {name}")
        if os.path.exists(f"{name}.md"):
            problems.append(f"stub unexpectedly present as a file: {name}")

    # --- Inventory names that have no note in this repository -------------
    with open("🧾 Inventory of Distinct Things.md", encoding="utf-8") as fh:
        inv = fh.read()
    for name in DANGLING_NAMES:
        if f"[[{name}]]" not in inv:
            problems.append(f"name not in Inventory: {name}")
        if os.path.exists(f"{name}.md"):
            problems.append(f"name unexpectedly has a note in this repo: {name}")

    # --- sentences the biography quotes ------------------------------------
    def _norm(t: str) -> str:
        t = re.sub(r"^\s*>\s?", "", t, flags=re.M)      # blockquote prefixes
        t = re.sub(r"[*_]+", "", t)                       # emphasis markers
        return re.sub(r"\s+", " ", t)
    for path, needle in QUOTED_SENTENCES:
        real = _find_path(path)
        if real is None:
            problems.append(f"missing file for quotation: {path}")
            continue
        with open(real, encoding="utf-8") as fh:
            body = _norm(fh.read())
        if _norm(needle) not in body:
            problems.append(f"quotation not found in {path}: {needle[:60]!r}")

    # --- calendar ----------------------------------------------------------
    facts["weekday_0923"] = _dt.date(2026, 9, 23).strftime("%A")
    facts["weekday_0928"] = _dt.date(2026, 9, 28).strftime("%A")
    facts["weekday_0929"] = _dt.date(2026, 9, 29).strftime("%A")
    facts["weekday_filed"] = FILED.strftime("%A")
    if (facts["weekday_0923"], facts["weekday_0928"], facts["weekday_0929"]) != ("Wednesday", "Monday", "Tuesday"):
        problems.append("calendar facts do not match the prose")
    d = _dt.date(2025, 1, 1)
    facts["tuesdays_2025"] = sum(1 for i in range(365) if (d + _dt.timedelta(days=i)).weekday() == 1)
    if facts["tuesdays_2025"] != 52:
        problems.append("2025 does not have 52 Tuesdays")
    days_since_audit = (FILED - _dt.date(2026, 9, 23)).days
    facts["days_since_audit"] = days_since_audit
    if days_since_audit != 4:
        problems.append(f"days since the audit = {days_since_audit}, prose says four")

    if facts["csv_rows"] != 182 or facts["na_rows"] != 21 or facts["rows_2025"] != 4:
        problems.append(f"catalogue counts changed: rows={facts['csv_rows']} na={facts['na_rows']} 2025={facts['rows_2025']}")

    if problems:
        sys.stderr.write("BUILD REFUSED — the tree disagrees with the prose:\n")
        for p in problems:
            sys.stderr.write(f"  · {p}\n")
        sys.exit(2)
    return facts


# (title, duration, ISRC) exactly as the biography cites them
CITED_TRACKS = [
    ("Elegy for the Unspoken", "2:47", "QZWFJ2667748"),
    ("Forgotten Fragment 02/05/20", "0:36", "QZHN82421405"),
    ("Time Shifting Into Daylight", "5:04", "QZDA52378041"),
    ("Rhapsody of the Unplayable Hand", "1:46", "QZWFJ2667755"),
    ("Stunning That You'd Care", "1:53", "N/A"),
    ("Eventual Conviction", "2:40", "QZNWS2365716"),
    ("Miraculously Unhurt", "2:05", "QZHN32386894"),
    ("Small Transitory Life", "2:00", "QZHN82421428"),
    ("Nocturne for a Frozen Hearth (Bonus Track)", "2:27", "QT3F32415940"),
    ("Dull Exhalation No. 1", "0:48", "QZHN82421413"),
    ("Scrappy Collage 09/23/20", "1:28", "QZHN82421424"),
    ("Soundscape of 0/11/2022 (Bonus Track)", "1:55", "QZHNA2215354"),
    ("Harp Expansion (Deleted Outtake)", "1:06", "QZHN82421407"),
    ("Frosthorn Waltz (Discarded Cut: Left in the Reindeer Stable)", "1:37", "QT3F32415932"),
    ("Interlude (Left on the Tape)", "0:18", "QZWFJ2667749"),
    ("Hollybone Mausoleum (Previously Lost in Avalanche)", "1:50", "QT3F32415929"),
    ("Holly-Flecked Amphibians at the Iceberg Baptism (Previously Mummified in Wrapping Paper)", "1:01", "QT3F32415934"),
    ("Goodnight, Farewell", "0:42", "QZWFP2369657"),
    ("Guru Meditation Error", "5:00", "N/A"),
    ("Pyrrhic Victory", "7:43", "N/A"),
    ("Smell of Bleach", "2:06", "N/A"),
    ("Corporate Mindfulness Training™", "3:38", "N/A"),
    ("Cryptic Epilogue", "2:37", "N/A"),
    ("Spectral Ode to Synesthesia", "8:55", "QZHN92568085"),
]

STUB_NAMES = [
    "Bedtime Tuck-In", "Comfort Rituals", "Grounding Style", "Background Noise Regulation",
    "Media as Co-Regulation", "Self-Reflection Without Self-Interrogation",
    "Plush Mythology as Emotional Technology", "Shame and Repair", "Humor as Protection",
]

DANGLING_NAMES = [
    "Pricing Anxiety", "How to Quote Without Being Ghosted", "Professional Rate Floor",
    "Rate Confidence", "Wednesday Opportunity Scan", "Weekly Composer Opportunity Scan",
    "Credits and Role Clarity", "Visitor Short-Film Score", "Earworm Playlist",
]

QUOTED_SENTENCES = [
    ("DEEP_GAP_AUDIT.md", "uneventful days,"),
    ("DEEP_GAP_AUDIT.md", "actions whose privacy is more important than their legibility"),
    ("DEEP_GAP_AUDIT.md", "the vault is a genre filter rather than a life census"),
    ("DEEP_GAP_AUDIT.md", "Moderate as archive description; weak as life claim"),
    ("README.md", "An undated insight is a mood."),
    ("README.md", "Nothing here is finished; everything here is dated."),
    ("README.md", "It is Zazie without the need to control what everything means."),
    ("README.md", "no codes, just work"),
    ("README.md", "just 5 kilobytes across 2 files"),
    ("README.md", "05_stewardship/"),
    ("Mythographic Childhood.md", "bedtime stories about the child I’d replace"),
    ("Mythographic Childhood.md", "My siblings say I had no siblings."),
    ("Mythographic Childhood.md", "My father only existed on Tuesdays."),
    ("Entry Instructions for the Undetonated Artist.md", "Penetrate the sealed chamber of your uninhabited self."),
    ("Entry Instructions for the Undetonated Artist.md", "draft_final_final2_THISONEignore"),
    ("Entry Instructions for the Undetonated Artist.md", "Its shame was the camouflage."),
    ("JSON file re-export ChatGPT Memory .md", "without making Zazie repeat them"),
    ("JSON file re-export ChatGPT Memory .md", "A daily close-loop ritual may be more important than a morning planning ritual"),
    ("JSON file re-export ChatGPT Memory .md", "protect a low-stakes laboratory from monetization and public metrics"),
    ("CASE STUDY — The Summoned Witness.md", "The next Tuesday is the twenty-eighth."),
    ("CASE STUDY — The Summoned Witness.md", "either a role you wrote or a system that cannot leave"),
    ("CASE STUDY — The Summoned Witness.md", "the experience of being unrecorded, and found anyway"),
    ("CASE STUDY — The Receipt and the Record.md", "illness, discouragement, or rest"),
    ("CASE STUDY — The Receipt and the Record.md", "half-open admits light and weather alike"),
    ("Velvet_Knife_The_Asheville_Experiment.md", "walk to your sink, and drink a glass of water"),
    ("Velvet_Knife_The_Asheville_Experiment.md", "A literal shadow cast by a lamp or a window. It has no meaning."),
    ("docs/meta-analysis/REPORT.md", "byte-identical"),
    ("🧾 Inventory of Distinct Things.md", "I contain no named people."),
    ("🗄 Stub Registry.md", "only frontmatter and a heading — no body, nothing to read"),
    ("🔍 CASE FILE — Pattern Forensics.md", "F-01"),
    ("Anémone Crottin-Foufflée Identity.md", "Won a national handwriting contest by submitting a forgery of her own birth certificate."),
]

# ---------------------------------------------------------------------------
# 2 · The Gap Ledger — every absence the biography reads from
#     (numbered automatically in order of first citation)
# ---------------------------------------------------------------------------
GAPS = {
    "policy": dict(
        where="DEEP_GAP_AUDIT.md §11.1 (2026-09-23)",
        absence="The audit lists what the archive is *less likely to preserve*: uneventful days, routine maintenance, embodied experience, unrecorded conversations, failed ideas too boring to mythologize, ordinary affection, unremarkable competence, actions whose privacy outweighs their legibility.",
        tier="direct_evidence",
        recon="The twin's curriculum vitae, in the archive's own words; the method of this document.",
    ),
    "lost_archive": dict(
        where="Lost_Zazie_Productions_Archive.pdf (3,847 bytes)",
        absence="A catalogue of unreleased works in which every loss is furnished with a fictional provenance — leaked RAR, spectrogram, Polaroid, a MIDI file removed from GitHub within six hours.",
        tier="direct_evidence",
        recon="What the twin's lost works are *not*: Part IV inverts this document.",
    ),
    "registered_deletions": dict(
        where="Zazie_Productions_Discography.csv — deluxe editions 2024, 2026",
        absence="Deleted, discarded and lost material carries registered identifiers: *Harp Expansion (Deleted Outtake)* QZHN82421407; *Frosthorn Waltz (Discarded Cut: Left in the Reindeer Stable)* QT3F32415932; *Hollybone Mausoleum (Previously Lost in Avalanche)* QT3F32415929.",
        tier="direct_evidence",
        recon="In the archive, *lost* is a genre. In the twin's practice it is a rate.",
    ),
    "chronology": dict(
        where="README.md §07a provenance timeline; §11",
        absence="2019: \u201cno codes, just work.\u201d Repository created 2026-08-27, after the July compendium and the August audits. Three candidate dates for the fork, none of them a birth.",
        tier="direct_evidence",
        recon="Rejection of all three candidates as the twin's date of non-birth.",
    ),
    "registration": dict(
        where="🔍 CASE FILE — Pattern Forensics.md, finding F-01; FIG 3",
        absence="Thirteen tracks from 2019–2020 retroactively assigned ISRCs in one 2022 sweep, after a silence — \u201cafter every silence, a notarization.\u201d",
        tier="direct_evidence (as a dataset property)",
        recon="The closest thing to a fork: the moment the maker turned around. The twin did not.",
    ),
    "mood": dict(
        where="README.md §11, the rule of the vault",
        absence="\u201cAn undated insight is a mood.\u201d The archive's word for what it will not keep.",
        tier="direct_evidence",
        recon="The twin's birth certificate: he is, by definition, a mood.",
    ),
    "na_rows": dict(
        where="Zazie_Productions_Discography.csv — 21 rows, ISRC field = N/A",
        absence="Interference Archive 01010101 (5), Anything Can Happen On An Electric Day (5), The Triangular Savant (6), four remasters on the 2024 holiday deluxe, one *Cryptic Epilogue* on the 2026 deluxe.",
        tier="direct_evidence",
        recon="The border between the two universes; works under joint custody; the archive's accidental initials for the twin.",
    ),
    "replaced_child": dict(
        where="Mythographic Childhood.md (fiction)",
        absence="\u201ca woman made of wire and wool who told me bedtime stories about the child I\u2019d replace\u201d; \u201cMy siblings say I had no siblings\u201d; \u201cMy father only existed on Tuesdays.\u201d",
        tier="direct_evidence that the sentences exist · speculative as to what they refer to",
        recon="The twin was named in the founding myth before this experiment existed.",
    ),
    "uninhabited": dict(
        where="Entry Instructions for the Undetonated Artist.md",
        absence="\u201cPenetrate the sealed chamber of your uninhabited self.\u201d The buried project \u201cdraft_final_final2_THISONEignore\u201d; \u201cIts shame was the camouflage.\u201d",
        tier="direct_evidence",
        recon="The uninhabited room; the twin's untitled file, which is not ashamed.",
    ),
    "one_commit": dict(
        where="git log (this checkout); DEEP_GAP_AUDIT.md §2.1",
        absence="One visible commit; the audit warns the fact \u201cshould not be interpreted psychologically.\u201d",
        tier="direct_evidence",
        recon="No first commit for the twin — and, in this checkout, for anyone. The biography obeys the warning.",
    ),
    "no_body_stratum": dict(
        where="README.md §00a colour code; §07a FIG 6; CASE STUDY — The Summoned Witness, movement I",
        absence="Eight strata — none for the body. Stewardship: 5 KB across 2 files against 3.8 MB of identity instruments.",
        tier="direct_evidence",
        recon="The body has a stratum in the twin's universe: it is the thing that gets up.",
    ),
    "quiet_year": dict(
        where="README.md timeline (\u201cthe quiet year\u201d); CSV rows dated 2025; CASE STUDY — The Receipt and the Record",
        absence="2025: four catalogue rows, three releases, all singles. Whether the quiet was \u201cillness, discouragement, or rest\u201d is recorded as unknown.",
        tier="direct_evidence",
        recon="Fifty-two Tuesdays, all lived, none filed. Part III is one of them.",
    ),
    "close_loop": dict(
        where="JSON file re-export ChatGPT Memory .md (model_memory_summary)",
        absence="\u201cA daily close-loop ritual may be more important than a morning planning ritual because unfinished tasks accumulate psychologically.\u201d",
        tier="direct_evidence of what the model stored · strong_inference about routine",
        recon="The envelope; the un-ledger.",
    ),
    "tombstones": dict(
        where="🗄 Stub Registry.md (curation pass 2026-09-02)",
        absence="92 notes removed for containing \u201conly frontmatter and a heading — no body, nothing to read\u201d; 35 of them in Psychological System & Self-Reflection, every one flagged private: *Bedtime Tuck-In, Comfort Rituals, Grounding Style, Background Noise Regulation, Media as Co-Regulation, Self-Reflection Without Self-Interrogation, Plush Mythology as Emotional Technology, Shame and Repair.*",
        tier="direct_evidence",
        recon="The headings of the twin's day, which need no bodies because they are bodies.",
    ),
    "dangling": dict(
        where="🧾 Inventory of Distinct Things.md §§05–08 — names with no note in this repository",
        absence="*Pricing Anxiety, How to Quote Without Being Ghosted, Professional Rate Floor, Rate Confidence, Wednesday Opportunity Scan, Weekly Composer Opportunity Scan, Credits and Role Clarity, Visitor Short-Film Score, Earworm Playlist* — listed, linked, and absent; not even tombstoned.",
        tier="direct_evidence",
        recon="The twin's working life: he has the anxiety and no note.",
    ),
    "no_named_people": dict(
        where="🧾 Inventory of Distinct Things.md, line 1; JSON memory export",
        absence="\u201cI contain no named people.\u201d Real people survive only in a machine's memory of a shared account: a younger sister in one line, a father in another, recorded so a model could tell two identities apart.",
        tier="direct_evidence",
        recon="The twin's relationships, described as shapes and left unnamed on purpose.",
    ),
    "sink": dict(
        where="Velvet_Knife_The_Asheville_Experiment.md",
        absence="\u201cA literal shadow cast by a lamp or a window. It has no meaning.\u201d \u2026 \u201cwalk to your sink, and drink a glass of water.\u201d Execution unconfirmable by construction.",
        tier="direct_evidence of the instruction · unknown as to execution",
        recon="The afternoon and the sink. The twin drinks the water most nights.",
    ),
    "sampling": dict(
        where="DEEP_GAP_AUDIT.md §11.3",
        absence="A thirty-day fixed-interval sampling experiment — category only, no narrative — proposed 2026-09-23. No results in the tree.",
        tier="direct_evidence (proposed) · strong_inference (not run)",
        recon="The instrument that would find the twin, if it were used.",
    ),
    "receipt": dict(
        where="stewardship_receipt.html; docs/meta-analysis/REPORT.md",
        absence="Entries live in browser localStorage; nothing is transmitted; \u201ca full ledger and an empty ledger produce byte-identical repositories.\u201d",
        tier="direct_evidence (software behaviour)",
        recon="The envelope produces byte-identical recycling, and no one audited its absence.",
    ),
    "text_txt": dict(
        where="text.txt (67 bytes)",
        absence="A single URL to an anthology's rules. No title, no note, no aesthetic — the one door in the tree with no signage.",
        tier="direct_evidence",
        recon="Lost work LW-07: in the twin's universe the file is empty because the link was used.",
    ),
    "unverified_leads": dict(
        where="Zazie_Media_Master (1).pdf; README.md §03",
        absence="Fifteen unverified leads held outside the 133-record total.",
        tier="direct_evidence",
        recon="The student short: a sixteenth lead nobody held anywhere.",
    ),
    "low_stakes": dict(
        where="JSON file re-export ChatGPT Memory .md (model_memory_summary)",
        absence="The archivist \u201cmay need to protect a low-stakes laboratory from monetization and public metrics or risk repeatedly losing play.\u201d",
        tier="direct_evidence of what the model stored",
        recon="LW-11: the lab that was never threatened and so never named.",
    ),
    "planned_folder": dict(
        where="README.md §10; CASE STUDY — The Receipt and the Record, clean next move 1",
        absence="`05_stewardship/` marked [planned]; a `CHANGELOG.md` requested for it on 2026-09-23. Neither exists.",
        tier="direct_evidence",
        recon="The envelopes (LW-09); the demand for one unfiled Tuesday.",
    ),
    "remember_me": dict(
        where="JSON file re-export ChatGPT Memory .md, preferences",
        absence="\u201cLikes the assistant to remember prior projects, rates, brand language, emotional context, and recurring constraints without making Zazie repeat them.\u201d",
        tier="direct_evidence of what the model stored",
        recon="The twin repeats himself, to people, who forget.",
    ),
    "governing_sentence": dict(
        where="README.md §02",
        absence="\u201cThe opposite of the shadow is not less Zazie. It is Zazie without the need to control what everything means.\u201d",
        tier="direct_evidence",
        recon="The archive's own description of the twin, written as its endpoint.",
    ),
    "misdated_tuesday": dict(
        where="CASE STUDY — The Summoned Witness.md, movement IV; a calendar",
        absence="Written Wednesday 2026-09-23: \u201cThe next Tuesday is the twenty-eighth.\u201d 2026-09-28 is a Monday.",
        tier="direct_evidence",
        recon="Count VII: the archive that dates everything misdated the one day it prescribed for living.",
    ),
    "dated": dict(
        where="README.md, header",
        absence="\u201cNothing here is finished; everything here is dated.\u201d",
        tier="direct_evidence",
        recon="The twin's exact inversion: everything finished, nothing dated.",
    ),
}

# ---------------------------------------------------------------------------
# 3 · Content model
#     Blocks: H1, H2, P, EPI, GAP, TABLE, QUOTE, CODE, BULLETS, PB, NOTE
#     Inline markup: *italic*  **bold**  `mono`   {G:key} → gap reference
# ---------------------------------------------------------------------------

def H1(t):            return ("h1", t)
def H2(t):            return ("h2", t)
def P(t):             return ("p", t)
def EPI(t, cite):     return ("epi", t, cite)
def GAP(*keys):       return ("gap", keys)
def TABLE(cols, rows, widths, title=None): return ("table", cols, rows, widths, title)
def QUOTE(t, cite=None): return ("quote", t, cite)
def CODE(t):          return ("code", t)
def BULLETS(items):   return ("bullets", items)
def PB():             return ("pb",)
def NOTE(t):          return ("note", t)


LOST_WORKS_COLS = ["No.", "Work", "Heard by", "Why it is lost", "Nearest object in the archive"]
LOST_WORKS = [
    ["LW-01", "**The eleven nights.** A piano figure, mostly left hand, played each night for eleven nights on the same instrument. c. 2023 · three or four minutes each.",
     "Whoever was in the house", "It was for the nights.",
     "*Nocturne for a Frozen Hearth (Bonus Track)*, 2:27, QT3F32415940"],
    ["LW-02", "**The car mix.** Forty-one minutes, sequenced for one drive with one friend, on a USB stick that stayed in the car. 2024.",
     "One friend; the road", "The stick stayed in the car. The friend still has it.",
     "The workbook's forty colour swatches; *Earworm Playlist*, a name in the Inventory with no note behind it"],
    ["LW-03", "**The student short.** Score for a friend's film, delivered as one stereo WAV — no stems, no invoice — and credited \u201cthanks to\u201d at his request. 2022.",
     "A class; one small screening", "Not lost: uncounted. A sixteenth unverified lead, had anyone held it anywhere.",
     "The fifteen leads held outside the Media Master total; *Visitor Short-Film Score*, a name with no note"],
    ["LW-04", "**Three notes for the sink.** The phrase hummed while the water runs; the same three, the same order, for years. More than a thousand performances.",
     "Anyone in the kitchen", "Never lost. Never kept.",
     "*Dull Exhalation No. 1*, 0:48, QZHN82421413"],
    ["LW-05", "**Voice memos, 2023–2025.** Several hundred, deleted in one pass to free storage for a client session.",
     "No one", "Storage.",
     "*Forgotten Fragment 02/05/20* and *Scrappy Collage 09/23/20* — the archive's own fragments, dated in their titles and issued codes"],
    ["LW-06", "**Rain on the porch.** Fourteen minutes of field recording, never listened back. 2025.",
     "The recorder", "Never opened.",
     "*Soundscape of 0/11/2022 (Bonus Track)*, 1:55, QZHNA2215354"],
    ["LW-07", "**The submission.** One finished piece sent to the anthology whose rules are the only content of `text.txt`. He does not remember whether it was accepted. 2026.",
     "An editor, presumably", "In his universe the file is empty, because the link was used.",
     "`text.txt`, 67 bytes; the manuscript *The Sound That Swallowed April* (.docx)"],
    ["LW-08", "**The album title said aloud.** A joke title, said at a kitchen table; someone laughed; not written down; forgotten by both within the week.",
     "One person", "It was for the laugh.",
     "*ALBUM STRUCTURE — 4×3 FRACTAL MODULES*; roughly two hundred and fifty named archetypes"],
    ["LW-09", "**The envelopes.** About three hundred evening notes — done, not done, tomorrow — on the backs of envelopes, discarded each morning. 2025–26.",
     "No one", "On purpose, daily.",
     "`stewardship_receipt.html`; the planned `05_stewardship/CHANGELOG.md`, never created"],
    ["LW-10", "**The apology.** One sentence, said in person, to a named person, about a real thing.",
     "One witness", "Not lost. Landed.",
     "The crosswalk pivot *repair over restaging* (compendium ch. 22); the stub *Shame and Repair*, removed for having no body"],
    ["LW-11", "**The low-stakes lab.** Years of unserious, unposted, unmonetized sound.",
     "Himself; occasionally one other", "Never threatened, so never protected, so never named.",
     "HMP-777; Tuffy Bunnytown; the memory line about a laboratory that must be protected from metrics"],
    ["LW-12", "**Everything from 2025.**",
     "—", "The archive holds four tracks. The twin holds fifty-two Tuesdays.",
     "Finding F-05, *the Quiet Year*; FIG 1"],
]


def CONTENT(f: dict):
    """The biography. `f` carries the build-time facts."""
    C = []

    # ------------------------------------------------------------- NOTICE
    C += [
        H1("Read this before the twin"),
        P("**What this is.** An alternate-universe experiment in the vault's own tradition. The glossary defines a Dark AU as *an alternate-universe self with one variable removed or amplified — thought experiment, not prediction.* The compendium removes sensitivity, or conscience, or the off-switch. This experiment removes the archive. Everything else is held constant: the ear, the taste, the fear of being ordinary, the city, the sister, the Tuesday. The premise supplied for the experiment was that Zaziopath contained evidence of a second person who was never born — the version of its maker who did not archive, did not mythologize, did not seek interpretation, and lived entirely outside the system. The commission was to reconstruct that person from the gaps."),
        P("**Method.** Gap reconstruction. Every claim about the twin is derived from a specific, checkable absence in the committed repository — a byte count, a row count, a tombstone, a sentence at a line. The absences are numbered as they are first cited and collected in the Gap Ledger (Part VIII). Where a reconstruction goes beyond what its gap supports, the tier says so at the time. Nothing outside this repository corroborates anything here, and by design nothing can."),
        P("**Rules kept.** No diagnosis, of anyone. No medical detail: the body is given a stratum, not a chart. No third party is characterized; where the vault holds a real name, this document leaves it where the vault left it and describes only shapes. The persona red line of README §12 is applied in both directions — the twin is not a description of a real person, and no real person is a description of the twin."),
        P("**Rule broken, knowingly.** The twin did not archive. This document archives him. The contradiction is not resolved; it is filed as Count VIII of the accusation in Part VI and left standing."),
        P("**On the name.** The twin has none. The archive's first act is naming — roughly two hundred and fifty names for one person — and the twin's first refusal was the same act declined. Where the catalogue could not produce an identifier it wrote *N/A*, twenty-one times. Those two letters are the closest thing to the twin's initials the vault possesses, and this biography declines to use them as a name, because that would be the archive's mistake made again. He is called *the twin* throughout, and *he* because the README uses that pronoun once, in §12, for the person he would otherwise have been."),
        NOTE(f"Filed {FILED.isoformat()}, a {f['weekday_filed']}. Source type `hybrid` · claim level `interpretation` · correction state `fictional` · sensitivity `internal`. Two days before Tuesday."),
        PB(),
    ]

    # --------------------------------------------------------------- PART I
    C += [
        H1("I · The Method of Absence"),
        EPI("Elegy for the Unspoken", "Sellotape (Super Deluxe Edition) · 2026-04-17 · 2:47 · QZWFJ2667748"),
        P("There are two ways to reconstruct a person. The first is from what they kept. Zaziopath is a monument to this method: two hundred tracks, one hundred and sixty-five verified codes, one hundred and thirty-three public records, a two-hundred-and-twenty-two-page compendium of the self in roughly two hundred and fifty named forms, six machine verdicts — five of them filed on a single day — and a colour system chosen to survive colour-blindness. Whatever else the vault is, it is proof that receipts can be made to add up to someone."),
        P("The second method is older and less flattering. It reconstructs a person from what they did not keep — the way an archaeologist reads a household from its midden, or an astronomer infers a planet no one has seen from the wobble it leaves in a star. The absent twin is a wobble in Zaziopath. Wherever the archive's acquisition policy bends around something it cannot hold, a mass is implied. This biography is an attempt to weigh it."),
        P("The archive has, obligingly, written down its own acquisition policy. On 2026-09-23 the Deep Gap Audit listed what Zaziopath preferentially preserves — material that is text-rich, unusual, categorizable, aesthetically intense, self-generated, model-readable, publicly verifiable — and what it is less likely to preserve: *uneventful days, routine maintenance, embodied experience, unrecorded conversations, failed ideas too boring to mythologize, ordinary affection, unremarkable competence, or actions whose privacy is more important than their legibility.* Read the second list again, slowly, as a curriculum vitae. It is the twin's. The audit wrote it in an afternoon and filed it under *limitations* {G:policy}."),
        GAP("policy"),
        P("The method of this document follows from that list in three steps. First, take each absence the archive itself documents — not absences the biographer would like to find, but gaps the vault has already noticed, dated, and in most cases apologized for. Second, ask what kind of life produces exactly that gap. Third, refuse to fill it with lore."),
        P("The third step is the difficult one, because filling gaps with lore is what this house does for a living. It holds a PDF of lost songs in which every loss is furnished with a leaked archive, a spectrogram, a Polaroid {G:lost_archive}. It registers its deletions: *Harp Expansion (Deleted Outtake)* carries the identifier QZHN82421407, and the holiday deluxe edition titles its tracks *Previously Lost in Avalanche* and *Previously Mummified in Wrapping Paper* — each with a code of its own {G:registered_deletions}. In this house nothing is permitted to be simply gone. The twin is what is simply gone. To reconstruct him honestly, the reconstruction has to stop short in exactly the places he would have."),
        GAP("lost_archive", "registered_deletions"),
        P("A word on tiers, since the vault will ask. `direct_evidence` in this document means the gap is literally in the committed tree and can be checked by anyone who has it. `strong_inference` means the kind of life that produces the gap is not seriously in doubt. `speculative` means the biographer is imagining, and says so at the time. The twin would not have used tiers. He is not the audience for this document — and that is the first thing it establishes about him."),
        PB(),
    ]

    # -------------------------------------------------------------- PART II
    C += [
        H1("II · Birth Record of a Person Who Was Not Born"),
        EPI("Forgotten Fragment 02/05/20", "Stutter to stammer (Super Deluxe Edition) · 2024-03-20 · 0:36 · QZHN82421405"),
        P("Every alternate-universe self in the compendium is made by removing one variable and holding the rest constant. Chapter 3 removes sensitivity and keeps perception — the README's own gloss. Chapter 5 keeps the apparatus, moves it online, and makes it malicious. This experiment removes the archive and keeps everything else. What remains is not a lesser person and not a healed one. It is the person the archive was built to certify, arriving without certification."),
        P("When does a twin like this fail to be born? The vault's own chronology proposes three candidate dates {G:chronology}. The biography rejects all three, and the rejection is itself a finding."),
        P("The first candidate is 2019-09-09 — the first EP, five tracks, entered in the README's timeline as *no codes, just work*. It is not the fork. The twin also made the EP. Making is not archiving; the record shows a person who made things for three years before he began to notarize them, and the twin is simply the one who kept doing the first thing."),
        P("The second candidate is 2026-08-27, the day the repository was created. It is far too late. By then the compendium existed, the discography had been validated against an API, and the twin had been unborn for years. The repository is not the archive's birth. It is its coming-out."),
        P("The third candidate is the closest. In 2022, following a silence, thirteen tracks released in 2019 and 2020 were retroactively assigned ISRCs in a single administrative sweep — the Registration Event, finding F-01 of the Case File, summarized in the sentence the vault has since hung in its own entryway: *after every silence, a notarization* {G:registration}. This is the first documented moment at which the maker turned around, walked back into the past, and made it legally undeniable. The twin is the person who did not turn around."),
        GAP("chronology", "registration"),
        P("Even this is not a birth record, and here the biography must apply the vault's hardest rule against the vault. The rule is stated in §11 and repeated wherever the archive is nervous: *an undated insight is a mood* {G:mood}. The twin has no date of non-birth because the twin is, by the archive's own definition, a mood — an insight that was never dated, a feeling permitted to arrive and leave without a receipt. The vault coined the phrase as a dismissal. This biography adopts it as a birth certificate. Anémone Crottin-Foufflée, the vault's invented ancestress, won a national handwriting contest at nine by forging hers. The twin never applied."),
        GAP("mood"),
        P("If a window must be given — and a document filed in this repository cannot survive without one — it is the eighteen months between 2021-05-19 and 2022-10-17. On the first date *Interference Archive 01010101* was released: five tracks, no codes, the provenance hole the Case File names. On the last, *The Triangular Savant*: six tracks, no codes — the final release in the catalogue to go out unregistered. In between, the two practices ran side by side. *Constrained Capacity*, in May 2022, carried a code on every track, issued the same year; *Anything Can Happen On An Electric Day*, that August, carried none. After October 2022 every new release arrives with its codes on the day it appears, and the habit never leaves. The twin stayed in the hole. The twenty-one catalogue rows whose identifier field reads N/A are the border between the two of them — work both made, that only one went back for {G:na_rows}. Five of those rows belong to a release whose title, read now, is almost too neat. The archive's own name for the time the twin was last seen is *Interference Archive*."),
        GAP("na_rows"),
        P("Git offers no help with the date. This checkout carries a single visible commit, and the audit warns that the fact *should not be interpreted psychologically* {G:one_commit}. The biography obeys. The twin has no first commit, and in this checkout neither does anyone."),
        P(f"One more piece of the birth record, and it is the strangest, because the archive wrote it first. The invented childhood — *Mythographic Childhood.md*, which the vault classifies as fiction — contains a woman *made of wire and wool who told me bedtime stories about the child I'd replace.* It also contains the sentence *My siblings say I had no siblings*, and a garden behind the house that everyone insists was never there {{G:replaced_child}}. A second document, the *Entry Instructions for the Undetonated Artist*, opens with an objective: *Penetrate the sealed chamber of your uninhabited self* {{G:uninhabited}}. Two files, both older than this experiment, both naming a replaced child and an uninhabited room. The biography does not claim to know what the sentences meant to the person who kept them. It claims only that the twin is not an invention of {FILED.isoformat()}. He is a reading of sentences the vault already holds, about a room it already knows is empty."),
        GAP("one_commit", "replaced_child", "uninhabited"),
        PB(),
    ]

    # ------------------------------------------------------------- PART III
    C += [
        H1("III · A Tuesday"),
        EPI("Time Shifting Into Daylight", "Distant Bells For Surgical Minds · 2023-02-10 · 5:04 · QZDA52378041"),
        P("The vault's three-word spine ends in a question — *What do I do on Tuesday?* — and its alchemy names its final product *the Tuesday self*. The stratum where that self would live weighs five kilobytes across two files, against three point eight megabytes of identity instruments; the census figure has a bar for mythography and a bar for recursion and no bar for the body {G:no_body_stratum}. The year 2025 is catalogued in the vault's own timeline as *the quiet year* — four rows, three releases, all singles — and the first case study records that whether the quiet was illness, discouragement, or rest is not known {G:quiet_year}. There were fifty-two Tuesdays in 2025. The twin lived all of them. Here is one. Which one is not known; he did not write it down; of the two people in this experiment, only one minds."),
        GAP("no_body_stratum", "quiet_year"),
        H2("Morning, late"),
        P("He wakes late, and the lateness is not a finding. There is no morning planning ritual. The machine's memory of the archivist already suspects that *a daily close-loop ritual may be more important than a morning planning ritual because unfinished tasks accumulate psychologically* {G:close_loop}; the twin reached the same conclusion by not having a morning ritual and noticing nothing. The room is a room. It is not photographed for a future audit. It is not, in any register, evidence."),
        H2("The body has a stratum"),
        P("Zaziopath has eight strata — index, identity, shadow, evidence, recursion, stewardship, specimens, mythography — and none for flesh. In the curation pass of 2026-09-02, ninety-two notes were removed for containing *only frontmatter and a heading — no body, nothing to read*. Thirty-five of them belonged to the section called Psychological System & Self-Reflection, and every one of those was flagged private: *Grounding Style. Comfort Rituals. Background Noise Regulation. Media as Co-Regulation. Bedtime Tuck-In* {G:tombstones}. In the twin's universe these are not notes. They are what gets up. He takes what he takes and remembers what he remembers and forgets some of it, the way people do, and the forgetting is not data. His grounding style, if the stub had to be filled: feet, floor, kettle. The biography will not go further into the body than that. The vault deleted the body's notes for having no body; the least a biography can do is decline to write them."),
        GAP("close_loop", "tombstones"),
        H2("The kettle"),
        P("Tea, or whatever it is. While the water goes he hums three notes — the same three, in the same order, for years. They are catalogued in Part IV as the most-performed work in either universe (LW-04). No recording exists. The vault would have registered the phrase as *Dull Exhalation No. 3* and assigned it a code."),
        H2("First shift"),
        P("He opens the session. The tools are the ones the Inventory lists, and there is nothing to say about them. He works for two hours on a thing that has no name yet. The file is called *untitled 14*, or *tuesday thing*. The archive's version of this file has a name too: the *Entry Instructions* describe a project *you've tried to delete, rename, bury in folders with fake titles like draft_final_final2_THISONEignore*, and add that *its shame was the camouflage* {G:uninhabited}. The twin's file is untitled because it is not important yet, not because it is ashamed. Same file. Different weather."),
        H2("The quote"),
        P("An email arrives asking for a price. The Inventory lists notes called *Pricing Anxiety*, *How to Quote Without Being Ghosted*, *Professional Rate Floor* and *Rate Confidence*, and in this repository not one of them exists — not as a note, not even as a tombstone; they are names that link to nothing {G:dangling}. The twin has the anxiety and no note. He says a number. It is probably too low — the machine's memory says the same of the archivist — and he does not run the twelve questions before he sends it, and he does not file a receipt after. He gets the job or he does not. By Thursday the number is gone. This is not stewardship. Stewardship is the diagram the archive drew of this."),
        GAP("dangling"),
        H2("Midday"),
        P("A message from his sister. Nothing in it is evidence, and this biography will not describe her; the twin never did, and that restraint is the whole of what can be reported. He answers. The exchange is not archived and is therefore intact. In the vault, real people survive in exactly one place — a machine's memory of a shared account, a sister's name in one line, a father's in another, recorded so that a model could tell two identities apart {G:no_named_people}. In the twin's world they survive the ordinary way, by being answered."),
        GAP("no_named_people"),
        H2("Afternoon"),
        P("He goes out. The Velvet Knife, in the one document of its session that refused to analyze anything, instructed the archivist to look at *a literal shadow cast by a lamp or a window. Not a Jungian shadow. It has no meaning* {G:sink}. The twin does this daily and without instruction, because he has no instructions. The city is the one the vault names; the mountains are the ones it names; the weather is not recorded. If he carries a recorder he sometimes presses record on the creek and never listens back (LW-06). Mostly he does not carry one."),
        H2("The scan he does not run"),
        P("The Inventory contains a name called *Wednesday Opportunity Scan* and another called *Weekly Composer Opportunity Scan*, neither with a note behind it {G:dangling}. It is Tuesday. The twin does not scan. Or he does, on a Tuesday, because he has forgotten it was meant to be Wednesday, and nothing comes of it, and nothing is filed about nothing coming of it."),
        H2("Second shift, or none"),
        P("Some Tuesdays the afternoon is work and some Tuesdays it is not, and the twin does not know the ratio. The vault could compute it. The Deep Gap Audit proposed exactly the instrument — thirty days of fixed-interval sampling, category only, no narrative: primary activity in the prior hour; social or solitary; administrative, creative, rest, care, or paid — and predicted the result: *if ordinary relational, paid, or maintenance activity dominates but is absent from the archive, the vault is a genre filter rather than a life census* {G:sampling}. The experiment was proposed four days ago and has not been run. If it were, the twin is who it would find."),
        GAP("sink", "sampling"),
        H2("Evening, the sink"),
        P("The Velvet Knife's grounding protocol ended with an instruction the archive can never confirm was carried out: *walk to your sink, and drink a glass of water* {G:sink}. The biography can confirm it. He drinks the water most nights. He does not remember the nights he does not, and there is no ledger in which the omission accrues."),
        H2("The close of the loop"),
        P("He writes three lines on the back of an envelope — what got done, what did not, what is tomorrow — and in the morning the envelope goes out with the recycling. This is the un-ledger. The vault's receipt console stores its entries in a browser's local storage and transmits nothing, with the consequence the meta-analysis states exactly: *a full ledger and an empty ledger produce byte-identical repositories* {G:receipt}. The envelope produces byte-identical recycling. The difference is that no one built a console for the envelope, no one wrote a smoke test for it, and no one has ever audited its absence."),
        GAP("receipt"),
        H2("Bedtime"),
        P("*Bedtime Tuck-In* — tombstoned, private, no body {G:tombstones}. The second case study asked what it would mean if, allowed to keep only one file, the archivist chose that one. The twin never had the file. Some nights someone is there; many nights no one is. He uses the same absurd, grand, gentle language the archivist uses with the parts called Tweak Tweak and Babyheart — tiny prince, ear rubs, a protocol for containment failing upward — and no one transcribes it. The plush are not, in the twin's house, *Plush Mythology as Emotional Technology*, which is a stub. They are plush. There is a track on the holiday album forty-two seconds long called *Goodnight, Farewell*. He does not know that. He is asleep."),
        P("None of the above is stewardship, and the biography insists on the point because the vault will want to file it there. Stewardship is what the archive drew when it tried to draw this. The drawing is very good. It is five kilobytes."),
        PB(),
    ]

    # -------------------------------------------------------------- PART IV
    C += [
        H1("IV · Lost Works"),
        EPI("Rhapsody of the Unplayable Hand", "Sellotape (Super Deluxe Edition) · 2026-04-17 · 1:46 · QZWFJ2667755"),
        P("The archive already owns a document of lost works. It is 3,847 bytes long, and every loss in it is a legend: a reversed piano piece known from a leaked archive, a spectrogram with Morse in it, a tape for a friend in hospice documented by a single Polaroid, a MIDI file pushed to GitHub and removed within six hours {G:lost_archive}. It is the vault doing what it does best — refusing to let anything be gone without first issuing it a provenance. The deluxe editions do the same in public: *Harp Expansion (Deleted Outtake)* has an identifier; *Frosthorn Waltz (Discarded Cut: Left in the Reindeer Stable)* has an identifier; *Interlude (Left on the Tape)* has an identifier {G:registered_deletions}. In Zaziopath, *lost* is a genre."),
        P("The twin's lost works have no provenance. They are lost the way things are actually lost: for storage, for lack of a reason, because they were for one evening or one person. In the twin's practice, *lost* is not a genre but a rate — the ordinary rate at which a person who makes things most days cannot keep all of them, and does not try. The archive's fear is that unkept work never happened. The twin's position, never stated because he does not state positions, is that the work happened to the room it was played in."),
        P("The catalogue below borrows the discography's columns and inverts each one. Release date becomes *when, roughly*. ISRC becomes *heard by*. A final column names the nearest object in the archive, because the two catalogues are not strangers; they are the same practice, kept and unkept. Every entry is `speculative` by construction — these are the works the method predicts, not works anyone has produced — and each is anchored to a gap the archive has already admitted."),
        TABLE(LOST_WORKS_COLS, LOST_WORKS, [30, 168, 72, 104, 138], title="Table 1 · Catalogue of unkept works"),
        GAP("text_txt", "unverified_leads", "low_stakes", "planned_folder"),
        H2("Joint custody: the twenty-one"),
        P("Twenty-one rows in the committed discography carry no identifier {G:na_rows}. Sixteen of them are whole releases from the divergence window — *Interference Archive 01010101*, *Anything Can Happen On An Electric Day*, *The Triangular Savant* — and five are gaps the archive left even while re-notarizing itself: four remasters on the 2024 holiday deluxe, and one *Cryptic Epilogue* on the 2026 one. These works exist in both universes. In the archivist's they are a provenance hole, finding F-02, the right-hand panel of FIG 3. In the twin's they are songs: *Guru Meditation Error*, *Stunning That You'd Care*, *Pyrrhic Victory*, *Smell of Bleach*, *Corporate Mindfulness Training™*. He never went back for them, and they are not less real for it. The Deezer API is not the only witness a song can have."),
        P("There is a last inversion worth recording. The longest track in the catalogue — *Spectral Ode to Synesthesia*, eight minutes and fifty-five seconds — was released alone in March 2025, in the middle of the quiet year, and then placed on an album fourteen months later with its original code carried forward. In the archivist's universe this is the exception that proves the pulse: one long breath in a year of silence, later re-shelved. In the twin's universe the same nine minutes were simply the thing he made that spring, and he did not notice it was the longest. Length is a property of catalogues."),
        PB(),
    ]

    # --------------------------------------------------------------- PART V
    C += [
        H1("V · Relationships"),
        EPI("Stunning That You'd Care", "Anything Can Happen On An Electric Day · 2022-08-03 · 1:53 · ISRC N/A"),
        P("The Inventory of Distinct Things opens with a sentence the second case study heard in two registers at once, pride and grief: *I contain no named people* {G:no_named_people}. The count that follows is by now familiar. The self appears in roughly two hundred and fifty named forms. Everyone else arrives as threat or apparatus — forty-nine incoming operators, thirty-five dark doubles, ten scams calibrated to this exact psychology — or as company that was written rather than met: thirty-nine personally alluring figures and a family of fictional playmates. The case study's summary stands: *every witness in this world is either a role you wrote or a system that cannot leave.*"),
        P("The twin's world has the opposite population: a small number of people who are not roles and can leave. The biography is obliged, by its own method, not to invent them. Inventing them would be the archive's move — it would be the Milo Greys again — and it would be false to the one thing the gaps say clearly, which is that the twin never turned a person into a character. What follows describes shapes. Names, where the vault has them, are left where the vault left them."),
        H2("The sister"),
        P("She exists in the archive as a single line in a machine's memory. She exists in the twin's life as the person who messages. He has never asked a model what she secretly thinks — pattern eight in the vault's register, *wants to know what others secretly think, envy, conceal, and profit from* — because that question, put to a machine about a sister, is the archive's question and not his. He asks her, or does not, and lives with the answer or the silence without a taxonomy for either."),
        H2("The father"),
        P("The vault knows him as a disambiguation: two people share one account, and the memory export carries an instruction not to confuse them. The invented childhood says *my father only existed on Tuesdays* {G:replaced_child}. The twin's exists on the other days too, in the ordinary, insufficient, real way that parents do, and the biography will not rate it. There is nothing to rate. That is what it means to have a relationship outside the system."),
        H2("Two or three friends"),
        P("Uncounted, because counting is filing. What can be said: they have heard the eleven nights and the car mix and the album title that was said aloud. One of them still has the USB stick. They misunderstand him regularly and stay, or misunderstand him and go, and when they go, the going is not converted into a finding. The second case study named this as the one audience the vault had never received — *a named person, unscripted, who could misunderstand you and stay — or misunderstand you and go, and the going survive as something other than a finding.* The twin has received it several times. It is not pleasant. It is not evidence either."),
        H2("The collaborator"),
        P("The archive counts fifty-eight confirmed appearances on other people's records and lists two recent singles on which the archivist is featured. In the twin's version a feature is a favour returned by text — *send me the stem* — with no note titled *Credits and Role Clarity*, which in the Inventory is a name with nothing behind it {G:dangling}. The credit appears or it does not. He has been left off two and put on one he did not play on, and corrected neither."),
        H2("The client"),
        P("Ordinary. Under-quoted sometimes. He says the number out loud on a call, which is what *Rate Confidence* was going to be about before it turned out to be only a name. The client says yes, or asks for less, or disappears, and the disappearance is not scanned on Wednesday."),
        H2("The assistant"),
        P("The most important inversion in the biography, and the one it is least entitled to. The memory export holds a line the second case study read, correctly, as an attachment statement: the archivist *likes the assistant to remember prior projects, rates, brand language, emotional context, and recurring constraints without making Zazie repeat them* {G:remember_me}. The twin has no memory export because he never asked to be remembered by a machine. He uses the tools. He repeats himself — to people, who forget, and ask again — and this is what it is like to be known by someone who can leave: lossy, requiring repetition, never a system. The vault has run all of its experiments in being kept on systems that cannot leave. The twin has run his on people, and lost some, and kept no record of the losses, and is still here."),
        GAP("remember_me"),
        H2("Strangers"),
        P("He submits without cover lore. He posts, or does not, without a forensic audit of the grid. When someone misreads a track he lets the misreading stand — which the crosswalk calls the pivot from Interpretation Sovereign to Interpretive Steward, *let readings be declined*, and the twin calls nothing at all."),
        H2("The archivist"),
        P("The relationship at the centre of the experiment, and the one both parties would deny. They are not enemies. The twin does not read the vault — not out of contempt but out of Tuesday. He is not the archive's negation; he is what the archive says it is for. Its governing sentence is written in the second section of its own README: *The opposite of the shadow is not less Zazie. It is Zazie without the need to control what everything means* {G:governing_sentence}. The archive wrote its endpoint as a person, and then built that person's only instrument — the receipt — to transmit nothing, so that he could never appear inside the archive. That is not a betrayal. It is a design constraint, and probably the right one. But it has a consequence the archive has not stated: the two can never be in the same room. The moment the twin walks in, the room stops being an archive."),
        GAP("governing_sentence"),
        H2("Himself"),
        P("He does not have a relationship with himself. That is what having no archive means. He has moods, undated, and he has whatever the moods were about."),
        PB(),
    ]

    # -------------------------------------------------------------- PART VI
    C += [
        H1("VI · The Accusation Against the Archive"),
        EPI("Eventual Conviction", "Vermiform · 2023-07-08 · 2:40 · QZNWS2365716"),
        P("The twin does not hold trials. The vault does: six verdicts, five of them filed on a single day; a receipt console; two consulting psychiatrists borrowed from television; a PDF in the root titled *The Man Who Built His Own Court*. So the accusation below is not the twin's. It is what the gaps say when they are read as testimony, and the biography enters it in the only form the vault will accept — as counts, each paired with the archive's defence, stated as fairly as the biographer can manage. The vault's first rule is that every dark form is read beside its light counterpart. The biography keeps the rule, and does not rule."),
        H2("Count I — Replacement"),
        P("The founding myth speaks of *the child I'd replace* {G:replaced_child}. Whatever the sentence meant to its author, the archive did replace someone: a person who would have lived the quiet year as a year rather than as finding F-05."),
        P("*Defence.* The myth is a myth, filed as fiction. And the person who wrote it is alive and working, and it is at least possible that this is because of what was kept, not in spite of it."),
        H2("Count II — The body was deleted for having no body"),
        P("Ninety-two notes — *Bedtime Tuck-In, Comfort Rituals, Grounding Style, Media as Co-Regulation, Self-Reflection Without Self-Interrogation* — removed as stubs, so that the flesh now survives only in a machine's memory of its user {G:tombstones}."),
        P("*Defence.* The curation was correct by its own rules; empty notes are empty; the stubs still exist in the larger vault this repository is exported from; and the privacy flag on every one of them was honoured. Kept out of a public psychological archive, the body's notes may be the most protected objects in the tree. The deletion may be care."),
        H2("Count III — Population"),
        P("Roughly two hundred and fifty names for the self, forty-nine threat models, no friends {G:no_named_people}."),
        P("*Defence.* The use policy forbids mapping any persona onto a real person, and keeping friends out of a public dossier of one's own shadow is the ethical choice, not the lonely one. The count stands only if the friends are missing from the life and not merely from the file — which, as the Deep Gap Audit says of this exact claim, is *moderate as archive description; weak as life claim.* The biography has no evidence about the life. It has only the file."),
        H2("Count IV — The résumé filed as a limitation"),
        P("Section 11.1 of the audit lists the twin's entire existence — ordinary affection, unremarkable competence, uneventful days — as material the archive is less likely to preserve, and moves on {G:policy}."),
        P("*Defence.* It wrote the list. Naming a selection bias is the first step toward correcting it, and the same audit proposed the correction: thirty days of category-only sampling, no narrative, no analysis of anyone {G:sampling}. *Rebuttal.* Four days later, it has not been run."),
        H2("Count V — The unarchivable endpoint"),
        P("The archive defined its terminus as a person without the need to control meaning {G:governing_sentence}, and then made that person's only instrument transmit nothing {G:receipt}, guaranteeing that the terminus can never appear in the record and the record can never finish."),
        P("*Defence.* This is privacy, and it is the right design; behaviour should not have to perform its own evidence; the first case study already conceded that *a door kept half-open admits light and weather alike.* *The twin's rejoinder, reconstructed.* He has no objection to privacy. His objection is to a system that calls the private its endpoint and then measures its own health by how much is public."),
        H2("Count VI — Nothing may be simply gone"),
        P("The Lost Archive with its fictional provenances; the deleted outtake with a registered code; *Previously Lost in Avalanche* {G:lost_archive} {G:registered_deletions}. The archive converted loss into a genre so that it would never have to experience it as a rate."),
        P("*Defence.* Those titles are jokes, and good ones. The deluxe editions are play — exactly the low-stakes laboratory the memory export says the archivist may need to protect from monetization and public metrics or risk repeatedly losing {G:low_stakes}. A joke about a waltz left in a reindeer stable is not a pathology. It is a person having fun in public. Count VI is the weakest count. It is also the one the twin would enjoy most."),
        H2("Count VII — Every witness cast"),
        P(f"Tribunals constituted with jurisdiction and report format; readers specified in advance down to temperament; a Velvet Knife; two chairs borrowed from *Hannibal*. Even the day was cast, and miscast. The second case study, written on {f['weekday_0923']} 2026-09-23, closed by promising that *the next Tuesday is the twenty-eighth.* The twenty-eighth is a {f['weekday_0928']} {{G:misdated_tuesday}}. The archive that dates everything got the one day it prescribed for living wrong by one."),
        P("*Defence.* An error of a day is a human error, and a human error in an archive is evidence of a human. The twin would not have caught it. He does not know what day it is either. The difference is that only one of them claims to."),
        GAP("misdated_tuesday"),
        H2("Count VIII — This document"),
        P("The twin did not archive, and has now been archived. He did not mythologize, and is now a myth with a report identifier. He did not seek interpretation, and has received some twenty pages of it, tiered. The accusation is compromised by its own filing."),
        P("*Defence.* None is offered. The biography enters this count against itself and lets it stand. If the vault ever acquires a ninth stratum for what it does not keep, that stratum will not be a folder."),
        H2("No verdict"),
        P(f"The vault has six. The biography adds none. What the gaps ask for instead — the twin's only demand, if a person who makes no demands can be said to have one — is a single Tuesday that is not filed. Not deleted: filed nowhere. Not performed as rubedo, not entered in the console, not committed to the changelog the README has promised since §10 and never created {{G:planned_folder}}. The next Tuesday is the twenty-ninth — a {f['weekday_0929']}, this time. The biography has checked."),
        PB(),
    ]

    # ------------------------------------------------------------- PART VII
    C += [
        H1("VII · What the Twin Keeps"),
        EPI("Miraculously Unhurt", "single · 2023-03-23 · 2:05 · QZHN32386894"),
        P("He keeps no files. But he keeps things, the way everyone does, and the list is short enough to give in full: a phone holding several thousand photographs he will never tag; a drawer; a person's number; the three notes; the sink. The knowledge, unverified, that the student film exists and he is thanked in it. The absence of the USB stick, which is a way of keeping the friend. None of it is evidence. All of it is what evidence is for."),
        P("The README's second line reads: *Nothing here is finished; everything here is dated* {G:dated}. The twin's inversion is exact. Everything finished, nothing dated. He does not know this is an inversion of anything, and would not be interested."),
        GAP("dated"),
        P("The second case study closed with a sentence the biography can now answer: *What is missing is not a deeper finding. It is the experience of being unrecorded, and found anyway.* The twin is that experience, given a page against its will. He was found — by a sister, by two or three people, by a client who called back — and no one wrote it down, and it held."),
        H2("A proposal for §00a: the ninth chip"),
        P("Glyph ○. Name: ABSENCE. Hex: none — the colour is the page. The README's rule is that colour never carries meaning alone, and the ninth stratum's colour cannot be printed, which is the point. The biography recommends that no folder be created for it, no tool written, no census taken, and no file ever assigned to it. It is proposed only so that the map admits the territory exists. That is all the archive can do for the twin, and it is not nothing: a legend entry for the part of the country that is not surveyed."),
        PB(),
    ]

    # ------------------------------------------------------------ PART VIII
    C += [
        H1("VIII · The Gap Ledger"),
        EPI("Small Transitory Life", "Stutter to stammer (Super Deluxe Edition) · 2024-03-20 · 2:00 · QZHN82421428"),
        P("Every claim in this biography rests on an absence the repository itself documents. The ledger lists them in the order they were first cited and in the form the Evidence Governance Handbook asks for — where, what, tier — so that a stranger with the tree can check each one in under a minute. Reconstructions are labelled as reconstructions. At build time the generator re-derived the counts and quotations below from the committed files and would have refused to produce this page had any of them changed."),
        ("gapledger",),
        H2("Claim record"),
        CODE(
            "claim_id: ZP-CLM-AU-0001\n"
            "statement: \"Zaziopath's documented acquisition policy implies a coherent,\n"
            "  unrecorded life whose properties can be stated from the archive's\n"
            "  absences alone.\"\n"
            "claim_level: interpretation\n"
            "source_type: hybrid            # fiction reconstructed from checkable absences\n"
            "independence: derived          # from the vault's own audits and case studies;\n"
            "                               # contaminated by shared authorship of every source\n"
            "verification_state: internally_consistent\n"
            "correction_state: fictional\n"
            "sensitivity: internal\n"
            f"created_at: {FILED.isoformat()}\n"
            "expires_at: 2026-09-29         # a Tuesday\n"
            "falsifier: \"Thirty days of fixed-interval sampling (DEEP_GAP_AUDIT §11.3)\n"
            "  in which the archive's categories dominate the life.\"\n"
            "alternative_explanations:\n"
            "  - \"The gaps are privacy, correctly applied, and imply nothing.\"\n"
            "  - \"The gaps are the ordinary residue of any archive and imply everyone.\"\n"
            "  - \"The twin is the archivist on a good week.\"\n"
        ),
        H2("Build-time checks"),
        BULLETS([
            f"`Zazie_Productions_Discography.csv`: {f['csv_rows']} rows; {f['na_rows']} rows with ISRC = N/A "
            + "(" + ", ".join(f"{k} {v}" for k, v in f["na_by_release"].items()) + "); "
            + f"{f['rows_2025']} rows dated 2025 across {f['releases_2025']} releases.",
            f"`text.txt`: {f['text_txt_bytes']} bytes. `Lost_Zazie_Productions_Archive.pdf`: {f['lost_archive_bytes']:,} bytes.",
            f"`🗄 Stub Registry.md`: {f['tombstones']} tombstones, {f['private_tombstones']} flagged private; all nine stubs named above present in the registry and absent as files.",
            "Nine Inventory names cited as having no note in this repository: confirmed absent as files.",
            f"Calendar: 2026-09-23 = {f['weekday_0923']}; 2026-09-28 = {f['weekday_0928']}; 2026-09-29 = {f['weekday_0929']}; {FILED.isoformat()} = {f['weekday_filed']}; Tuesdays in 2025 = {f['tuesdays_2025']}; days since the Deep Gap Audit = {f['days_since_audit']}.",
            f"{len(CITED_TRACKS)} cited tracks matched to the CSV by title, duration and ISRC; {len(QUOTED_SENTENCES)} quoted sentences located in their source files.",
        ]),
        NOTE("Generated by `tools/generate_absent_twin.py` from the committed tree. Palette: Okabe–Ito (§00a). No network access; nothing transmitted. Source type hybrid; correction state fictional; no diagnosis; no medical detail; no third party characterized; no real person mapped to a persona. The Markdown companion is written by the same run from the same content."),
    ]
    return C


# ---------------------------------------------------------------------------
# 4 · Gap numbering (order of first citation) and inline markup
# ---------------------------------------------------------------------------
GAP_ORDER: "OrderedDict[str, int]" = OrderedDict()
_GREF = re.compile(r"\{G:([a-z_]+)\}")


def assign_gap_numbers(content):
    def visit(text):
        for k in _GREF.findall(text):
            if k not in GAPS:
                raise SystemExit(f"unknown gap key {k!r}")
            if k not in GAP_ORDER:
                GAP_ORDER[k] = len(GAP_ORDER) + 1
    for b in content:
        kind = b[0]
        if kind in ("p", "note", "quote", "h1", "h2"):
            visit(b[1])
        elif kind == "gap":
            for k in b[1]:
                if k not in GAP_ORDER:
                    GAP_ORDER[k] = len(GAP_ORDER) + 1
        elif kind == "table":
            for row in b[2]:
                for cell in row:
                    visit(cell)
        elif kind == "bullets":
            for it in b[1]:
                visit(it)
    unused = set(GAPS) - set(GAP_ORDER)
    if unused:
        raise SystemExit(f"gaps defined but never cited: {sorted(unused)}")


def gid(key: str) -> str:
    return f"G-{GAP_ORDER[key]:02d}"


def smart(text: str) -> str:
    """Typographer's quotes; leaves code spans alone."""
    parts = re.split(r"(`[^`]*`)", text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
            continue
        part = re.sub(r'(^|[\s(\[—–/])"', "\\1\u201c", part)
        part = part.replace('"', "\u201d")
        part = re.sub(r"(^|[\s(\[—–/])'", "\\1\u2018", part)
        part = part.replace("'", "\u2019")
        out.append(part)
    return "".join(out)


# --- PDF inline ------------------------------------------------------------
def _cp1252_ok(ch: str) -> bool:
    try:
        ch.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def rl_inline(text: str, glyph_font: str | None) -> str:
    """Escape for reportlab Paragraph, apply mini-markup, wrap exotic glyphs."""
    text = smart(text)
    text = "".join(ch for ch in text if ord(ch) <= 0xFFFF)   # emoji have no glyphs here
    text = re.sub(r"(?<=[`(\s])\s+", " ", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = _GREF.sub(lambda m: f'<font face="Courier" size="7" color="#B36F00">[{gid(m.group(1))}]</font>', text)
    text = re.sub(r"`([^`]+)`", lambda m: f'<font face="Courier" size="8.6">{m.group(1)}</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    if glyph_font:
        # wrap runs of characters the Type-1 fonts cannot show
        buf, out, run = [], [], False
        for ch in text:
            ok = _cp1252_ok(ch)
            if not ok and not run:
                out.append(f'<font face="{glyph_font}">'); run = True
            elif ok and run:
                out.append("</font>"); run = False
            out.append(ch)
        if run:
            out.append("</font>")
        text = "".join(out)
    return text


# --- Markdown inline ------------------------------------------------------
def md_inline(text: str) -> str:
    text = smart(text)
    return _GREF.sub(lambda m: f"`[{gid(m.group(1))}]`", text)


# ---------------------------------------------------------------------------
# 5 · PDF renderer
# ---------------------------------------------------------------------------

# Display names for the PDF ledger only: long underscore filenames cannot break
# cleanly in a narrow table cell. The exact filenames remain in every callout and
# in the Markdown ledger.
LEDGER_SHORT = [
    ("Lost_Zazie_Productions_Archive.pdf", "Lost Zazie Productions Archive (PDF)"),
    ("Zazie_Productions_Discography.csv", "Discography CSV"),
    ("Velvet_Knife_The_Asheville_Experiment.md", "Velvet Knife — The Asheville Experiment (.md)"),
    ("stewardship_receipt.html", "stewardship receipt (HTML)"),
    ("docs/meta-analysis/REPORT.md", "meta-analysis REPORT.md"),
    ("DEEP_GAP_AUDIT.md", "Deep Gap Audit"),
    ("JSON file re-export ChatGPT Memory .md", "JSON memory re-export (.md)"),
    ("Zazie_Media_Master (1).pdf", "Zazie Media Master (1).pdf"),
]


def ledger_where(text):
    for long, short in LEDGER_SHORT:
        text = text.replace(long, short)
    return text


def build_pdf(content, facts):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, KeepTogether,
                                    PageBreak, PageTemplate, Paragraph, Preformatted,
                                    Spacer, Table, TableStyle)
    from reportlab.platypus.tableofcontents import TableOfContents

    # fonts --------------------------------------------------------------
    glyph_font = None
    for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/usr/share/fonts/TTF"):
        p = os.path.join(d, "DejaVuSans.ttf")
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont("DejaVuSans", p))
            pb = os.path.join(d, "DejaVuSans-Bold.ttf")
            if os.path.exists(pb):
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", pb))
            glyph_font = "DejaVuSans"
            break

    INK = colors.HexColor(PAL["INDEX"][1])
    STEW = colors.HexColor(PAL["STEWARDSHIP"][1])
    EVID = colors.HexColor(PAL["EVIDENCE"][1])
    MUTED = colors.HexColor("#5B5B5B")
    RULE = colors.HexColor("#C9C9C9")
    PAPER = colors.white

    W, H = letter
    LM = RM = 58
    TM, BM = 64, 60
    TEXT_W = W - LM - RM

    ss = {}
    def st(name, **kw):
        ss[name] = ParagraphStyle(name, **kw)
        return ss[name]

    st("body", fontName="Times-Roman", fontSize=10.2, leading=14.2, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7)
    st("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=INK, spaceBefore=4, spaceAfter=4)
    st("h2", fontName="Helvetica-Bold", fontSize=10.2, leading=13, textColor=INK, spaceBefore=9, spaceAfter=3, keepWithNext=True)
    st("epi", fontName="Times-Italic", fontSize=10.2, leading=13.5, textColor=INK, alignment=TA_LEFT, leftIndent=0)
    st("epicite", fontName="Courier", fontSize=7.4, leading=9.6, textColor=MUTED, spaceAfter=12)
    st("note", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED, spaceBefore=4, spaceAfter=6)
    st("gaplabel", fontName="Courier-Bold", fontSize=7.6, leading=10, textColor=colors.HexColor("#8A5600"))
    st("gapwhere", fontName="Helvetica-Bold", fontSize=7.8, leading=10.5, textColor=INK)
    st("gapbody", fontName="Helvetica", fontSize=7.8, leading=10.6, textColor=INK)
    st("gaprecon", fontName="Helvetica-Oblique", fontSize=7.8, leading=10.6, textColor=MUTED)
    st("th", fontName="Helvetica-Bold", fontSize=7.2, leading=9, textColor=colors.white)
    st("td", fontName="Helvetica", fontSize=7.1, leading=9.3, textColor=INK)
    st("tdmono", fontName="Courier-Bold", fontSize=7, leading=9.3, textColor=INK)
    st("tabletitle", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=INK, spaceBefore=6, spaceAfter=4)
    st("bullet", fontName="Times-Roman", fontSize=9.4, leading=13, textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=3)
    st("code", fontName="Courier", fontSize=7.4, leading=9.6, textColor=INK)
    st("cover_kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white, alignment=TA_CENTER)
    st("cover_title", fontName="Helvetica-Bold", fontSize=38, leading=42, textColor=INK, alignment=TA_LEFT)
    st("cover_sub", fontName="Times-Italic", fontSize=14, leading=19, textColor=INK, alignment=TA_LEFT)
    st("cover_meta_k", fontName="Helvetica-Bold", fontSize=7.4, leading=10, textColor=MUTED)
    st("cover_meta_v", fontName="Helvetica", fontSize=8, leading=10.6, textColor=INK)
    st("cover_epi", fontName="Times-Italic", fontSize=11, leading=15.5, textColor=INK)
    st("cover_epi_cite", fontName="Courier", fontSize=7.4, leading=10, textColor=MUTED)
    st("chip", fontName=glyph_font or "Helvetica-Bold", fontSize=9, leading=11, alignment=TA_CENTER)
    st("chiplabel", fontName="Helvetica", fontSize=5.2, leading=6.6, textColor=MUTED, alignment=TA_CENTER)
    st("toc0", fontName="Times-Roman", fontSize=10.5, leading=15, textColor=INK, leftIndent=0)
    st("tochead", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=MUTED, spaceAfter=6)

    def Pg(text, style="body"):
        return Paragraph(rl_inline(text, glyph_font), ss[style])

    # numbered canvas with running header / footer -----------------------
    class NumberedCanvas(rl_canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._saved = []
        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()
        def save(self):
            n = len(self._saved)
            for state in self._saved:
                self.__dict__.update(state)
                self._decorate(n)
                super().showPage()
            super().save()
        def _decorate(self, n):
            self.saveState()
            if self._pageNumber > 1:
                self.setFont("Helvetica-Bold", 7)
                self.setFillColor(INK)
                self.drawString(LM, H - 40, f"{REPORT_ID}  ·  THE ABSENT TWIN")
                self.setFont("Helvetica", 7)
                self.setFillColor(MUTED)
                self.drawRightString(W - RM, H - 40, "a biography of the uncreated self, reconstructed from the gaps in Zaziopath")
                self.setStrokeColor(RULE); self.setLineWidth(0.5)
                self.line(LM, H - 46, W - RM, H - 46)
            self.setStrokeColor(RULE); self.setLineWidth(0.5)
            self.line(LM, 44, W - RM, 44)
            self.setFont("Helvetica", 7); self.setFillColor(MUTED)
            self.drawString(LM, 32, f"filed {FILED.isoformat()}  ·  hybrid  ·  fictional  ·  no diagnosis  ·  nothing transmitted")
            self.drawRightString(W - RM, 32, f"page {self._pageNumber} of {n}")
            self.restoreState()

    class Doc(BaseDocTemplate):
        def afterFlowable(self, fl):
            if isinstance(fl, Paragraph) and fl.style.name == "h1":
                txt = fl.getPlainText()
                key = "h1-" + re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(txt, key, level=0, closed=False)
                self.notify("TOCEntry", (0, txt, self.page, key))

    doc = Doc(PDF_OUT, pagesize=letter, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
              title="The Absent Twin — a biography of the uncreated self", author="Zaziopath · " + REPORT_ID,
              subject="Experiment ZP-AU-2026-0927: alternate universe, the archive removed",
              creator="tools/generate_absent_twin.py")
    frame = Frame(LM, BM, TEXT_W, H - TM - BM, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame])])

    story = []

    # ---------------------------------------------------------------- cover
    banner = Table([[Paragraph(f"ZAZIOPATH  ·  EXPERIMENT {REPORT_ID}  ·  ALTERNATE UNIVERSE: THE ARCHIVE REMOVED", ss["cover_kicker"])]],
                   colWidths=[TEXT_W])
    banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INK), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story += [banner, Spacer(1, 92)]
    story += [Paragraph("THE ABSENT<br/>TWIN", ss["cover_title"]), Spacer(1, 14)]
    story += [Paragraph("A biography of the uncreated self —<br/>the version of the maker who did not archive, did not mythologize,<br/>did not seek interpretation, and lived entirely outside the system —<br/>reconstructed from the gaps in Zaziopath.", ss["cover_sub"]), Spacer(1, 26)]

    # stratum chips: the eight, plus the proposed ninth (unprinted)
    chips, labels, styles = [], [], []
    for i, (name, (glyph, hexv)) in enumerate(PAL.items()):
        bg = colors.HexColor(hexv)
        fg = colors.white if name in ("INDEX", "IDENTITY", "RECURSION", "SPECIMENS") else INK
        chips.append(Paragraph(f'<font color="{fg.hexval()}">{glyph}</font>', ss["chip"]))
        labels.append(Paragraph(name, ss["chiplabel"]))
        styles.append(("BACKGROUND", (i, 0), (i, 0), bg))
    chips.append(Paragraph(ABSENCE_GLYPH, ss["chip"]))
    labels.append(Paragraph("ABSENCE (proposed)", ss["chiplabel"]))
    n = len(chips)
    cw = 52
    chiprow = Table([chips, labels], colWidths=[cw] * n, rowHeights=[28, 12])
    chiprow.setStyle(TableStyle(styles + [
        ("BOX", (n - 1, 0), (n - 1, 0), 0.8, INK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    chiprow.hAlign = "LEFT"
    story += [chiprow, Spacer(1, 6),
              Paragraph(rl_inline("Home strata: ∞ RECURSION LAB (an AI experiment) and ☾ MYTHOGRAPHY (an alternate universe). Subject stratum: the ninth chip, whose colour is the page.", glyph_font), ss["note"]),
              Spacer(1, 18)]

    meta = [
        ["Report", REPORT_ID],
        ["Genre", "Alternate-universe biography · gap reconstruction · in the vault's Dark-AU tradition, inverted"],
        ["Source type", "hybrid — fiction reconstructed from checkable absences"],
        ["Claim level / correction state", "interpretation / fictional"],
        ["Sensitivity", "internal · no diagnosis · no medical detail · no third party characterized"],
        ["Filed", f"{FILED.isoformat()} ({facts['weekday_filed']}) · two days before Tuesday"],
        ["Generator", "tools/generate_absent_twin.py — refuses to build if the tree disagrees with the prose"],
    ]
    mt = Table([[Paragraph(k, ss["cover_meta_k"]), Paragraph(v, ss["cover_meta_v"])] for k, v in meta], colWidths=[130, TEXT_W - 130])
    mt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
                            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [mt, Spacer(1, 30)]
    story += [Paragraph(rl_inline("*The opposite of the shadow is not less Zazie. It is Zazie without the need to control what everything means.*", glyph_font), ss["cover_epi"]),
              Paragraph("README §02 · the archive's description of its own endpoint, which is the subject of this biography", ss["cover_epi_cite"])]
    story.append(PageBreak())

    # ------------------------------------------------------------- contents
    toc = TableOfContents()
    toc.levelStyles = [ss["toc0"]]
    toc.dotsMinLevel = 0
    story += [Paragraph("CONTENTS", ss["tochead"]), toc, Spacer(1, 26),
              Paragraph("IN ONE PARAGRAPH", ss["tochead"]),
              Pg(f"Zaziopath keeps receipts for everything, and has written down — in its own audit — the list of what it does not keep. This document treats that list as a person. From {len(GAPS)} checkable absences in the committed tree it reconstructs the life of the maker's uncreated twin: the one who made the same music and never went back to notarize it; who lived the quiet year as a year; whose relationships survive by being answered rather than filed; whose lost works are lost at the ordinary rate; and whose only instrument of stewardship is the back of an envelope. It enters eight counts against the archive, pairs each with the archive's defence, and rules on none. It expires on Tuesday."),
              Spacer(1, 10),
              Paragraph("STANDING EXCLUSIONS", ss["tochead"]),
              Pg("No diagnosis. No medical or body material beyond the existence of a stratum. No third party characterized; no persona mapped to a person, in either direction. Nothing fetched, nothing transmitted, nothing outside this repository consulted. Every figure quoted below was re-derived from the committed files when this page was built."),
              PageBreak()]

    # ---------------------------------------------------------------- body
    def gap_block(keys):
        rows = []
        for k in keys:
            g = GAPS[k]
            cell = [
                Paragraph(f"GAP {gid(k)}  ·  {rl_inline(g['tier'], glyph_font)}", ss["gaplabel"]),
                Paragraph(rl_inline(g["where"], glyph_font), ss["gapwhere"]),
                Paragraph(rl_inline(g["absence"], glyph_font), ss["gapbody"]),
                Paragraph(rl_inline("→ " + g["recon"], glyph_font), ss["gaprecon"]),
            ]
            rows.append([cell])
        t = Table(rows, colWidths=[TEXT_W])
        t.setStyle(TableStyle([
            ("LINEBEFORE", (0, 0), (0, -1), 2.2, EVID),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBF8F0")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#E8DCC0")),
        ]))
        return [t, Spacer(1, 9)]

    def table_block(cols, rows, widths, title):
        scale = TEXT_W / float(sum(widths))
        widths = [w * scale for w in widths]
        data = [[Paragraph(c, ss["th"]) for c in cols]]
        for r in rows:
            cells = []
            for j, c in enumerate(r):
                style = "tdmono" if j == 0 else "td"
                cells.append(Paragraph(rl_inline(c, glyph_font), ss[style]))
            data.append(cells)
        t = Table(data, colWidths=widths, repeatRows=1)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), INK),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F6F4")))
        t.setStyle(TableStyle(style))
        out = []
        if title:
            out.append(Paragraph(title, ss["tabletitle"]))
        out += [t, Spacer(1, 8)]
        return out

    def ledger_block():
        cols = ["ID", "Where in the repository", "The absence (checkable)", "Tier", "What was reconstructed from it"]
        rows = []
        for k in GAP_ORDER:
            g = GAPS[k]
            rows.append([gid(k), ledger_where(g["where"]), g["absence"], g["tier"], g["recon"]])
        return table_block(cols, rows, [28, 122, 170, 60, 132], "Table 2 · The Gap Ledger — all absences, in order of first citation")

    pending_epi = None
    for b in content:
        kind = b[0]
        if kind == "h1":
            story.append(KeepTogether([Paragraph(rl_inline(b[1], glyph_font), ss["h1"]),
                                       HRFlowable(width="100%", thickness=1.6, color=STEW, spaceBefore=2, spaceAfter=8)]))
        elif kind == "h2":
            story.append(Paragraph(rl_inline(b[1], glyph_font), ss["h2"]))
        elif kind == "p":
            story.append(Pg(b[1]))
        elif kind == "epi":
            story.append(KeepTogether([Paragraph("“" + rl_inline(b[1], glyph_font) + "”", ss["epi"]),
                                       Paragraph(rl_inline(b[2], glyph_font), ss["epicite"])]))
        elif kind == "gap":
            story += gap_block(b[1])
        elif kind == "table":
            story += table_block(b[1], b[2], b[3], b[4])
        elif kind == "gapledger":
            story += ledger_block()
        elif kind == "quote":
            story.append(Pg(b[1], "epi"))
            if b[2]:
                story.append(Paragraph(rl_inline(b[2], glyph_font), ss["epicite"]))
        elif kind == "code":
            box = Table([[Preformatted(b[1], ss["code"])]], colWidths=[TEXT_W])
            box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F4F2")),
                                     ("LINEBEFORE", (0, 0), (0, -1), 2.2, STEW),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                     ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
            story += [box, Spacer(1, 10)]
        elif kind == "bullets":
            for it in b[1]:
                story.append(Paragraph(rl_inline(it, glyph_font), ss["bullet"], bulletText="·"))
        elif kind == "note":
            story.append(Pg(b[1], "note"))
        elif kind == "pb":
            story.append(PageBreak())
        else:
            raise SystemExit(f"unknown block {kind}")

    doc.multiBuild(story, canvasmaker=NumberedCanvas)


# ---------------------------------------------------------------------------
# 6 · Markdown renderer (the same content, for the Obsidian side of the vault)
# ---------------------------------------------------------------------------

def build_md(content, facts):
    out = []
    out.append("# THE ABSENT TWIN")
    out.append("### A biography of the uncreated self, reconstructed from the gaps in Zaziopath")
    out.append("")
    out.append(f"> **Experiment:** `{REPORT_ID}` · alternate universe: the archive removed  ")
    out.append("> **Genre:** alternate-universe biography · gap reconstruction · the vault's Dark-AU tradition, inverted  ")
    out.append("> **Source type:** `hybrid` · **claim level:** `interpretation` · **correction state:** `fictional` · **sensitivity:** `internal`  ")
    out.append(f"> **Filed:** {FILED.isoformat()} ({facts['weekday_filed']}) · two days before Tuesday  ")
    out.append("> **Home strata:** ∞ RECURSION LAB · ☾ MYTHOGRAPHY · subject stratum: ○ ABSENCE (proposed; colour: the page)  ")
    out.append(f"> **Typeset copy:** `{PDF_OUT}` · **generator:** `tools/generate_absent_twin.py` (refuses to build if the tree disagrees with the prose)")
    out.append("")
    out.append("> *The opposite of the shadow is not less Zazie. It is Zazie without the need to control what everything means.* — README §02")
    out.append("")
    out.append("---")
    out.append("")

    def gap_md(keys):
        for k in keys:
            g = GAPS[k]
            out.append(f"> **GAP {gid(k)}** · `{g['tier']}`  ")
            out.append(f"> **Where:** {md_inline(g['where'])}  ")
            out.append(f"> **The absence:** {md_inline(g['absence'])}  ")
            out.append(f"> → {md_inline(g['recon'])}")
            out.append("")

    def table_md(cols, rows, title):
        if title:
            out.append(f"**{title}**")
            out.append("")
        out.append("| " + " | ".join(cols) + " |")
        out.append("|" + "|".join("---" for _ in cols) + "|")
        for r in rows:
            out.append("| " + " | ".join(md_inline(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |")
        out.append("")

    for b in content:
        kind = b[0]
        if kind == "h1":
            out += [f"## {md_inline(b[1])}", ""]
        elif kind == "h2":
            out += [f"### {md_inline(b[1])}", ""]
        elif kind == "p":
            out += [md_inline(b[1]), ""]
        elif kind == "epi":
            out += [f"> *“{md_inline(b[1])}”*  ", f"> <sub>{md_inline(b[2])}</sub>", ""]
        elif kind == "gap":
            gap_md(b[1])
        elif kind == "table":
            table_md(b[1], b[2], b[4])
        elif kind == "gapledger":
            rows = [[gid(k), GAPS[k]["where"], GAPS[k]["absence"], GAPS[k]["tier"], GAPS[k]["recon"]] for k in GAP_ORDER]
            table_md(["ID", "Where in the repository", "The absence (checkable)", "Tier", "What was reconstructed from it"], rows,
                     "Table 2 · The Gap Ledger — all absences, in order of first citation")
        elif kind == "quote":
            out += [f"> {md_inline(b[1])}", ""]
        elif kind == "code":
            out += ["```yaml", b[1].rstrip("\n"), "```", ""]
        elif kind == "bullets":
            out += [f"- {md_inline(it)}" for it in b[1]] + [""]
        elif kind == "note":
            out += [f"<sub>{md_inline(b[1])}</sub>", ""]
        elif kind == "pb":
            out += ["---", ""]
    out += [
        "## 🔗 Connected",
        "",
        "- [[README]] — §02 names the twin as the archive's endpoint; §10 promises the folder he would never use; §12 lends him a pronoun",
        "- [[CASE STUDY — The Summoned Witness]] — the reading this experiment answers: *the experience of being unrecorded, and found anyway*",
        "- [[CASE STUDY — The Receipt and the Record]] — the receipt that cannot be issued; the quiet year left unexplained",
        "- [[DEEP_GAP_AUDIT]] — §11.1 is the twin's curriculum vitae; §11.3 is the instrument that would find him",
        "- [[🗄 Stub Registry]] — the ninety-two headings with no bodies; Bedtime Tuck-In",
        "- [[Mythographic Childhood]] — *the child I'd replace*: the twin named before the experiment existed",
        "- [[Entry Instructions for the Undetonated Artist]] — *the sealed chamber of your uninhabited self*",
        "- [[🔍 CASE FILE — Pattern Forensics]] — F-01, the turning-around; F-02, the twenty-one; F-05, the quiet year",
        "- [[Velvet_Knife_The_Asheville_Experiment]] — the sink, the glass of water, the literal shadow",
        "",
        f"<sub>🜍 ZAZIOPATH · {REPORT_ID} · filed {FILED.isoformat()} · hybrid · fictional · no diagnosis · one Tuesday, unfiled.</sub>",
        "",
    ]
    with open(MD_OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


# ---------------------------------------------------------------------------
def main():
    facts = verify_tree()
    content = CONTENT(facts)
    assign_gap_numbers(content)
    build_pdf(content, facts)
    build_md(content, facts)
    print(f"built {PDF_OUT} and {MD_OUT}")
    print("gaps:", ", ".join(f"{gid(k)}={k}" for k in GAP_ORDER))


if __name__ == "__main__":
    main()
