#!/usr/bin/env python3
"""Re-derive every checkable fact used in 🧨 COUNTER-ZAZIOPATH.md.

Run from anywhere:   python3 tools/verify_counter_zaziopath.py
Emits a log to stdout and writes docs/counter-zaziopath/verification.json.

Dependencies
------------
* Standard library only for: CSV, XLSX (read via zipfile/xml), HTML, Markdown and
  extension-less text checks, and the Deezer-snapshot comparison.
* `pypdf` (optional) for checks that read PDFs. Without it those checks are recorded
  as {"status": "skipped"} instead of guessed.   pip install pypdf

Design rules (inherited from README §11 and EVIDENCE_GOVERNANCE_HANDBOOK):
* every number carries its counting rule;
* absence claims name the place searched;
* nothing here reads a verdict's conclusion as evidence — only primary files.

The new files this run produces (the counter-document itself, this script, and
docs/counter-zaziopath/) are EXCLUDED from the vocabulary search, otherwise the search
for words like "Barnum" would find the document that reports their absence.
"""
import csv
import glob
import json
import os
import re
import statistics
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT_DIR = "docs/counter-zaziopath"
R = {}

try:
    from pypdf import PdfReader  # type: ignore
    HAVE_PDF = True
except Exception:  # pragma: no cover
    HAVE_PDF = False

EXCLUDE = {"🧨 COUNTER-ZAZIOPATH.md"}


def rec(key, value, note=""):
    R[key] = {"value": value, "note": note}
    shown = json.dumps(value, ensure_ascii=False)
    if len(shown) > 110:
        shown = shown[:107] + "..."
    print(f"  {key:<38} {shown}  {note}")


def skipped(key, why):
    R[key] = {"status": "skipped", "note": why}
    print(f"  {key:<38} SKIPPED — {why}")


_pdf_cache = {}


def pdf_text(path):
    if not HAVE_PDF:
        return None
    if path not in _pdf_cache:
        import logging
        logging.getLogger("pypdf").setLevel(logging.CRITICAL)
        r = PdfReader(path)
        pages = []
        for i, p in enumerate(r.pages, 1):
            pages.append((i, p.extract_text() or ""))
        _pdf_cache[path] = pages
    return _pdf_cache[path]


def flat(text):
    return re.sub(r"\s+", " ", text)


def dur(s):
    p = [int(x) for x in s.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


print(f"VERIFICATION RUN · {date.today().isoformat()} · cwd={ROOT} · pypdf={'yes' if HAVE_PDF else 'NO'}\n")

# ---------------------------------------------------------------- 1. CSV vs Case File
print("[1] Case File numbers re-derived from Zazie_Productions_Discography.csv")
rows = list(csv.DictReader(open("Zazie_Productions_Discography.csv", encoding="utf-8")))
for r in rows:
    r["sec"] = dur(r["Duration"])
    r["year"] = r["Release Date"][:4]
rec("csv_rows", len(rows))
late22 = [r for r in rows if r["year"] in ("2019", "2020") and r["ISRC"][5:7] == "22"]
rec("F01_2019_2020_rows_with_isrc_year_22", len(late22), "Case File F-01 says 13")
na = [r for r in rows if r["ISRC"] == "N/A"]
hole = Counter(r["Release Title"] for r in na)
rec("F02_na_rows", len(na), "Case File F-02 says 21")
rec("F02_na_by_release", dict(hole))
med = {}
for y in sorted({r["year"] for r in rows}):
    v = [r["sec"] for r in rows if r["year"] == y]
    m = statistics.median(v)
    med[y] = {"n": len(v), "median": f"{int(m // 60)}:{int(m % 60):02d}", "under_120s": sum(1 for x in v if x < 120)}
rec("F03_median_by_year", med, "Case File F-03")
rec("F03_shortest_longest", [min(r["sec"] for r in rows), max(r["sec"] for r in rows)], "seconds; 7 and 535 = 0:07 / 8:55")
per_rel = Counter(r["Release Title"] for r in rows)
rec("F04_deluxe_track_counts", {k: v for k, v in per_rel.items() if "Super Deluxe" in k})
y25 = [r for r in rows if r["year"] == "2025"]
rec("F05_2025_rows", len(y25))
rec("F05_2025_feature_rows", sum(1 for r in y25 if r["Artist"] != "Zazie Productions"), "rows whose Artist column is not Zazie Productions")

# ---------------------------------------------------------------- 2. XLSX
print("\n[2] The workbook's own legend and scope")


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    names = [s.get("name") for s in wb.find("m:sheets", ns)]
    out = {}
    for i, n in enumerate(names, 1):
        sh = ET.fromstring(z.read(f"xl/worksheets/sheet{i}.xml"))
        rows_ = []
        for r in sh.iter("{%s}row" % ns["m"]):
            cells = []
            for c in r.findall("m:c", ns):
                v = c.find("m:v", ns)
                if v is None:
                    isv = c.find("m:is", ns)
                    cells.append("".join(t.text or "" for t in isv.iter("{%s}t" % ns["m"])) if isv is not None else "")
                else:
                    cells.append(ss[int(v.text)] if c.get("t") == "s" else v.text)
            if any(x.strip() for x in cells):
                rows_.append(cells)
        out[n] = rows_
    return out


wbk = read_xlsx("Zazie_Productions_Complete_Discography.xlsx")
rec("xlsx_sheets", list(wbk.keys()))
legend = wbk["LEGEND"]
bc_only = [r[1] for r in legend if len(r) > 5 and "BC-only" in r[5]]
rec("xlsx_legend_bc_only_releases", bc_only, "LEGEND column ISRC PREFIX contains 'BC-only'")
cover_txt = " ".join(" ".join(r) for r in wbk["COVER"])
rec("xlsx_cover_states_bandcamp_only_not_on_deezer", "Bandcamp-only / netlabel, not distributed to Deezer" in cover_txt)
rec("xlsx_legend_defines_isrc_year_as_year_of_assignment", any("YY=year of assignment" in " ".join(r) for r in legend))
cat = [r for r in wbk["CATALOG"] if r and re.match(r"^\d+(\.0)?$", r[0] or "")]
rec("xlsx_catalog_rows", len(cat))
g7e = [r for r in cat if len(r) > 2 and r[2] == "G7e Torpedo"]
rec("xlsx_G7e_Torpedo_rows", len(g7e), "Bandcamp-only 2019 EP")
rec("csv_contains_G7e_Torpedo", any(r["Release Title"] == "G7e Torpedo" for r in rows))
comp25 = [r for r in wbk["COMPILATIONS"] if len(r) > 3 and r[3] in ("2025", "2025.0")]
feat25 = [r for r in wbk["FEATURES & COLLABS"] if len(r) > 4 and r[4] in ("2025", "2025.0")]
rec("xlsx_2025_compilation_rows", len(comp25), "COMPILATIONS sheet, YEAR column")
rec("xlsx_2025_feature_rows", len(feat25))
rec("xlsx_2025_catalog_rows", len([r for r in cat if len(r) > 4 and r[4] in ("2025", "2025.0")]), "CATALOG sheet rows with YEAR 2025 (singles + features + compilation appearances)")

cf = open("🔍 CASE FILE — Pattern Forensics.md", encoding="utf-8").read().lower()
rec("casefile_mentions_bandcamp_or_workbook", any(w in cf for w in ("bandcamp", "workbook", "xlsx", "netlabel")), "F-02 names 'a platform that issued no codes' but never identifies it")
rec("casefile_contains_both_readings_agree_sentence", "both readings agree" in cf)

# ---------------------------------------------------------------- 3. Deezer snapshot
print("\n[3] CSV vs a third-party listing (Deezer snapshot fetched 2026-09-30)")
snap = json.load(open(f"{OUT_DIR}/deezer_snapshot_2026-09-30.json", encoding="utf-8"))
dz_dates = {a["release_date"] for a in snap["albums"]}
csv_dates = {r["Release Date"] for r in rows}
rec("deezer_albums_listed", len(snap["albums"]))
rec("csv_release_dates", len(csv_dates))
rec("release_dates_in_both", sorted(dz_dates & csv_dates).__len__())
rec("csv_only_release_dates", sorted(csv_dates - dz_dates))
rec("deezer_only_release_dates", sorted(dz_dates - csv_dates))
hole_dates = sorted({r["Release Date"] for r in na if r["Release Title"] in ("Interference Archive 01010101", "Anything Can Happen On An Electric Day", "The Triangular Savant")})
rec("F02_hole_releases_absent_from_deezer_listing", all(d not in dz_dates for d in hole_dates), f"dates {hole_dates}")
spot = snap["isrc_spot_check"]
row = next(r for r in rows if r["ISRC"] == spot["isrc"])
rec("isrc_spot_check_title_match", row["Track Title"] == spot["deezer_title"])
rec("isrc_spot_check_duration_match", row["sec"] == spot["deezer_duration_seconds"])
rec("isrc_spot_check_deezer_resolves_to_2024_deluxe_only", spot["deezer_album_release_date"] == "2024-03-20",
    "the 2019 ISRC resolves to the 2024 deluxe; the 2019 original is not listed as its own Deezer album")

# ---------------------------------------------------------------- 4. CV vs CSV
print("\n[4] The artist CV against the catalogue scope")
CV = "Zazie_Kanwar-Torge_Artist_CV_2026_electroacoustic.pdf"
if HAVE_PDF:
    cvtxt = "\n".join(t for _, t in pdf_text(CV))
    lines = [l for l in cvtxt.splitlines() if re.match(r"^(2025)(–26)?\s", l)]
    rec("cv_entries_dated_2025", len(lines), "lines beginning '2025' or '2025–26' (wrapped lines not double-counted)")
    films = re.search(r"FILMOGRAPHY(.*?)ALBUMS AND EPS", cvtxt, re.S).group(1)
    rec("cv_2025_films", re.findall(r"^2025 (.+)$", films, re.M))
    rec("cv_lists_interference_archive_year", re.findall(r"(20\d\d) Interference Archive", cvtxt), "CSV says 2021-05-19")
    rec("cv_lists_to_halt_space_adrift_year", re.findall(r"(20\d\d) To Halt Space Adrift\n", cvtxt), "CSV/Deezer say 2023-04-28")
else:
    skipped("cv_entries_dated_2025", "pypdf not installed")

# ---------------------------------------------------------------- 5. Identity card
print("\n[5] Identity card — distribution of graded labels")
IC = "Identity _ Typological Vault.pdf"
if HAVE_PDF:
    t = flat("\n".join(x for _, x in pdf_text(IC)))
    pairs = re.findall(r"([A-Za-z\-&/\(\)' ]+?):\s+(Extremely High|Very High|Moderate-High|Moderate-Low|High|Moderate|Low|\d+%)", t)
    distinct = {}
    for k, v in pairs:
        distinct[k.strip().lstrip("•").strip()] = v   # dedupe: Perfectionism and Status Sensitivity appear twice on the card
    c = Counter(v for v in distinct.values() if not v.endswith("%"))
    n = sum(c.values())
    rec("identity_graded_labels", dict(c), f"n={n} distinct label-bearing attributes (+ 'Peter Pan Complex: 65%'); duplicates removed")
    rec("identity_share_very_or_extremely_high", round((c["Very High"] + c["Extremely High"]) / n, 3))
    rec("identity_share_high_or_above", round((c["High"] + c["Very High"] + c["Extremely High"]) / n, 3), "High + Very High + Extremely High")
    rec("identity_first_line", t[:50], "chat-prompt residue at the top of the committed card")
else:
    skipped("identity_graded_labels", "pypdf not installed")

# ---------------------------------------------------------------- 6. Compendium
print("\n[6] Compendium — where evidence grades and calibration notes live")
COMP = "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf"
if HAVE_PDF:
    pages = pdf_text(COMP)
    cur, cal, ev = None, Counter(), Counter()
    for n, txt in pages:
        m = re.search(r"CHAPTER\s*(\d+)\.", txt) or re.search(r"^PART\s*(\d+)", txt, re.M)
        if m:
            cur = int(m.group(1))
        cal[cur] += txt.count("Calibrationnote")
        ev[cur] += txt.count("Evidence:")
    rec("compendium_calibration_notes_by_chapter", {str(k): v for k, v in sorted(cal.items(), key=lambda kv: (kv[0] or 0)) if v}, "chapters 6-9 = incoming personas")
    rec("compendium_evidence_grades_by_chapter", {str(k): v for k, v in sorted(ev.items(), key=lambda kv: (kv[0] or 0)) if v})
    full = "\n".join(t for _, t in pages)
    rec("compendium_user_agreement_sentence", "based on the visible profile and the user’s agreement with it" in flat(full))
    rec("compendium_two_poles_sentence", "they are the two poles of one status-regulation system" in flat(full))
    names = {k: k in flat(full) for k in ["The Self-Awareness Prestige Trap", "The Anti-Ordinary Missionary", "The Evidentiary Stylist", "The Moral Aesthetician", "The Solitary Genius Emergency", "The Complexity Exemption", "The Beautifully Explained Recidivist", "The Witness Engineer"]}
    rec("compendium_pre_named_critique_archetypes_present", names)
else:
    skipped("compendium_calibration_notes_by_chapter", "pypdf not installed")

# ---------------------------------------------------------------- 7. Instrument output not integrated
print("\n[7] An instrument result that no other document cites")


def corpus():
    c = {}
    paths = [p for p in glob.glob("*.md") + glob.glob("docs/**/*.md", recursive=True)]
    binary = {".pdf", ".png", ".zip", ".xlsx", ".docx", ".py", ".js"}
    paths += [p for p in glob.glob("*") if os.path.isfile(p) and os.path.splitext(p)[1] not in binary and not p.endswith((".md", ".html", ".txt", ".csv"))]  # extension-less + verdict_from_A.i*
    paths += glob.glob("*.html") + glob.glob("*.txt") + glob.glob("*.csv")
    for p in paths:
        if os.path.basename(p) in EXCLUDE or p.startswith(OUT_DIR):
            continue
        txt = open(p, encoding="utf-8", errors="ignore").read()
        if p == "README.md":  # drop the README row that advertises this counter-document, which uses the search terms
            txt = "\n".join(l for l in txt.splitlines() if "COUNTER-ZAZIOPATH" not in l)
        c[p] = txt
    for p in glob.glob("*.docx"):
        x = zipfile.ZipFile(p).read("word/document.xml").decode("utf8", "ignore")
        c[p] = re.sub(r"<[^>]+>", " ", x)
    if HAVE_PDF:
        for p in glob.glob("*.pdf"):
            try:
                c[p] = "\n".join(t for _, t in pdf_text(p))
            except Exception:
                pass
    return c


CORP = corpus()
rec("corpus_files_searched", len(CORP), "md, extension-less/verdict files, html, txt, csv, docx" + (", pdf" if HAVE_PDF else " (PDFs NOT searched: pypdf missing)"))
rec("corpus_words_searched", sum(len(v.split()) for v in CORP.values()))
SF = "6Foundations 2.pdf"
if HAVE_PDF:
    s = flat("\n".join(t for _, t in pdf_text(SF)))
    rec("6foundations_raw", re.findall(r"(Care|Fairness|Loyalty|Authority|Sanctity|Liberty): (\d+) / 30", s))
    rec("6foundations_estimated_ideology_mentions_objectivism", "Objectivism" in s)
    rec("6foundations_next_matches", re.search(r"Next Matches: (.*?) What does", s).group(1))
    others = [p for p, v in CORP.items() if p != SF and re.search(r"6Foundations|Objectivism|Right-Libertarian", v)]
    rec("files_other_than_the_result_that_mention_it", others, "searched corpus excluding the result file itself")
else:
    skipped("6foundations_raw", "pypdf not installed")

# ---------------------------------------------------------------- 8. Vocabulary
print("\n[8] Validity vocabulary — files in which each term occurs at least once")
TERMS = ["barnum", "forer", "test-retest", "retest", "inter-rater", "base rate", "base-rate", "preregist", "pre-regist", "holdout", "hold-out",
         "overfit", "reification", "reify", "forking paths", "multiple comparison", "demand characteristic", "personal validation",
         "confirmation bias", "sycophan", "falsif", "validity", "psychometric"]
vocab = {}
for t_ in TERMS:
    hits = [p for p, v in CORP.items() if t_ in v.lower()]
    vocab[t_] = len(hits)
rec("vocabulary_file_counts", vocab)
rec("typology_files", len([p for p, v in CORP.items() if re.search(r"\bMBTI\b|Enneagram|Socionics", v)]), "files mentioning MBTI, Enneagram or Socionics")
ctx = {}
for t_ in ("sycophan", "confirmation bias", "pre-regist", "psychometric"):
    ctx[t_] = [p for p, v in CORP.items() if t_ in v.lower()]
rec("vocabulary_hit_files_for_nonzero_validity_terms", ctx)

# ---------------------------------------------------------------- 9. Console and ledger
print("\n[9] Stewardship console and the pre-ruled ledger")
html = open("stewardship_receipt.html", encoding="utf-8").read()
cw = re.search(r"const crosswalks=\[(.*?)\];", html, re.S).group(1)
qs = re.search(r"const questions=\[(.*?)\];", html, re.S).group(1)
rec("console_crosswalk_options", cw.count("['"))
rec("console_question_items", len(re.findall(r"^\s*'", qs, re.M)))
esc = [w for w in ["false positive", "none of these", "no action", "retire", "disconfirm", "interpretation revised", "sought"] if w in html.lower()]
rec("console_escape_terms_found", esc, "searched stewardship_receipt.html for disconfirming options")
v4 = open("verdict_from_A.i_4", encoding="utf-8").read()
ledger = re.findall(r"^(2026-09-\d\d)  ·  (.*)$", v4, re.M)
rec("preruled_ledger_lines", len(ledger))
rec("preruled_ledger_lines_filled", sum(1 for _, x in ledger if x.strip("_ ")), "committed copy only; local receipts are invisible to Git by design")

# ---------------------------------------------------------------- 10. Public credential documents
print("\n[10] Does the self-analysis appear in the credentialing documents?")
cred = ["Zazie_Kanwar-Torge_Artist_CV_2026.pdf", "Zazie_Kanwar-Torge_Artist_CV_2026_electroacoustic.pdf", "Zazie_Media_Master (1).pdf",
        "ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf"]
if HAVE_PDF:
    counts = {}
    for p in cred:
        tx = "\n".join(t for _, t in pdf_text(p))
        counts[p] = len(re.findall(r"zaziopath|self-analysis|typolog|shadow work|\bvault\b", tx, re.I))
    rec("credential_docs_mentions_of_zaziopath_or_self_analysis", counts)
    sr = "\n".join(t for _, t in pdf_text("Shadow_Resume.pdf"))
    rec("shadow_resume_pages", len(pdf_text("Shadow_Resume.pdf")))
    rec("shadow_resume_unusually", len(re.findall(r"unusually", sr, re.I)))
    rec("shadow_resume_first_lines", flat(sr)[:140])
else:
    skipped("credential_docs_mentions_of_zaziopath_or_self_analysis", "pypdf not installed")

# ---------------------------------------------------------------- 11. Layers of analysis
print("\n[11] Volume: documents whose stated object is an earlier analysis")
ANALYSES_OF_ANALYSES = [
    "verdict_from_A.i_2", "verdict_from_A.i_3", "verdict_from_A.i_4", "verdict_from_A.i_5", "verdict_from_A.i_6",
    "META-ANALYSIS — The Verdict Corpus Audited.md", "META_ANALYSIS_OF_ZAZIOPATH.md", "docs/meta-analysis/REPORT.md",
    "DEEP_GAP_AUDIT.md", "CLAIM_PROVENANCE_LEDGER.md", "EVIDENCE_GOVERNANCE_HANDBOOK.md", "HOSTILE_BIOGRAPHER_DOSSIER.md",
    "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
]
w = {p: len(open(p, encoding="utf-8", errors="ignore").read().split()) for p in ANALYSES_OF_ANALYSES if os.path.exists(p)}
rec("analyses_of_analyses_documents", len(w), "hand-listed; V2..V6 each read V1..; the rest audit the verdict corpus or its audits")
rec("analyses_of_analyses_words", sum(w.values()))
readme = open("README.md", encoding="utf-8").read()
rec("readme_depth_cap_text_present", "Max 3 without a break" in readme)
rec("readme_adversarial_prompt_presupposes_hidden_content", "Ask it to find what\nyou are hiding." in readme)
rec("readme_constitutional_authorship_quote_present", "You construct a temporary institution" in readme)
stew = [p for p in ("stewardship_receipt.html", "Anti-Perfectionism Brain Hacks.md", "Entry Instructions for the Undetonated Artist.md") if os.path.exists(p)]
rec("stewardship_named_files_bytes", {p: os.path.getsize(p) for p in stew})

# ---------------------------------------------------------------- 12. Static observations
print("\n[12] Observed outside the tree (recorded, not re-derivable offline)")
rec("github_repo_observed_2026_09_30", {"visibility": "public", "created_at": "2026-08-27T04:48:12Z", "stars": 0, "forks": 0, "watchers": 0},
    "via `gh api repos/zazieproductions/Zaziopath` on 2026-09-30")

os.makedirs(OUT_DIR, exist_ok=True)
with open(f"{OUT_DIR}/verification.json", "w", encoding="utf-8") as f:
    json.dump({"run_date": date.today().isoformat(), "pypdf": HAVE_PDF, "results": R}, f, ensure_ascii=False, indent=2)
print(f"\nwrote {OUT_DIR}/verification.json ({len(R)} results)")
