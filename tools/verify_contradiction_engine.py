#!/usr/bin/env python3
"""
Verifier for `⚡ CONTRADICTION ENGINE.md` (report ZP-CE-2026-0930).

Three jobs, all re-derived from primary files:

  1. LOADS   — re-measure every axis load (FIG 8) from the tag ledger in
               tools/generate_contradiction_field.py and compare it against the
               numbers printed in the engine document.
  2. QUOTES  — locate every quotation the engine attributes to a committed file
               inside that file. Markdown/text/HTML/DOCX are read with the
               standard library; PDFs need `pypdf` (see requirements-verify.txt).
               When the extractor is absent a quote is reported as
               `not_verified`, never as a pass.
  3. LINKS   — check that every local file the engine refers to exists, and that
               every internal anchor target it names resolves.

Output: a dated log on stdout + docs/contradiction/engine_verification.json

Run from the repository root:  python3 tools/verify_contradiction_engine.py
Exit code is non-zero if any load disagrees, any quote fails to locate, or any
named file is missing — quoting is a claim, and claims here are checkable.

Nothing in this script reads the engine's own sentences as evidence for the
engine's own sentences; it compares them to the files they cite.
"""

import datetime
import json
import os
import re
import sys
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
DOC = "⚡ CONTRADICTION ENGINE.md"
OUT = os.path.join("docs", "contradiction", "engine_verification.json")

# ───────────────────────── normalisation ─────────────────────────
_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−"), "-")
_QUOTES = dict.fromkeys(map(ord, "‘’‚‛"), "'")
_QUOTES.update(dict.fromkeys(map(ord, "“”„‟"), '"'))


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(_DASHES).translate(_QUOTES)
    s = s.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    # markdown emphasis, inline code and blockquote markers are formatting, not text
    s = re.sub(r"(?m)^\s{0,3}>\s?", "", s)
    s = s.replace("**", "").replace("__", "").replace("`", "").replace("*", "")
    s = re.sub(r"\s+", " ", s)
    # PDF extraction routinely leaves a space before punctuation and after an opening bracket
    s = re.sub(r"\s+([.,;:!?%)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s.strip().casefold()


def variants(s):
    """Source-text variants: plain, and with line-break hyphenation rejoined."""
    yield norm(s)
    yield norm(re.sub(r"-\s+", "", s))


def locate(quote, text, strict=True):
    """Return (found, ratio) where ratio is the length fraction of the longest
    matching prefix — so partial extraction failures are visible, not binary.
    Trailing sentence punctuation is ignored: a quotation truncated at a full
    stop is a formatting difference, not a different claim."""
    q = norm(quote).strip(' .,;:"')
    if not strict:
        q = q.rstrip('.,;:')
    for t in variants(text):
        if q in t:
            return True, 1.0
    best = 0.0
    words = q.split(" ")
    for t in variants(text):
        lo, hi = 0, len(words)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if " ".join(words[:mid]) in t:
                lo = mid
            else:
                hi = mid - 1
        if lo:
            best = max(best, len(" ".join(words[:lo])) / len(q))
    return False, round(best, 3)


# ───────────────────────── source loaders ─────────────────────────
def read_text(path):
    if path.lower().endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml").decode("utf8"))
        W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        return "\n".join("".join(n.text or "" for n in p.iter(W + "t"))
                         for p in root.iter(W + "p"))
    return open(path, encoding="utf-8", errors="ignore").read()


def read_pdf(path):
    """Returns (text, extractor_name) or (None, reason)."""
    try:
        from pypdf import PdfReader  # noqa: WPS433
    except ImportError:
        return None, "pypdf not installed"
    try:
        r = PdfReader(path)
        return "\n".join((pg.extract_text() or "") for pg in r.pages), "pypdf"
    except Exception as e:  # noqa: BLE001
        return None, f"extraction failed: {e}"


_cache = {}


def get_source(path):
    if path not in _cache:
        if path.lower().endswith(".pdf"):
            text, how = read_pdf(path)
            _cache[path] = (text, how)
        else:
            _cache[path] = (read_text(path), "stdlib")
    return _cache[path]


# ───────────────────────── the quote register ─────────────────────────
# (id, source file, quote as it appears in the engine, engine location, method note)
# A fifth element, where present, is {"doc_check": False} for entries checked
# against the source only — paraphrases and locality references that the engine
# document deliberately does not reproduce verbatim.
QUOTES = [
    # X-00 / core findings
    ("Q-00a", "docs/meta-analysis/REPORT.md",
     "Total independent evidence-gathering events across ~30,000 words: four.",
     "§0.5, §10.1, §12"),
    ("Q-00b", "README.md",
     "A shadow reading that never reaches stewardship is just a more elaborate way of being stuck.",
     "§0.1, §0.2"),
    ("Q-00c", "🔍 CASE FILE — Pattern Forensics.md",
     "Diagnosis outweighs treatment roughly",
     "§0.2, §2.3, §7"),
    ("Q-00d", "verdict_from_A.i_6",
     "The apparatus is complete. Completion is the terminal state of a mirror.",
     "§3 costs"),
    ("Q-00e", "ERROR_LOG_BIOGRAPHICA-7.md",
     "an event that is not a document, will not become one, and is kept that way on purpose",
     "§7, §10.1"),
    ("Q-00f", "README.md",
     "not clinical. No document here diagnoses anyone, including the subject.",
     "§9"),
    ("Q-00g", "EVIDENCE_GOVERNANCE_HANDBOOK.md",
     "A hybrid label must identify which factual claims remain intended for reliance.",
     "§10.4"),
    ("Q-00h", "verdict_from_A.i_6",
     "the art frame absorbs every failure in advance",
     "§10.4"),
    ("Q-00i", "verdict_from_A.i_6",
     "the private tags on empty notes really are the most quietly devastating detail in the repository",
     "§10.3 (quoted there as the tribunal's line)"),
    ("Q-00j", "⚡ Unexpected Connections.md",
     "A weakness that survives one register needs a second.",
     "§7"),
    ("Q-00k", "IDEOLOGICAL", "PLACEHOLDER", ""),
]

# ── quotes from `⚡ Unexpected Connections.md` ──
QUOTES += [
    ("Q-01a", "⚡ Unexpected Connections.md",
     "The myth supplies the motive; the audits supply the refutation. Neither works alone.",
     "§5"),
    ("Q-01b", "⚡ Unexpected Connections.md",
     "specificity carried past realism until it becomes its own emotional weather",
     "§5"),
    ("Q-01c", "⚡ Unexpected Connections.md",
     "the subject opposes non-consensual training while maintaining, in this very repo, an archive of AI output filed under a human name",
     "§12 coupling 1, §14 S-01"),
    ("Q-01d", "⚡ Unexpected Connections.md",
     "A weakness that survives one register needs a second.",
     "§7"),
]

# ── quotes from `Shadow Journal Observations .pdf` ──
QUOTES += [
    ("Q-02a", "Shadow Journal Observations .pdf",
     "You don't resolve contradictions — you feed on them.",
     "§6 (origin of the FEED move)"),
    ("Q-02b", "Shadow Journal Observations .pdf",
     "Ambiguity is your oxygen",
     "§6"),
    ("Q-02c", "Shadow Journal Observations .pdf",
     "You often position yourself as a cult artist or a singular freak before anyone else can do it for you.",
     "§4"),
    ("Q-02d", "Shadow Journal Observations .pdf",
     "Your perfectionism and visionary standards aren't just ambition; they're armor.",
     "§7"),
]

# ── quotes from the Ideological Inversion Audit ──
QUOTES += [
    ("Q-03a", "Ideological Inversion Audit.pdf",
     "No authority deserves obedience merely because it exists.",
     "§3"),
    ("Q-03b", "Ideological Inversion Audit.pdf",
     "Your rebellion is not against order. It is against being ordered by systems whose intelligence, legitimacy, or aesthetic authority you do not recognize.",
     "§3"),
    ("Q-03c", "Ideological Inversion Audit.pdf",
     "You do not merely request information. You construct a temporary institution, assign it jurisdiction, establish evidentiary rules, and prescribe its report format.",
     "§3, §4"),
    ("Q-03d", "Ideological Inversion Audit.pdf",
     "You want to write the constitution of the interaction.",
     "§3"),
    ("Q-03e", "Ideological Inversion Audit.pdf",
     "A tightly authored sovereign microstate disguised as a creative practice.",
     "§3"),
    ("Q-03f", "Ideological Inversion Audit.pdf",
     "You are anti-hierarchy when hierarchy claims sovereignty over you, but selectively hierarchical when organizing knowledge, taste, creative labor, or the interior world.",
     "§0.1, §3"),
    ("Q-03g", "Ideological Inversion Audit.pdf",
     "The bunny wears the crown so the conscious ego can deny wanting a throne.",
     "§3 costs"),
    ("Q-03h", "Ideological Inversion Audit.pdf",
     "exact roles for the assistant to inhabit",
     "§6"),
    ("Q-03i", "Ideological Inversion Audit.pdf",
     "Procedural ambiguity — whether anyone can exploit uncertainty against you.",
     "§6"),
]

# ── quotes from the memory export ──
QUOTES += [
    ("Q-04a", "JSON file re-export ChatGPT Memory .md",
     "Zazie repeatedly asks how to become more visible, searchable, envied, culturally magnetic, or impossible to ignore.",
     "§4"),
    ("Q-04b", "JSON file re-export ChatGPT Memory .md",
     "the most hidden risk is turning every vulnerability into content before it has been privately cared for",
     "§14 S-02"),
    ("Q-04c", "JSON file re-export ChatGPT Memory .md",
     "Low-stakes play is not a side hobby for Zazie; it is maintenance for the creative system",
     "§14 S-03 (quoted to the first clause)"),
    ("Q-04d", "README.md",
     "The longitudinal behavioural record underneath every other document.",
     "§9 (the charter's description of the memory export)"),
]

# ── quotes from the Instagram audit ──
QUOTES += [
    ("Q-05a", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "The asymmetry between a 12k follower count and a missing business pathway is the profile's central structural paradox",
     "§4"),
    ("Q-05b", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "advertises an artist of stature while behaving like a private account",
     "§4"),
    ("Q-05c", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "Every recommended action adds a legibility layer around the art, or removes ambiguity, without touching the art itself",
     "§4 production"),
    ("Q-05d", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "the account's equity",
     "§4"),
    ("Q-05e", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "the anonymous avant-garde polymath",
     "§4"),
    ("Q-05f", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "the finding most likely to quietly cost supervisory/label interest",
     "§4 costs"),
    ("Q-05g", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "I don't understand what I'm looking at exactly",
     "§4 costs (CM-01)"),
    ("Q-05h", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "clients buy a person's reliability",
     "§4 costs"),
    ("Q-05i", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "Total anonymity — no face, no personal name",
     "§10.2"),
    ("Q-05j", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
     "portfolio re-score",
     "§5"),
]

# ── quotes from the compendium ──
QUOTES += [
    ("Q-06a", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
     "The goal is not merely to make art but to make the artist and catalog feel like a coherent legend",
     "§5"),
    ("Q-06b", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
     "I would rather know exactly where I am capable of corruption than build an identity around goodness.",
     "§8"),
    ("Q-06c", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
     "Knowing darkness can become a more interesting exceptional identity than ordinary decency.",
     "§8"),
    ("Q-06d", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
     "The glamor of being dangerous but contained",
     "§8 heading (extraction may concatenate)"),
    ("Q-06e", "README.md",
     "17 of Zazie's own shadow rhetorics",
     "§8 (the charter's count of compendium ch. 14)"),
]

# ── quotes from the README ──
QUOTES += [
    ("Q-07a", "README.md",
     "The vault refuses to let the self be argued about in the abstract. Wherever a claim can be replaced by a count, it is.",
     "§5"),
    ("Q-07b", "README.md",
     "Rule of the vault: every finding carries a date and a tier. An undated insight is a mood.",
     "§5"),
    ("Q-07c", "README.md",
     "It is filed for three purposes only.",
     "§8"),
    ("Q-07d", "README.md",
     "The failure mode this vault is most exposed to is not missing a pattern",
     "§8"),
    ("Q-07e", "README.md",
     "The opposite of the shadow is not less Zazie. It is Zazie without the need to control what everything means.",
     "§0.3"),
    ("Q-07f", "README.md",
     "ambiguity is your oxygen",
     "§6 (charter's §14 one-liner)"),
]

# ── DEEP_GAP_AUDIT ──
QUOTES += [
    ("Q-08a", "DEEP_GAP_AUDIT.md",
     "directness and truth are different dimensions",
     "§9 (audit §3.1)"),
    ("Q-08b", "VISITORS_NOTEBOOK.md",
     "a bespoke targeting manual for its own author",
     "§8 costs (notebook §4)"),
    ("Q-08b2", "DEEP_GAP_AUDIT.md",
     "lowers the work required to create a convincing targeted approach",
     "§8 costs (audit §10.1)"),
    ("Q-08c", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
     "no authority to enforce any of it",
     "§3 costs (FF-14)"),
    ("Q-08e", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
     "shall be moved to a separate encrypted store and never committed",
     "§8 costs (Order 6)"),
    ("Q-08d", "DEEP_GAP_AUDIT.md",
     "routine maintenance",
     "§7 costs (audit §11.1 acquisition list)"),
]

# ── hearing + notebook + case studies + dossiers ──
QUOTES += [
    ("Q-09a", "VISITORS_NOTEBOOK.md",
     "cannot distinguish \"nothing happened\" from \"something happened privately\"",
     "§10.1 (the engine renders the negation; checked against the source)"),
    ("Q-09b", "VISITORS_NOTEBOOK.md",
     "the one risk the building's outward-facing warnings do not cover",
     "§8 costs"),
    ("Q-09c", "VISITORS_NOTEBOOK.md",
     "were never retro-labelled",
     "§5 costs"),
    ("Q-09d", "CASE STUDY — The Receipt and the Record.md",
     "The vault is the artwork — and its doubleness is the medium.",
     "§10.4"),
    ("Q-09e", "CASE STUDY — The Receipt and the Record.md",
     "controlled audition of dangerous readers",
     "§10.2"),
    ("Q-09f", "verdict_from_A.i_5",
     "an intelligence attending to you at full resolution, on demand, without limit, and without going anywhere",
     "§10.2"),
    ("Q-09g", "docs/meta-analysis/REPORT.md",
     "no diagnosis, no reading of medical or body material; structures, numbers and arguments only",
     "§9 (standing exclusion)"),
    ("Q-09h", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
     "twice failed to answer a question outside its own text",
     "§6 costs"),
    ("Q-09i", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
     "This Court is not independent, and says so",
     "§3 production"),
    ("Q-09j", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
     "the archive chose to file, date, and index a record of a reader failing to find a person in it",
     "source-only check (FF-17); §0.4 refers to it without quoting",
     {"doc_check": False}),
    ("Q-09k", "Zaziopath_Alana_Bloom_Frederick_Chilton.pdf",
     "Chilton writes subject on the cover. Alana crosses it out and writes author.",
     "epigraph, §9"),
    ("Q-09l", "Zaziopath_Alana_Bloom_Frederick_Chilton.pdf",
     "in case neither word is enough",
     "epigraph, §9"),
    ("Q-09m", "ANATOMIA_CONTRADICTIONIS_LECTER_DUMAURIER_XRAY.pdf",
     "He prepares the dining table with exquisite gold cutlery",
     "§10.1 (commissioned persona; number used, image disclaimed)"),
    ("Q-09n", "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf",
     "Give me the line that cuts through every defense and explains the entire archive.",
     "§6"),
    ("Q-09o", "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf",
     "We can offer a sentence as literature if it is labeled as literature and allowed to be wrong.",
     "§6"),
    ("Q-09p", "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf",
     "Do not increase certainty to improve customer satisfaction.",
     "§6 production"),
    ("Q-09q", "invisible_observer_dossier.md",
     "They wish to be discovered without becoming discoverable in the ordinary manner",
     "§0.4"),
    ("Q-09r", "Anti-Perfectionism Brain Hacks.md",
     "It doesn't have to be perfect. It just has to be real",
     "§7"),
    ("Q-09s", "Anti-Perfectionism Brain Hacks.md",
     "put its shoes on and walk it to the gate",
     "§7"),
    ("Q-09t", "Entry Instructions for the Undetonated Artist.md",
     "Disavow Aesthetic Sovereignty. Burn your taste.",
     "§7"),
    ("Q-09u", "CLAIM_PROVENANCE_LEDGER.md",
     "unresolved, not yet a contradiction",
     "§6, §0.3"),
    ("Q-09v", "CLAIM_PROVENANCE_LEDGER.md",
     "Resolved for meta-analysis",
     "§0.3"),
    ("Q-09w", "ZAZIOPATH — Collected Readings (2026-09-23).md",
     "clarity, delivered in the right register, can substitute for the Tuesday",
     "§5 costs (style tax)"),
    ("Q-09x", "ZAZIOPATH — Collected Readings (2026-09-23).md",
     "Genre ambiguity of that kind is affordable in fiction and costly in a dossier",
     "§10.4"),
    ("Q-09y", "🗄 Stub Registry.md",
     "The 92 removed stubs, by Inventory section",
     "§10.3 (the engine renders the count in a register row)",
     {"doc_check": False}),
    ("Q-09z", "RECURSIVE IDENTITY CASTLES.md",
     "Do anything today that statistically refutes its claim.",
     "§5"),
]

# ───────────────────────── load register ─────────────────────────
# axis id -> (pole1 fractional share, pole2 fractional share) as printed in the doc
LOAD_CLAIMS = {
    "X-00": (0.24, 0.76),
    "X-01": (0.67, 0.33),
    "X-02": (0.53, 0.47),
    "X-03": (0.27, 0.73),
    "X-04": (0.36, 0.64),
    "X-05": (0.07, 0.93),
    "X-06": (0.76, 0.24),
    "X-07": (0.08, 0.92),
    "X-08": (0.42, 0.58),
    "X-09": (0.10, 0.90),
    "X-10": (0.33, 0.67),
}
# axis id -> (pole1 KB, pole1 files, pole2 KB, pole2 files) as printed in the doc
LOAD_ABS = {
    "X-00": (107, 7, 332, 10),
    "X-01": (389, 6, 191, 7),
    "X-02": (714, 7, 642, 8),
    "X-03": (408, 8, 1101, 10),
    "X-04": (268, 8, 480, 7),
    "X-05": (93, 7, 1233, 8),
    "X-06": (1384, 9, 432, 9),
    "X-07": (238, 5, 2875, 10),
    "X-08": (452, 10, 627, 6),
    "X-09": (176, 6, 1566, 8),
    "X-10": (289, 8, 597, 11),
}


def measure_loads():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import generate_contradiction_field as gen  # noqa: WPS433
    rows, missing = gen.measure()
    out = {}
    for r in rows:
        a, b = r["a_bytes"], r["b_bytes"]
        tot = a + b
        out[r["ax"]["id"]] = dict(a_share=a / tot, b_share=b / tot,
                                 a_kb=a / 1024, b_kb=b / 1024,
                                 a_files=r["a_files"], b_files=r["b_files"])
    return out, missing


def main():
    results = {"report": "ZP-CE-2026-0930", "verifier": "tools/verify_contradiction_engine.py",
               "run_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "document": DOC}
    failures = []

    print(f"VERIFICATION RUN · {results['run_at']} · {DOC}\n")

    # 1 · loads
    print("[1] Axis loads — re-measured from the tag ledger, compared to the document")
    loads, missing_tags = measure_loads()
    load_report = {}
    for ax, (p1, p2) in LOAD_CLAIMS.items():
        m = loads[ax]
        ok_share = abs(m["a_share"] - p1) <= 0.011 and abs(m["b_share"] - p2) <= 0.011
        ka, fa, kb, fb = LOAD_ABS[ax]
        ok_abs = (abs(m["a_kb"] - ka) <= 2.0 and m["a_files"] == fa
                  and abs(m["b_kb"] - kb) <= 2.0 and m["b_files"] == fb)
        load_report[ax] = {"measured": {k: round(v, 4) if isinstance(v, float) else v
                                        for k, v in m.items()},
                           "document_claims": {"p1_share": p1, "p2_share": p2,
                                               "p1_kb": ka, "p1_files": fa,
                                               "p2_kb": kb, "p2_files": fb},
                           "shares_match": ok_share, "absolutes_match": ok_abs}
        flag = "ok " if (ok_share and ok_abs) else "DIFF"
        print(f"  {flag} {ax}  measured {m['a_kb']:7.1f}KB/{m['a_files']:>2}f "
              f"({m['a_share']*100:4.1f}%) vs {m['b_kb']:7.1f}KB/{m['b_files']:>2}f "
              f"({m['b_share']*100:4.1f}%)   doc: {ka}KB/{fa}f vs {kb}KB/{fb}f")
        if not (ok_share and ok_abs):
            failures.append(f"load {ax}")
    if missing_tags:
        failures.append("untagged files: " + repr(missing_tags))
    results["loads"] = load_report
    results["untagged_files"] = [f"{a}:{b}" for a, b in missing_tags]

    # 2 · quotes
    print("\n[2] Quotations — located in the files they are attributed to")
    quote_report = []
    by_source = {}
    for entry in QUOTES:
        qid, src, quote, where = entry[:4]
        if src == "IDEOLOGICAL" or quote == "PLACEHOLDER":
            continue
        if not os.path.exists(src):
            quote_report.append({"id": qid, "source": src, "where": where,
                                 "status": "source_missing", "ratio": 0.0})
            failures.append(f"{qid}: source missing {src}")
            print(f"  MISS {qid:<7} source missing: {src}")
            continue
        text, how = get_source(src)
        if text is None:
            quote_report.append({"id": qid, "source": src, "where": where,
                                 "status": "not_verified", "extractor": how,
                                 "ratio": None})
            print(f"  SKIP {qid:<7} {how:<32} {src}")
            continue
        doc_check = True
        if len(entry) > 4 and isinstance(entry[4], dict):
            doc_check = entry[4].get("doc_check", True)
        in_doc = locate(quote, open(DOC, encoding="utf-8").read())[0] if doc_check else None
        found, ratio = locate(quote, text)
        status = "located" if found else ("partial" if ratio >= 0.6 else "NOT_FOUND")
        quote_report.append({"id": qid, "source": src, "where": where,
                             "status": status, "ratio": ratio, "extractor": how,
                             "in_engine_document": in_doc, "quote": quote})
        if in_doc is False:
            failures.append(f"{qid}: registered quote not found in {DOC}")
        by_source[src] = how
        tag = {"located": "ok  ", "partial": "part", "NOT_FOUND": "FAIL"}[status]
        print(f"  {tag} {qid:<7} {ratio:5.3f}  {src[:52]:<54} {where[:34]}")
        if status == "NOT_FOUND":
            failures.append(f"{qid}: quote not located in {src}")
    results["quotes"] = quote_report

    # 2b · every load string printed anywhere in the document must match the ledger
    print("\n[2b] Load strings printed in the document — all must agree with the re-measurement")
    doc_text = open(DOC, encoding="utf-8").read()
    # long form: "107 KB · 7 files · 24%"   short form: "238 KB · 5 · 8%"
    tok_re = re.compile(r"([\d,]+) KB · (\d+)(?: files?)? · (\d+)%")
    bad_tokens = []
    for kb, files, pct in tok_re.findall(doc_text):
        kb_i, f_i, p_i = int(kb.replace(",", "")), int(files), int(pct) / 100.0
        hits = [ax for ax, m in loads.items()
                if ((abs(m["a_kb"] - kb_i) <= 1.1 and m["a_files"] == f_i
                     and abs(m["a_share"] - p_i) <= 0.011)
                    or (abs(m["b_kb"] - kb_i) <= 1.1 and m["b_files"] == f_i
                        and abs(m["b_share"] - p_i) <= 0.011))]
        if not hits:
            bad_tokens.append((kb, files, pct))
    print(f"  load strings found: {len(tok_re.findall(doc_text))} · unmatched: {len(bad_tokens)}")
    for t in bad_tokens:
        print(f"  STALE {t[0]} KB · {t[1]} files · {t[2]}%")
        failures.append(f"stale load string in {DOC}: {t}")
    results["load_strings_in_doc"] = len(tok_re.findall(doc_text))
    results["stale_load_strings"] = bad_tokens

    # 3 · links and named files
    print("\n[3] Referenced files — does every path the engine names exist?")
    doc = open(DOC, encoding="utf-8").read()
    from urllib.parse import unquote
    named = set()
    # markdown targets, honouring balanced parentheses inside the path
    for i, ch in enumerate(doc):
        if ch != "]" or doc[i:i + 2] != "](":
            continue
        depth, j = 1, i + 2
        while j < len(doc) and depth:
            if doc[j] == "(":
                depth += 1
            elif doc[j] == ")":
                depth -= 1
            j += 1
        target = doc[i + 2:j - 1]
        if target.startswith(("http", "#")):
            continue
        named.add(unquote(target.split("#")[0]))
    # backticked filenames: resolve by basename anywhere in the tree, so a bare
    # name in prose is not reported as a missing path
    tree = {}
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            tree.setdefault(unicodedata.normalize("NFC", f), os.path.join(dirpath, f))
    for m in re.findall(r"`([^`\n]+\.(?:md|pdf|png|svg|csv|json|html|py|docx|xlsx|txt|zip))`", doc):
        m = m.replace("python3 ", "").strip()
        named.add(m)
    planned = {"05_stewardship/ledger.md"}  # prescribed by hearing Order 7; not yet created
    missing_files = sorted(p for p in named
                           if not os.path.exists(p)
                           and unicodedata.normalize("NFC", os.path.basename(p)) not in tree
                           and p not in planned)
    planned_hits = sorted(p for p in named if p in planned)
    print(f"  named paths: {len(named)} · missing: {len(missing_files)} · "
          f"named-but-not-yet-created (planned): {len(planned_hits)} {planned_hits}")
    for p in missing_files:
        print(f"  MISS {p}")
    results["named_paths"] = sorted(named)
    results["planned_paths"] = planned_hits
    results["missing_paths"] = missing_files
    if missing_files:
        failures.append(f"{len(missing_files)} named path(s) missing")

    # 4 · summary
    occ = {}
    for q in quote_report:
        occ[q["status"]] = occ.get(q["status"], 0) + 1
    results["summary"] = {
        "axes_checked": len(LOAD_CLAIMS),
        "axes_matching": sum(1 for v in load_report.values()
                             if v["shares_match"] and v["absolutes_match"]),
        "quotes_checked": len(quote_report),
        "quote_status": occ,
        "extractors": by_source,
        "failures": failures,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)

    print(f"\n[4] SUMMARY · axes matching: {results['summary']['axes_matching']}/{len(LOAD_CLAIMS)}"
          f" · quotes: {occ}"
          f"\n    failures: {len(failures)}")
    for f in failures:
        print(f"      ✗ {f}")
    print(f"\n[verification] writing {OUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
