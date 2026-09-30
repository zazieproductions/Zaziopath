#!/usr/bin/env python3
"""
⚛️ PARTICLE COLLIDER — cross-stratum experiment engine.

Collides artifacts from distant strata of the vault and asks one question of each pair:
does combining these two datasets reveal a relationship neither contains alone?

The instrument has three parts:
  1. a census of every committed artifact, each assigned to one of the eight strata
     (README §00a) and tagged with how many independent observations it actually carries;
  2. a seeded blind draw of distant, never-before-paired artifacts, triaged by a mechanical
     beam-feasibility rule, plus a set of declared targeted beams;
  3. thirteen beams with pre-registered hypotheses, permutation nulls, validity gates and
     negative controls. Most are expected to fail, and the failures are the measurement.

Run:  python3 tools/particle_collider.py            (needs pypdf for PDF text)
Out:  docs/collider/beam_log.json  ·  docs/figures/fig8_beamline.png

Standing rule of this instrument: never promote an aesthetic coincidence into evidence
without testing it. Every HOLD in the log is reproducible from primary files alone.
"""
import sys, tempfile
import os, re, csv, json, glob, zipfile, random, hashlib, datetime, collections, itertools, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "tools" else os.getcwd()
os.chdir(ROOT)
# text cache lives outside the repo (never committed)
CACHE = os.environ.get("ZAZIOPATH_COLLIDER_CACHE") or os.path.join(tempfile.gettempdir(), "zaziopath_collider_text")

# ─────────────────────────── strata (README §00a) ───────────────────────────
STRATA = {
    "INDEX":       dict(chip="⬛", glyph="◈", hex="#231F20", name="INDEX & META"),
    "IDENTITY":    dict(chip="🟦", glyph="◉", hex="#0072B2", name="IDENTITY"),
    "SHADOW":      dict(chip="🟪", glyph="◐", hex="#CC79A7", name="SHADOW"),
    "EVIDENCE":    dict(chip="🟧", glyph="▤", hex="#E69F00", name="SIGNAL / EVIDENCE"),
    "RECURSION":   dict(chip="🟩", glyph="∞", hex="#009E73", name="RECURSION LAB"),
    "STEWARDSHIP": dict(chip="🔷", glyph="△", hex="#56B4E9", name="STEWARDSHIP"),
    "SPECIMENS":   dict(chip="🟥", glyph="⚠", hex="#D55E00", name="SPECIMENS"),
    "MYTHOGRAPHY": dict(chip="🟨", glyph="☾", hex="#F0E442", name="MYTHOGRAPHY"),
}

# ─────────────── stratum assignment.  tier: 'vault' = README §00a/§03/§12 or the
# §00c wire register names the artifact's home; 'analyst' = assigned here by content.
import unicodedata
A = {}
DOUBLE_FILED = {"THE OMNIVISIONARY GROK OUTPUT .pdf":
    "README §03 files it under the recursive AI experiments; §00a/§03 prose files it as specimen. Kept SPECIMENS."}
def assign(stratum, tier, *files):
    for f in files:
        A[unicodedata.normalize("NFC", f)] = (stratum, tier)

assign("INDEX", "vault",
    "README.md", "create a link.md", "Zazie Productions - MEGA-UNIVERSE.md",
    "🕸 Major Knowledge Graph.md", "🗄 Stub Registry.md", "🧾 Inventory of Distinct Things.md",
    "docs/meta-analysis/REPORT.md", "docs/meta-analysis/DREAM_LOGIC_RISK_ASSESSMENT.md",
    "docs/meta-analysis/verification.json", "docs/hearing/exhibit_verification.json",
    "docs/figures/fig0_colour_legend.png", "docs/figures/fig00c_complex_map.png",
    "docs/figures/fig00c_complex_map.svg", "tools/generate_figures.py",
    "tools/generate_complex_map.py")
assign("INDEX", "analyst",
    "CLAIM_PROVENANCE_LEDGER.md", "EVIDENCE_GOVERNANCE_HANDBOOK.md", "DEEP_GAP_AUDIT.md",
    "META_ANALYSIS_OF_ZAZIOPATH.md", "META-ANALYSIS — The Verdict Corpus Audited.md",
    "META_ANALYST_OF_INTERPRETATIONS.md", "UNEXPLORED_RABBIT_HOLES.md",
    "ANTHROPOLOGICAL_FIELD_REPORT_ZP-01.md", "VISITORS_NOTEBOOK.md", "VISITORS_NOTEBOOK.pdf",
    "tools/verify_meta_analysis.py", "tools/verify_hearing_transcript.py",
    "tools/build_wrong_reader_case.py", "tools/biographica7.py", "tools/check_stewardship_receipt.js",
    "generate_pdf.py", "generate_visitors_notebook.py", "zazie_mindmap.html", ".gitignore",
    "docs/figures/fig1_catalog_pulse.png", "docs/figures/fig2_miniaturization.png",
    "docs/figures/fig3_isrc_forensics.png", "docs/figures/fig4_deluxe_inflation.png",
    "docs/figures/fig5_seasonality.png", "docs/figures/fig6_strata_census.png",
    "docs/figures/fig7_title_lexicon.png")

assign("IDENTITY", "vault",
    "Identity _ Typological Vault.pdf", "JSON file re-export ChatGPT Memory .md",
    "6Foundations 2.pdf", "Archetype Test.pdf", "Avoidant Personality Spectrum Test.pdf",
    "Borderline Spectrum Test 5.pdf", "Brainrot Spectrum Test.pdf", "Moral Outrage Test (MOT).pdf",
    "Philosopher Personality Test Presocratics Edition.pdf")
assign("IDENTITY", "analyst",
    "ChatGPT Personality Dump.md", "greyhat", "Shadow_Resume.pdf",
    "Zazie_Kanwar-Torge_Artist_CV_2026.pdf", "Zazie_Kanwar-Torge_Artist_CV_2026_electroacoustic.pdf")

assign("SHADOW", "vault",
    "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
    "Shadow Journal Observations .pdf", "Ideological Inversion Audit.pdf",
    "HOSTILE_BIOGRAPHER_DOSSIER.md", "HOSTILE_BIOGRAPHER_DOSSIER.pdf")
assign("SHADOW", "analyst",
    "NEGATIVE-SPACE_BIOGRAPHY.md", "The_Architecture_of_Being_Seen_Psychological_Portrait.pdf",
    "Zaziopath_XRay_Two_Voices.pdf", "Zaziopath_Alana_Bloom_Frederick_Chilton.pdf",
    "Zaziopath_The_Analyst_Becomes_Evidence.pdf", "Zaziopath_The_Uncreated_Twin.pdf",
    "ANATOMIA_CONTRADICTIONIS_LECTER_DUMAURIER_XRAY.pdf", "invisible_observer_dossier.md",
    "Velvet_Knife_Report.md", "Velvet_Knife_Recursive_Analysis.md", "Velvet_Knife_Behind_The_Screen.md",
    "Velvet_Knife_Terminal_Descent.md", "Velvet_Knife_The_Asheville_Experiment.md",
    "Velvet_Knife_The_Hidden_Desires.md", "Velvet_Knife_The_Synthetic_Mirror.md",
    "Velvet_Knife_Handoff_Index.md")

assign("EVIDENCE", "vault",
    "Zazie_Productions_Discography.csv", "Zazie_Productions_Complete_Discography.xlsx",
    "Zazie_Media_Master (1).pdf", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
    "🔍 CASE FILE — Pattern Forensics.md", "ALBUM STRUCTURE - 4×3 FRACTAL MODULES.md")
assign("EVIDENCE", "analyst",
    "ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf",
    "UNEXPLAINED AERIAL PHENOMENA REPORT.md", "text.txt")

assign("INDEX", "analyst", "⚡ Unexpected Connections.md")
assign("RECURSION", "vault",
    "GPT Model 7.7-t Surveillance Subroutine.pdf", "THE OMNIVISIONARY GROK OUTPUT .pdf",
    "verdict_from_A.i", "verdict_from_A.i_2", "verdict_from_A.i_3", "verdict_from_A.i_4",
    "verdict_from_A.i_5", "verdict_from_A.i_6", "meta-experiment")
assign("RECURSION", "analyst",
    "Counterference Engine.pdf", "The_Infinite_Meta_Spiral.pdf", "reversed_turing_test.md",
    "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf",
    "ERROR_LOG_BIOGRAPHICA-7.md", "TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
    "CASE STUDY — The Receipt and the Record.md", "CASE STUDY — The Summoned Witness.md",
    "CASE_REPORT_THE_UNFILED_RECEIPT.pdf", "ZAZIOPATH — Collected Readings (2026-09-23).md",
    "ZAZIOPATH — Collected Readings (2026-09-23).pdf", "docs/excavation/EXCAVATION_REPORT_ZP-6026.md")

assign("STEWARDSHIP", "vault",
    "Anti-Perfectionism Brain Hacks.md", "Entry Instructions for the Undetonated Artist.md",
    "stewardship_receipt.html")
assign("STEWARDSHIP", "analyst", "OmniCipher_Signal_Codex_v1.0.pdf")

assign("SPECIMENS", "vault",
    "Social Engineering Email Templates .md", "Blueprints for Quiet, Horrifying Wealth.md",
    "Cognitive Infiltration Blueprints.md", "THE OMNIVISIONARY GROK OUTPUT .pdf")
assign("SPECIMENS", "analyst",
    "nuqkL_xKGpmDeDg0PiD0ebgdBeV49y9OVkGSQB-Ka_U.pdf",
    "online-presence-pr-seo-scam-vocabulary.pdf", "The Black Book II.pdf",
    "Personal Branding as Class War Psy-Ops.md", "TattleCrime_The_Man_Who_Built_His_Own_Court.pdf")

assign("MYTHOGRAPHY", "vault",
    "MAXIMAL SYMBOLIC SPECIFICITY ENGINE (MSS-E).md", "RECURSIVE IDENTITY CASTLES.md",
    "Dr. Caligo Vespertine in the Negative Observatory.md",
    "Twelve-Lung Grammar of the Forgotten Species.md", "GIBBERETIC SEED SPIRAL — glocht.md",
    "Mythographic Childhood.md", "Sovereign Interface Protocol (The Matrix).md")
assign("MYTHOGRAPHY", "analyst",
    "Anémone Crottin-Foufflée Identity.md", "This_Is_My_Design_The_Zazie_Reconstruction.pdf", "Hypostasis in Amber (Palindromic-image cascade).md",
    "Lost_Zazie_Productions_Archive.pdf", "TEXTUAL_EXHUMATIONS_UNICODE.pdf",
    "THE SPALLED VESTIBULE, OR_ WHERE THE BYLAWS GO TO ROT by Zazie Productions.pdf",
    "The_God_in_the_Syntax_Machine_Zazie_Productions_Expanded.docx",
    "The_Sound_That_Swallowed_April.docx", "Whispers_from_Unit_G19_FinalSubmission.docx",
    "Discoveries - Genius _ Hybrid _TE.pdf", "INDEX ORGANICA.zip", "conspiracy-tier-list-full.png",
    "Comprehensive Guide_ Building and Using an Unfettered Creative Brainstormer Inspired by History’s Greatest Minds.md",
    "docs/excavation/plates/plate_i_colour_codex.png",
    "docs/excavation/plates/plate_ii_receipt_amulet.png",
    "docs/excavation/plates/plate_iii_cartographic_shard.png")

# ─────────────── veto register: artifact groups already analyzed together ───────────────
# Each group = one existing analysis that paired these artifacts. A drawn pair whose two
# members sit in the same group is VETOED ("already analyzed together").
VETO_GROUPS = {
 "⚡ I":  ["RECURSIVE IDENTITY CASTLES.md", "Zazie_Productions_Complete_Discography.xlsx", "Zazie_Media_Master (1).pdf"],
 "⚡ I-b": ["JSON file re-export ChatGPT Memory .md", "GPT Model 7.7-t Surveillance Subroutine.pdf"],
 "⚡ II-a": ["Anti-Perfectionism Brain Hacks.md", "Entry Instructions for the Undetonated Artist.md"],
 "⚡ II-b": ["meta-experiment", "README.md"],
 "⚡ II-c": ["Sovereign Interface Protocol (The Matrix).md", "Ideological Inversion Audit.pdf"],
 "⚡ II-d": ["MAXIMAL SYMBOLIC SPECIFICITY ENGINE (MSS-E).md", "Dr. Caligo Vespertine in the Negative Observatory.md",
            "Twelve-Lung Grammar of the Forgotten Species.md", "GIBBERETIC SEED SPIRAL — glocht.md"],
 "⚡ III-a": ["Hypostasis in Amber (Palindromic-image cascade).md", "RECURSIVE IDENTITY CASTLES.md"],
 "⚡ III-b": ["ALBUM STRUCTURE - 4×3 FRACTAL MODULES.md", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf"],
 "⚡ III-c": ["ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf", "Zazie_Productions_Discography.csv"],
 "⚡ IV": ["Blueprints for Quiet, Horrifying Wealth.md", "Social Engineering Email Templates .md",
          "Cognitive Infiltration Blueprints.md", "JSON file re-export ChatGPT Memory .md"],
 "⚡ V":  ["ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf", "JSON file re-export ChatGPT Memory .md"],
 "⚡ VI": ["Mythographic Childhood.md", "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf"],
 "⚡ VII": ["Personal Branding as Class War Psy-Ops.md", "README.md"],
 "⚡ VIII-a": ["create a link.md", "Zazie Productions - MEGA-UNIVERSE.md", "README.md",
              "🕸 Major Knowledge Graph.md", "🗄 Stub Registry.md"],
 "⚡ VIII-b": ["verdict_from_A.i", "verdict_from_A.i_2", "verdict_from_A.i_3", "verdict_from_A.i_4",
              "verdict_from_A.i_5", "verdict_from_A.i_6", "README.md"],
 "🔍 F-01/02/03/04/05/06/07/10": ["Zazie_Productions_Discography.csv", "tools/generate_figures.py",
              "JSON file re-export ChatGPT Memory .md", "Identity _ Typological Vault.pdf",
              "Anti-Perfectionism Brain Hacks.md", "TEXTUAL_EXHUMATIONS_UNICODE.pdf"],
 "🔍 F-04/10-b": ["RECURSIVE IDENTITY CASTLES.md", "Zazie_Productions_Discography.csv"],
 "🔍 F-08": ["Blueprints for Quiet, Horrifying Wealth.md", "Social Engineering Email Templates .md",
             "JSON file re-export ChatGPT Memory .md", "README.md"],
 "🔍 F-09": ["README.md", "🗄 Stub Registry.md", "tools/generate_figures.py"],
 "§00c w06/w07": ["ALBUM STRUCTURE - 4×3 FRACTAL MODULES.md", "Anti-Perfectionism Brain Hacks.md",
                  "stewardship_receipt.html"],
 "§00c w12/w14": ["Zazie_Productions_Discography.csv", "ZazieKanwarTorge_ArtZoydResidency_SignalRotAtlas_2026.pdf",
                  "RECURSIVE IDENTITY CASTLES.md"],
 "C1 receipt case": ["stewardship_receipt.html", "CASE STUDY — The Receipt and the Record.md", "README.md",
                     "EVIDENCE_GOVERNANCE_HANDBOOK.md", "CASE_REPORT_THE_UNFILED_RECEIPT.pdf"],
 "C2 hearing": ["TRANSCRIPT — In re Zaziopath, Petition for Legal Personhood.md",
                "docs/hearing/exhibit_verification.json", "tools/verify_hearing_transcript.py"],
 "C3 verdict meta-analysis": ["docs/meta-analysis/REPORT.md", "docs/meta-analysis/verification.json",
                "verdict_from_A.i", "verdict_from_A.i_2", "verdict_from_A.i_3", "verdict_from_A.i_4",
                "verdict_from_A.i_5", "verdict_from_A.i_6", "META-ANALYSIS — The Verdict Corpus Audited.md",
                "tools/verify_meta_analysis.py"],
 "C4 excavation": ["docs/excavation/EXCAVATION_REPORT_ZP-6026.md", "README.md",
                "docs/figures/fig0_colour_legend.png", "🔍 CASE FILE — Pattern Forensics.md"],
 "C5 velvet knife": ["Velvet_Knife_Report.md", "Velvet_Knife_Recursive_Analysis.md",
                "Velvet_Knife_Handoff_Index.md", "README.md"],
 "C6 biographica7": ["ERROR_LOG_BIOGRAPHICA-7.md", "tools/biographica7.py", "README.md"],
 "C7 provenance ledger": ["CLAIM_PROVENANCE_LEDGER.md", "README.md", "meta-experiment",
                "Zazie_Productions_Discography.csv", "stewardship_receipt.html",
                "JSON file re-export ChatGPT Memory .md", "🔍 CASE FILE — Pattern Forensics.md",
                "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf"],
 "C8 rabbit holes": ["UNEXPLORED_RABBIT_HOLES.md", "verdict_from_A.i_6", "README.md"],
 "C9 collected readings": ["ZAZIOPATH — Collected Readings (2026-09-23).md",
                "ZAZIOPATH — Collected Readings (2026-09-23).pdf"],
 "C10 visitors notebook": ["VISITORS_NOTEBOOK.md", "VISITORS_NOTEBOOK.pdf", "generate_visitors_notebook.py"],
 "C11 deep gap audit": ["DEEP_GAP_AUDIT.md", "README.md", "🗄 Stub Registry.md"],
 "C12 inventory": ["🧾 Inventory of Distinct Things.md", "🗄 Stub Registry.md", "🕸 Major Knowledge Graph.md"],
}

# ─────────────────────────── text loading ───────────────────────────
def pdf_text(p):
    from pypdf import PdfReader
    r = PdfReader(p)
    return "\n".join((pg.extract_text() or "") for pg in r.pages)

def docx_text(p):
    z = zipfile.ZipFile(p)
    x = z.read("word/document.xml").decode("utf8", errors="ignore")
    x = re.sub(r"</w:p>", "\n", x)
    return re.sub(r"<[^>]+>", "", x)

def xlsx_text(p):
    """Every string and number in the workbook, in sheet order (for text-level scans)."""
    z = zipfile.ZipFile(p)
    out = []
    if "xl/sharedStrings.xml" in z.namelist():
        out += re.findall(r"<t[^>]*>(.*?)</t>", z.read("xl/sharedStrings.xml").decode("utf8", "ignore"), re.S)
    for n in sorted(x for x in z.namelist() if x.startswith("xl/worksheets/sheet")):
        out += re.findall(r"<v>(.*?)</v>", z.read(n).decode("utf8", "ignore"), re.S)
    return "\n".join(html_unescape(o) for o in out)

TEXT_CACHE, WORDS_CACHE = {}, {}

def doc_words(rel):
    if rel not in WORDS_CACHE: WORDS_CACHE[rel] = content_words(load_text(rel))
    return WORDS_CACHE[rel]

def load_text(rel):
    """Full plain text of an artifact ('' for binary/image archives)."""
    if rel in TEXT_CACHE: return TEXT_CACHE[rel]
    cache = os.path.join(CACHE, rel.replace("/", "__") + ".txt")
    if os.path.exists(cache):
        t = open(cache, encoding="utf-8", errors="ignore").read()
        TEXT_CACHE[rel] = t
        return t
    ext = os.path.splitext(rel)[1].lower()
    try:
        if ext == ".pdf":   t = pdf_text(rel)
        elif ext == ".docx": t = docx_text(rel)
        elif ext == ".xlsx": t = xlsx_text(rel)
        elif ext in (".png", ".svg", ".zip"): t = ""
        else: t = open(rel, encoding="utf-8", errors="ignore").read()
    except Exception:
        t = ""
    os.makedirs(CACHE, exist_ok=True)
    open(cache, "w", encoding="utf-8").write(t)
    TEXT_CACHE[rel] = t
    return t

# ─────────────────────────── inventory ───────────────────────────
def all_files():
    out = []
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), "."))
    return sorted(out)

def observations(rel, text):
    """How many independent rows/records the artifact actually carries (1 = unreplicated)."""
    ext = os.path.splitext(rel)[1].lower()
    if rel == "Zazie_Productions_Discography.csv":
        return len(list(csv.DictReader(open(rel, encoding="utf-8-sig"))))
    if ext == ".xlsx":
        return 200  # CATALOG sheet rows 1..200 (parsed in beams)
    if rel == "Zazie_Media_Master (1).pdf":
        return 133
    if rel == "Zazie_Productions_Instagram_Forensic_Audit.pdf":
        return 29   # grid posts on the audited surface
    if rel == "🗄 Stub Registry.md":
        return len([l for l in text.splitlines() if l.startswith("- [[")])
    if rel == "🧾 Inventory of Distinct Things.md":
        return len(re.findall(r"^- \[\[", text, re.M))
    if rel == "Department_of_Interpretive_Support_Zaziopath_Ticket_History.pdf":
        return len(re.findall(r"SUPPORT TICKET \d{4}", text))
    if rel == "CLAIM_PROVENANCE_LEDGER.md":
        return len(re.findall(r"^## ZP-CLM-\d{4}", text, re.M))
    if rel == "docs/hearing/exhibit_verification.json":
        return len(json.load(open(rel)).get("exhibits", [])) or 1
    if ext == ".csv":
        return max(len(text.splitlines()) - 1, 1)
    return 1

def inventory():
    inv = []
    for rel in all_files():
        text = load_text(rel)
        ext = os.path.splitext(rel)[1].lower() or "none"
        st = A.get(unicodedata.normalize('NFC', rel))
        iso = sorted(set("-".join(m) for m in re.findall(r"\b((?:19|20)\d\d)-(\d\d)-(\d\d)\b", text)))
        inv.append(dict(
            path=rel, name=os.path.basename(rel), ext=ext,
            bytes=os.path.getsize(rel), chars=len(text),
            stratum=(st[0] if st else None), tier=(st[1] if st else "unfiled"),
            n_obs=observations(rel, text),
            n_dates=len(iso), dates=iso,
            n_nums=len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text)),
            n_pct=text.count("%"),
            n_table_rows=len(re.findall(r"^\|.*\|$", text, re.M)),
            binary=ext in (".png", ".svg", ".zip"),
            analyzed=any(rel in g for g in VETO_GROUPS.values()),
        ))
    return inv

def vetoed(a, b):
    hits = [k for k, g in VETO_GROUPS.items() if a in g and b in g]
    return hits

# ─────────────────────────── beam-line machinery ───────────────────────────
# Stratum graph: edges are the containment/wire relationships the vault itself documents
# in README §00b and the §00c indexed wire register (17 wires), reduced to stratum level.
STRATUM_EDGES = [
    ("IDENTITY","SHADOW"), ("SHADOW","STEWARDSHIP"), ("EVIDENCE","IDENTITY"),
    ("RECURSION","SHADOW"), ("SPECIMENS","IDENTITY"), ("MYTHOGRAPHY","RECURSION"),
    ("EVIDENCE","STEWARDSHIP"), ("EVIDENCE","MYTHOGRAPHY"), ("SPECIMENS","SHADOW"),
    ("SPECIMENS","MYTHOGRAPHY"), ("RECURSION","IDENTITY"), ("MYTHOGRAPHY","IDENTITY"),
]
INF = 99   # INDEX & META appears in no §00b/§00c edge: the map never wires the mapmaker.

def stratum_distance():
    adj = collections.defaultdict(set)
    for a, b in STRATUM_EDGES:
        adj[a].add(b); adj[b].add(a)
    D = {}
    for s in STRATA:
        dist = {s: 0}; frontier = [s]
        while frontier:
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if v not in dist:
                        dist[v] = dist[u] + 1; nxt.append(v)
            frontier = nxt
        for t in STRATA:
            D[(s, t)] = dist.get(t, INF)
    return D

DIST = stratum_distance()

# Artifacts that are instruments rather than specimens: excluded from the draw pool,
# kept in the census. (Generated figures, renderers, verifiers, editor cruft.)
NOT_POOL = lambda rel: (
    rel.startswith("tools/") or rel.startswith("docs/figures/") or
    rel in ("generate_pdf.py", "generate_visitors_notebook.py", ".gitignore") or
    os.path.splitext(rel)[1].lower() in (".png", ".svg", ".zip"))

def feasibility(a, b):
    """Mechanical triage. T/L/C are beam-capable classes: they put a population on one side
    and a classifier, a chronology or a second population on the other. S (both bodies carry
    >=20 numeric tokens) is review-required only: numbers without a common referent are not
    a dataset, and almost every S pair dies on F1."""
    cls = []
    if a["n_obs"] >= 20 and b["n_obs"] >= 20: cls.append("T")   # two populations, joinable in principle
    if (a["n_obs"] >= 20) != (b["n_obs"] >= 20):
        pop, other = (a, b) if a["n_obs"] >= 20 else (b, a)
        if other["chars"] >= 3000: cls.append("L")               # population x lexicon source
    if a["n_dates"] >= 8 and b["n_dates"] >= 8: cls.append("C")  # two chronologies
    if a["n_nums"] >= 20 and b["n_nums"] >= 20: cls.append("S")  # two numeric-claim bodies
    return cls

def draw(n_draws=24, seed=20260930, min_distance=2):
    inv = {i["path"]: i for i in inventory()}
    pool = [p for p, i in inv.items() if i["stratum"] and not NOT_POOL(p)]
    pairs, veto_log = [], collections.Counter()
    for a, b in itertools.combinations(sorted(pool), 2):
        ia, ib = inv[a], inv[b]
        if ia["stratum"] == ib["stratum"]:
            veto_log["same stratum"] += 1; continue
        if DIST[(ia["stratum"], ib["stratum"])] < min_distance:
            veto_log["too close (d<2)"] += 1; continue
        v = vetoed(a, b)
        if v:
            veto_log["already analyzed together"] += 1; continue
        pairs.append((a, b))
    rng = random.Random(seed)
    digest = hashlib.sha256("\n".join(f"{a}|{b}" for a, b in pairs).encode()).hexdigest()[:16]
    picks = rng.sample(pairs, n_draws)
    rows = []
    for k, (a, b) in enumerate(picks, 1):
        ia, ib = inv[a], inv[b]
        cls = [c for c in feasibility(ia, ib) if c != "S"]
        rows.append(dict(draw=k, a=a, b=b, s_only="S" in feasibility(ia, ib), stratum_a=ia["stratum"], stratum_b=ib["stratum"],
                         distance=DIST[(ia["stratum"], ib["stratum"])],
                         obs_a=ia["n_obs"], obs_b=ib["n_obs"],
                         dates_a=ia["n_dates"], dates_b=ib["n_dates"],
                         chars_a=ia["chars"], chars_b=ib["chars"],
                         beam_classes=cls, verdict="NO-BEAM" if not cls else "TRIAGED"))
    return dict(seed=seed, n_draws=n_draws, min_distance=min_distance, pool=len(pool),
                eligible_pairs=len(pairs), pair_list_sha16=digest, veto=dict(veto_log),
                draws=rows, run_date=datetime.date.today().isoformat())

# where each promoted draw ended up: a beam id, or the reason it never became one.
# recorded so the log carries every draw's fate, not just the survivors'.
DRAW_DISPOSITIONS = {
    4:  dict(beam="C-12"),
    6:  dict(beam=None, failure_class="F2 no shared referent",
             note="the Velvet Knife prose never mentions an exhibit, a hearing or a verification "
                  "(0 hits for each), so the exhibit-verification join key exists on one side only"),
    10: dict(beam=None, failure_class="F2 no shared referent",
             note="the Media Master and the exhibit verification share only a 4-row join; 133 census "
                  "observations against 106 exhibits with no stable key between them"),
    11: dict(beam="C-03"),
    19: dict(beam="C-02"),
}

# ─────────────────────────── statistics (stdlib only) ───────────────────────────
def perm_p(observed, null, two_sided=False, greater=True):
    null = list(null)
    if not null: return None
    if two_sided:
        return sum(1 for x in null if abs(x) >= abs(observed)) / len(null)
    if greater:
        return sum(1 for x in null if x >= observed) / len(null)
    return sum(1 for x in null if x <= observed) / len(null)

def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j+1]] == xs[order[i]]: j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j+1): r[order[k]] = avg
        i = j + 1
    return r

def spearman(a, b):
    if len(a) < 3: return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra)/len(ra), sum(rb)/len(rb)
    num = sum((x-ma)*(y-mb) for x, y in zip(ra, rb))
    den = (sum((x-ma)**2 for x in ra) * sum((y-mb)**2 for y in rb)) ** 0.5
    return None if den == 0 else num/den

def dispersion(counts):
    """Index of dispersion (variance/mean) over units with >=1 opportunity."""
    counts = [c for c in counts]
    if not counts: return None
    m = sum(counts)/len(counts)
    if m == 0: return None
    v = sum((c-m)**2 for c in counts)/(len(counts)-1) if len(counts) > 1 else 0.0
    return v/m

def cohen_kappa(pairs):
    """pairs: list of (rater1, rater2) categorical labels."""
    cats1 = sorted({a for a, _ in pairs}); cats2 = sorted({b for _, b in pairs})
    n = len(pairs)
    if n == 0: return None, None
    po = sum(1 for a, b in pairs if a == b)/n
    pe = 0.0
    for c in set(cats1) & set(cats2):
        pe += (sum(1 for a, _ in pairs if a == c)/n) * (sum(1 for _, b in pairs if b == c)/n)
    return (po, (po-pe)/(1-pe) if pe != 1 else None)

def gini(xs):
    xs = sorted(xs); n = len(xs)
    if n == 0 or sum(xs) == 0: return None
    return (2*sum((i+1)*x for i, x in enumerate(xs)) - (n+1)*sum(xs)) / (n*sum(xs))

def words(text):
    return re.findall(r"[A-Za-z][A-Za-z'’\-]+", text.lower())

STOP = set("""the a an and or of to in for on with by at from as is are was were be been being it its this that
these those there here not no nor so than then thus into over under out up down off again more most other some
such only own same too very can will just should now i you he she they we them his her their our your my me him
us if but because while during between about against through above below to from""".split())

def content_words(text):
    return [w for w in words(text) if w not in STOP and len(w) > 2]

# ─────────────────────────── dataset parsers ───────────────────────────
FURNITURE = {"P", "DATE", "PUBLICATION", "TITLE / HOW FEATURED", "EXACT NAME", "LINK",
             "#", "YEAR", "COMPILATION", "TRACK / CONTRIBUTION", "LABEL / PUBLISHER",
             "Zazie Productions / Zazie Kanwar-Torge"}

def _mm_sections():
    t = load_text("Zazie_Media_Master (1).pdf")
    names = ["Press & Editorial", "Film, Festivals & Exhibitions", "Publications & Recognition",
             "Profiles & Catalogs", "Music Compilations"]
    pos = {n: [m.start() for m in re.finditer(re.escape(n), t)][-1] for n in names}
    order = sorted(pos.items(), key=lambda kv: kv[1])
    out = {}
    for i, (n, st) in enumerate(order):
        end = order[i+1][1] if i+1 < len(order) else len(t)
        seg = t[st:end]
        j = seg.find("LINK")
        out[n] = seg[j+4:] if j >= 0 else seg
    return out

PUBS = ["Five Steps From The Fringe / Spotify for Creators", "Five Steps From The Fringe / Spotify",
        "Black Mountain College Museum + Arts Center", "Black Mountain College Radio / SoundCloud",
        "Canyon Cinema Foundation / Vimeo", "Experimental Cinema / Visualcontainer [.BOX]",
        "Lake Ivan Film Journal", "Limitless Magazine", "Grammy Weekly", "HEAVY Magazine", "Indie AM",
        "Shock Web Radio", "Pop Fantasma", "Casey Douglass", "Viral Nation", "PR ON THE GO", "PRFree",
        "Telegraph (telegra.ph)", "Apple Podcasts", "Superpresent Magazine", "Ranger Magazine",
        "BillboardWire", "Pebbles Underground", "Visualcontainer TV", "Latest TV Brighton",
        "New Media Artspace", "Cybernetic Futures", "The Film-Makers' Cooperative", "Apple Support",
        "Pulitzer Center", "Amazon Books", "Smashwords", "Enigma Labs", "IMDb", "LinkedIn", "Stage 32",
        "FilmFreeway", "MUSE", "SoundBetter", "WFCN", "Musicians.Directory", "BandMix",
        "Casting Call Club", "itch.io", "Hackaday.io", "ReelCrafter", "Songstats", "Viberate",
        "Groover", "Slaps", "Behance", "Equipboard", "Spotify", "Apple Music", "Deezer", "Bandcamp",
        "Discogs", "Muso.AI", "Gumroad", "Linktree", "ReverbNation", "Rate Your Music", "Amazon Music"]

def _norm(s): return re.sub(r"\s+", " ", s).strip()

def media_master():
    """Parse all 133 census records from the reading edition."""
    secs = _mm_sections()
    recs = []
    for sec in ["Press & Editorial", "Film, Festivals & Exhibitions", "Publications & Recognition",
                "Profiles & Catalogs"]:
        for blk in secs[sec].split("OPEN"):
            L = [l.strip() for l in blk.split("\n") if l.strip()]
            L = [l for l in L if l not in FURNITURE and not l.startswith("ZAZIE EXACT-NAME")
                 and not l.startswith("RESEARCHED THROUGH") and not re.match(r"^Page \d+$", l)]
            if len(L) < 3 or L[0] not in ("A", "B", "C"):
                continue
            pri, date = L[0], L[1]
            rest, pub, k = [], None, 2
            acc = ""
            while k < len(L):
                acc = _norm((acc + " " + L[k]).strip()) if acc else _norm(L[k])
                k += 1
                if acc in PUBS: pub = acc; break
                if not any(p.startswith(acc) for p in PUBS): break
            rest = L[k:]
            subj = ""
            for i2, l in enumerate(rest):
                if l.startswith("Subject:"):
                    subj = _norm(l[8:].strip())
                    for l2 in rest[i2+1:]:
                        if "Zazie" in l2: break
                        subj = _norm(subj + " " + l2)
                    break
            mid = _norm(" / ".join(rest[:rest.index(next(l for l in rest if l.startswith('Subject:')))])) \
                  if any(l.startswith("Subject:") for l in rest) else _norm(" / ".join(rest))
            recs.append(dict(section=sec, priority=pri, date=date, publication=pub or "?",
                             mid=mid, subject=subj))
    comp = []
    for blk in secs["Music Compilations"].split("OPEN"):
        L = [l.strip() for l in blk.split("\n") if l.strip()]
        L = [l for l in L if l not in FURNITURE and not l.startswith("ZAZIE EXACT-NAME")
             and not l.startswith("RESEARCHED THROUGH") and not re.match(r"^Page \d+$", l)
             and not l.startswith("Discogs currently displays") and not l.startswith("header summarizes")]
        if len(L) < 5 or not L[0].isdigit():
            continue
        comp.append(dict(section="Music Compilations", idx=int(L[0]), year=L[1],
                         compilation=_norm(" ".join(L[2:-2])), track=_norm(L[-2]), label=_norm(L[-1]),
                         priority="C", publication=_norm(L[-1]), subject=_norm(L[-2]),
                         date=L[1], mid="Compilation listing (Discogs appearance index)"))
    return recs, comp

def catalog_csv():
    rows = list(csv.DictReader(open("Zazie_Productions_Discography.csv", encoding="utf-8-sig")))
    for r in rows:
        m, s = (r["Duration"].split(":") + ["0"])[:2]
        r["secs"] = int(m) * 60 + int(s)
        r["gap"] = r["ISRC"].strip().upper() in ("", "N/A", "NA", "—", "-")
    rel = collections.OrderedDict()
    for r in rows:
        rel.setdefault((r["Release Date"], r["Release Title"], r["Release Type"]), []).append(r)
    return rows, rel

def xlsx_cell(c, shared):
    t = re.search(r't="(\w+)"', c); v = re.search(r"<v>(.*?)</v>", c, re.S)
    if not v:
        iss = re.search(r"<is>.*?<t[^>]*>(.*?)</t>", c, re.S)
        return html_unescape(iss.group(1)) if iss else ""
    val = v.group(1)
    return shared[int(val)] if (t and t.group(1) == "s") else val

def html_unescape(s):
    import html as _h; return _h.unescape(s)

def catalog_xlsx():
    """CATALOG sheet rows 1..200 + STATISTICS sheet."""
    z = zipfile.ZipFile("Zazie_Productions_Complete_Discography.xlsx")
    shared = [html_unescape(s) for s in
              re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf8"), re.S)]
    def sheet(n):
        x = z.read(n).decode("utf8")
        out = []
        for r in re.findall(r"<row[^>]*>(.*?)</row>", x, re.S):
            cells = re.findall(r"<c[^>]*?/>|<c[^>]*?>.*?</c>", r, re.S)
            out.append([xlsx_cell(c, shared).replace("<t>", "").replace("</t>", "") for c in cells])
        return out
    cat = sheet("xl/worksheets/sheet3.xml")
    tracks = []
    for row in cat:
        if not row or not row[0]: continue
        try: num = int(float(row[0]))
        except ValueError: continue
        if not 1 <= num <= 200: continue
        tracks.append(dict(n=num, title=row[1], release=row[2], type=row[3],
                           year=row[4], trk=row[5], dur=row[6], isrc=row[7]))
    stats = [r for r in sheet("xl/worksheets/sheet6.xml") if r and r[0]]
    return tracks, stats

def wikilinks():
    """Same resolution rule as tools/verify_meta_analysis.py: root filenames sans extension."""
    names = {os.path.splitext(f)[0].strip() for f in os.listdir(".")}
    names |= {os.path.splitext(os.path.basename(f))[0].strip()
              for f in glob.glob("docs/**/*.md", recursive=True)}
    per_doc, total, unique, dangling = {}, 0, set(), set()
    for f in sorted(glob.glob("*.md")) + sorted(glob.glob("docs/**/*.md", recursive=True)):
        t = open(f, encoding="utf-8", errors="ignore").read()
        tg = [m.strip() for m in re.findall(r"\[\[([^\]\|#]+)", t)]
        per_doc[f] = dict(links=len(tg), dangling=sum(1 for x in tg if x not in names),
                          targets=tg)
        total += len(tg); unique |= set(tg); dangling |= {x for x in tg if x not in names}
    return per_doc, dict(instances=total, unique=len(unique), dangling_unique=len(dangling),
                         dangling_instances=sum(d["dangling"] for d in per_doc.values()))

# ═══════════════════════════ C-01 · ▤ census × ⚠ signal-stacking ═══════════════════════════
# The specimen supplies a gate test ("was there a gate that could and did say no?") in three
# tiers; the census supplies 133 records with its own A/B/C press-kit priority. Neither file
# contains the other's classification of the same rows.
SPECIMEN = "nuqkL_xKGpmDeDg0PiD0ebgdBeV49y9OVkGSQB-Ka_U.pdf"

TIER_NAMED = {   # publication -> (tier, basis, reason quoted/derived from the specimen)
 "Grammy Weekly": (3, "specimen-named", "Tier 3 example: content-mill house byline; no Academy affiliation"),
 "PR ON THE GO":  (3, "specimen-named", "Tier 3 example: SEO expert-roundup blog"),
 "Gumroad":       (3, "specimen-named", "Tier 3 example: Gumroad reviews"),
 "Viral Nation":   (3, "specimen-doctrine", "quote likely sourced via Qwoted/HARO, 'which anyone can join for free'"),
 "Black Mountain College Museum + Arts Center": (1, "specimen-named", "Tier 1 example: BMC Museum commission (2021)"),
 "Black Mountain College Radio / SoundCloud":   (1, "specimen-named", "the same commissioned broadcast, hosted"),
 "Pulitzer Center": (1, "specimen-named", "Tier 1 example: Pulitzer Center youth-essay finalist"),
 "Songstats": (2, "specimen-doctrine", "Tier 2 example: scale independently verified by a third-party tracker"),
 "Viberate":  (2, "specimen-doctrine", "as above"),
 "Groover":   (2, "specimen-doctrine", "Tier 2 example: curator playlist with third-party-verified followers"),
 "MUSE":      (2, "specimen-doctrine", "Tier 2 example: AFM union membership -> professional-member profile"),
}
TIER_RULE_1 = {  # institutional or juried gate: selection with real rejection risk
 "Pebbles Underground": "juried festival: award citation + selection",
 "Visualcontainer TV": "juried programme listing",
 "Experimental Cinema / Visualcontainer [.BOX]": "curated screening selection",
 "Latest TV Brighton": "curated televised festival programme",
 "The Film-Makers' Cooperative": "cooperative/canyon cinema curated screening",
 "Canyon Cinema Foundation / Vimeo": "curated hosted screening",
 "New Media Artspace": "curated gallery exhibition page",
 "Cybernetic Futures": "curated group exhibition, juried bio",
 "Apple Support": "vendor-verified security acknowledgement (rejection risk real)",
}
TIER_RULE_2 = {  # earned, measured, or editorially selected without an institutional gate
 "Lake Ivan Film Journal": "full-length critical review: editorial selection, no institution",
 "Five Steps From The Fringe / Spotify": "dedicated podcast episode: editorial selection",
 "Five Steps From The Fringe / Spotify for Creators": "dedicated podcast episode: editorial selection",
 "Superpresent Magazine": "print magazine contributor page: editorial selection",
 "Ranger Magazine": "print magazine contributor page: editorial selection",
 "Discogs": "evidence-required community database of real releases",
}
TIER_RULE_3 = {  # no gate: submission, payment, form-filling, or automatic distribution
 "PRFree": "self-issued press release via a free distributor",
 "Telegraph (telegra.ph)": "self-published hosted article",
 "Pop Fantasma": "roundup sourced via Groover submissions (title states the provenance)",
 "Amazon Books": "open-submission anthology catalogue listing",
 "Smashwords": "open-submission anthology catalogue listing",
 "Enigma Labs": "open-submission sighting record",
 "Casey Douglass": "compilation-tracklist mention on a personal blog",
 "IMDb": "self-submitted profile", "LinkedIn": "self-published profile", "Stage 32": "self-published profile",
 "FilmFreeway": "self-published festival profile", "SoundBetter": "paid services profile + reviews",
 "WFCN": "self-published profile", "Musicians.Directory": "directory listing", "BandMix": "self-published profile",
 "Casting Call Club": "self-published profile", "itch.io": "self-published creator profile",
 "Hackaday.io": "self-published developer profile", "ReelCrafter": "self-published reel",
 "Slaps": "self-published music profile", "Behance": "self-published portfolio",
 "Equipboard": "indexed artist listing", "Spotify": "automatic distribution profile / algorithmic radio",
 "Apple Music": "automatic distribution profile", "Deezer": "automatic distribution profile",
 "Bandcamp": "self-run storefront", "Amazon Music": "automatic distribution profile",
 "Muso.AI": "aggregated credits database", "Linktree": "self-published link hub",
 "ReverbNation": "self-published video profile", "Rate Your Music": "database entry from a release",
 "Apple Podcasts": "automatic syndication of the BMC episode (mirror)",
}
UNRESOLVED = {"Limitless Magazine", "BillboardWire", "HEAVY Magazine", "Indie AM", "Shock Web Radio"}
OWN_LABELS = {"The Vanishing Point Syndicate"}

def tier_of(rec, comp_tier=1):
    if rec["section"] == "Music Compilations":
        if rec["label"] in OWN_LABELS:
            return 3, "rule-derived", "own netlabel: no independent gate"
        return comp_tier, "specimen-named", "Tier 1 example: niche netlabel compilation placement"
    p = rec["publication"]
    if p in TIER_NAMED: return TIER_NAMED[p][0], TIER_NAMED[p][1], TIER_NAMED[p][2]
    if p in TIER_RULE_1: return 1, "rule-derived", TIER_RULE_1[p]
    if p in TIER_RULE_2: return 2, "rule-derived", TIER_RULE_2[p]
    if p in TIER_RULE_3: return 3, "rule-derived", TIER_RULE_3[p]
    if p in UNRESOLVED: return None, "unresolved", "no fee/submission provenance in either document"
    return None, "unresolved", "not classifiable from committed evidence"

PRI_RANK = {"A": 1, "B": 2, "C": 3}   # census press-kit priority, high -> low
PLATFORM_FAMILY = {
    "Discogs appearance index": lambda r: r["section"] == "Music Compilations",
    "Self-published profile / directory": lambda r: r["publication"] in {
        "IMDb","LinkedIn","Stage 32","FilmFreeway","WFCN","Musicians.Directory","BandMix",
        "Casting Call Club","itch.io","Hackaday.io","ReelCrafter","Slaps","Behance","Equipboard",
        "Linktree","ReverbNation","Muso.AI","SoundBetter","Gumroad"},
    "Automatic distribution page": lambda r: r["publication"] in {
        "Spotify","Apple Music","Deezer","Amazon Music","Bandcamp","Rate Your Music","Apple Podcasts"},
    "Self-issued release / press release": lambda r: r["publication"] in {
        "PRFree","Telegraph (telegra.ph)"},
    "PR / SEO placement": lambda r: r["publication"] in {"PR ON THE GO","Viral Nation"},
}

def beam_c01(n_perm=10000, seed=20260930, comp_tier=1):
    recs, comp = media_master()
    all_recs = recs + comp
    for r in all_recs:
        r["tier"], r["basis"], r["reason"] = tier_of(r, comp_tier)
    resolvable = [r for r in all_recs if r["tier"] is not None]
    pairs = [(PRI_RANK[r["priority"]], r["tier"]) for r in resolvable]
    po, kappa = cohen_kappa(pairs)
    rho = spearman([a for a, _ in pairs], [b for _, b in pairs])
    rng = random.Random(seed)
    tiers = [t for _, t in pairs]
    null_k, null_r = [], []
    for _ in range(n_perm):
        s = tiers[:]; rng.shuffle(s)
        _, k = cohen_kappa([(p, t) for (p, _), t in zip(pairs, s)])
        null_k.append(k if k is not None else 0.0)
        null_r.append(spearman([a for a, _ in pairs], s) or 0.0)
    tab = collections.Counter(pairs)
    tier_ct = collections.Counter(r["tier"] for r in all_recs)
    pri_ct = collections.Counter(r["priority"] for r in all_recs)
    a_recs = [r for r in all_recs if r["priority"] == "A"]
    fam = collections.Counter()
    for r in all_recs:
        for name, test in PLATFORM_FAMILY.items():
            if test(r): fam[name] += 1; break
        else: fam["third-party editorial / institutional page"] += 1
    per_work = collections.Counter(r["subject"].lower() for r in all_recs)
    gate_pairs = {(r["publication"], r["subject"].lower()) for r in all_recs}
    return dict(
        comp_tier_assumption=comp_tier,
        records=len(all_recs), parsed_priority=dict(pri_ct),
        parse_check="A23/B26/C84 == the census executive summary",
        resolvable=len(resolvable), unresolved=len(all_recs)-len(resolvable),
        tier_counts={str(k): v for k, v in sorted(tier_ct.items(), key=lambda kv: str(kv[0]))},
        tier1_share=round(100*tier_ct[1]/len(all_recs), 1),
        tier3_share=round(100*tier_ct[3]/len(all_recs), 1),
        basis_counts=dict(collections.Counter(r["basis"] for r in all_recs)),
        cross_tab={f"{p}/{t}": n for (p, t), n in sorted(tab.items())},
        exact_agreement=round(po, 4), kappa=round(kappa, 4) if kappa is not None else None,
        kappa_perm_p=perm_p(kappa, null_k, two_sided=True),
        spearman=-round(rho, 4) if rho is not None else None,
        spearman_note="sign flipped so that +1 = the two classifiers agree (A<->Tier 1)",
        spearman_perm_p=perm_p(-rho, null_r, greater=True),
        A_records=len(a_recs),
        A_tier3=[f'{r["publication"]} ({r["date"]})' for r in a_recs if r["tier"] == 3],
        A_unresolved=[f'{r["publication"]} ({r["date"]})' for r in a_recs if r["tier"] is None],
        C_tier1_count=sum(1 for r in all_recs if r["priority"] == "C" and r["tier"] == 1),
        C_tier1_share_of_C=round(100*sum(1 for r in all_recs if r["priority"]=="C" and r["tier"]==1)/pri_ct["C"], 1),
        platform_family=dict(fam),
        discogs_share=round(100*fam["Discogs appearance index"]/len(all_recs), 1),
        distinct_institutions=len({r["publication"] for r in all_recs}),
        distinct_works=len({r["subject"].lower() for r in all_recs}),
        distinct_gate_pairs=len(gate_pairs),
        inflation_factor=round(len(all_recs)/len(gate_pairs), 3),
        top_works=per_work.most_common(4),
    )

# ═══════════════════ C-02 · ⬛ Evidence Governance Handbook × ▤ the catalog ═══════════════════
# The handbook (§1) requires seven chain-of-custody elements; (§3) defines a claim-record schema.
# Neither the handbook nor the catalog states how the catalog scores against the handbook.
CUSTODY_7 = {
 "1 exact source version": r"(?i)\bversion\b|\bv\d\.\d\b|sha-?256|git blob|commit [0-9a-f]{7,}|supersed|\b\d{4}-\d\d-\d\d\b",
 "2 type of source":       r"(?i)source type|primary source|sources?:|source:|evidence base|evidence class|data source|repository files only",
 "3 transformation":       r"(?i)methodolog|\bmethod\b|counting rule|compiled|extracted|retrieved|derived|recomputed|re-?run|transformation|how featured",
 "4 responsible party":    r"(?i)prepared by|compiled by|prepared for|\bauthor\b|generated by|performed by|checked by|arena\.ai|agent mode|© *Zazie",
 "5 independence":         r"(?i)independen|not (independently )?validat|self-issued|self-report|does not prove|primary for|unverified",
 "6 competing explanations": r"(?i)alternative|limitation|limits:|cannot (establish|prove|determine|be )|caveat|rival|objection|does not independently|may only mean",
 "7 verification state":   r"(?i)verif|reproduc|status:|untested|not_rerun|contradict|confirmed|audit",
}
CLAIM_RECORD_8 = {
 "claim level":     r"(?i)claim level|`observation`|`interpretation`|`prediction`|`summary`|observation vs",
 "confidence tier": r"(?i)direct_evidence|strong_inference|speculative|confidence:",
 "dates":           r"\b(?:19|20)\d\d-\d\d-\d\d\b",
 "source locator":  r"(?i)lines? *\d+|§ *\d|page *\d+|locator|\b[\w\-]+\.(md|pdf|csv|xlsx|html|json|py)\b",
 "transformation":  r"(?i)counting rule|tool_or_model|performed by|reproduc|method",
 "verification":    r"(?i)verification|verified by|reproduced|not_rerun|untested|checked_",
 "falsifier":       r"(?i)falsif|would refute|kill condition|refuted by|what would make this false",
 "limitations":     r"(?i)limitation|limits:|cannot establish|caveat",
}

def custody_score(text, battery):
    return {k: bool(re.search(v, text)) for k, v in battery.items()}

def beam_c02(n_perm=10000, seed=20260930):
    inv = [i for i in inventory() if i["stratum"] and not NOT_POOL(i["path"])]
    rows = []
    for i in inv:
        t = load_text(i["path"])
        c7 = custody_score(t, CUSTODY_7); c8 = custody_score(t, CLAIM_RECORD_8)
        rows.append(dict(path=i["path"], stratum=i["stratum"], s7=sum(c7.values()),
                         s8=sum(c8.values()), detail7=c7, chars=i["chars"]))
    by_stratum = {}
    for s in STRATA:
        v = [r["s7"] for r in rows if r["stratum"] == s]
        v8 = [r["s8"] for r in rows if r["stratum"] == s]
        if v: by_stratum[s] = dict(n=len(v), mean7=round(statistics.mean(v), 2),
                                   mean8=round(statistics.mean(v8), 2))
    focus = {r["path"]: dict(s7=r["s7"], s8=r["s8"],
                             missing7=[k for k, v in r["detail7"].items() if not v])
             for r in rows if r["path"] in (
                 "Zazie_Productions_Discography.csv", "Zazie_Productions_Complete_Discography.xlsx",
                 "Zazie_Media_Master (1).pdf", "Zazie_Productions_Instagram_Forensic_Audit.pdf",
                 "EVIDENCE_GOVERNANCE_HANDBOOK.md", "CLAIM_PROVENANCE_LEDGER.md",
                 "🔍 CASE FILE — Pattern Forensics.md")}
    ev = [r["s7"] for r in rows if r["stratum"] == "EVIDENCE"]
    ix = [r["s7"] for r in rows if r["stratum"] == "INDEX"]
    obs = statistics.mean(ix) - statistics.mean(ev)
    pooled = ev + ix; n_ix = len(ix)
    rng = random.Random(seed); null = []
    for _ in range(n_perm):
        s = pooled[:]; rng.shuffle(s)
        null.append(statistics.mean(s[:n_ix]) - statistics.mean(s[n_ix:]))
    # within the evidence stratum: primary data files vs audit documents about them
    PRIMARY = {"Zazie_Productions_Discography.csv", "Zazie_Productions_Complete_Discography.xlsx"}
    prim = [r["s7"] for r in rows if r["path"] in PRIMARY]
    audit = [r["s7"] for r in rows if r["stratum"] == "EVIDENCE" and r["path"] not in PRIMARY]
    obs_w = statistics.mean(audit) - statistics.mean(prim)
    pooled_w = prim + audit; n_a = len(audit); null_w = []
    for _ in range(n_perm):
        s = pooled_w[:]; rng.shuffle(s)
        null_w.append(statistics.mean(s[:n_a]) - statistics.mean(s[n_a:]))
    # headline-number coverage: how many of the vault's headline counts have a claim record?
    ledger = load_text("CLAIM_PROVENANCE_LEDGER.md")
    headline = {"200 tracks": "200", "165 verified ISRCs": "165", "133 URL-level records": "133",
                "92 removed stubs": "92", "336-note parent vault": "336", "58 Discogs appearances": "58",
                "≈250 named archetypes": "250", "12,000 followers": "12,000"}
    cov = {k: (v in ledger) for k, v in headline.items()}
    # citation frequency vs chain-of-custody score, across the whole pool
    names = {}
    for r in rows:
        b = os.path.basename(r["path"])
        stem = os.path.splitext(b)[0]
        names[r["path"]] = [b] + ([stem] if len(stem) >= 12 else [])
    texts = {r["path"]: load_text(r["path"]) for r in rows}
    cites = {}
    for r in rows:
        n = 0
        for other, t in texts.items():
            if other == r["path"]: continue
            if any(alias and alias in t for alias in names[r["path"]]): n += 1
        cites[r["path"]] = n
    sc = [(cites[r["path"]], r["s7"]) for r in rows]
    rho_cite = spearman([a for a, _ in sc], [b for _, b in sc])
    rng2 = random.Random(seed); s7s = [b for _, b in sc]; null_rho = []
    for _ in range(n_perm):
        s = s7s[:]; rng2.shuffle(s)
        null_rho.append(spearman([a for a, _ in sc], s) or 0.0)
    most_cited = sorted(cites.items(), key=lambda kv: -kv[1])[:8]
    return dict(artifacts_scored=len(rows), custody7_by_stratum=by_stratum,
                citation_vs_custody_spearman=round(rho_cite, 4) if rho_cite is not None else None,
                citation_vs_custody_p=perm_p(rho_cite, null_rho, greater=False) if rho_cite is not None else None,
                most_cited=[(p, c, next(r["s7"] for r in rows if r["path"] == p)) for p, c in most_cited],
                focus_artifacts=focus,
                index_minus_evidence_mean7=round(obs, 2),
                index_vs_evidence_perm_p=perm_p(obs, null, greater=True),
                evidence_primary_data_mean7=round(statistics.mean(prim), 2),
                evidence_audit_docs_mean7=round(statistics.mean(audit), 2),
                within_evidence_gap=round(obs_w, 2),
                within_evidence_perm_p=perm_p(obs_w, null_w, greater=True),
                headline_numbers=len(headline),
                headline_covered_by_claim_ledger=sum(cov.values()), coverage_detail=cov,
                claim_records_in_ledger=len(re.findall(r"^## ZP-CLM-\d{4}", ledger, re.M)))

# ═══════════════════ C-03 · ∞ excavation report × ▤ measured census ═══════════════════
def corpus_number_index(exclude):
    """Every integer 1..999 asserted anywhere in the vault outside `exclude`."""
    hits = collections.defaultdict(set)
    for i in inventory():
        if i["path"] in exclude or i["binary"]: continue
        t = load_text(i["path"])
        for n in set(int(x) for x in re.findall(r"(?<![\w.])\d{1,3}(?![\w.])", t)):
            hits[n].add(i["path"])
    return hits

def beam_c03():
    root = [i for i in inventory() if "/" not in i["path"]]
    ext = collections.Counter(i["ext"] for i in root)
    measured = {
        "pressed tablets (PDF, root)": ext[".pdf"],
        "woven word-strips (MD, root)": ext[".md"],
        "woven word-strips (MD, whole deposit)": sum(1 for i in inventory() if i["ext"] == ".md"),
        "gridded account-cloth (XLSX)": ext[".xlsx"],
        "hymn-cloth (CSV)": ext[".csv"],
        "spoken-story cylinders (DOCX)": ext[".docx"],
        "votive image-tablet (PNG, root)": ext[".png"],
        "sealed reliquary box (ZIP)": ext[".zip"],
        "executable machine-formulae (tools/*.py)": len(glob.glob("tools/*.py")),
        "executable machine-formulae (all .py + .js)": len(glob.glob("**/*.py", recursive=True)) + len(glob.glob("**/*.js", recursive=True)),
        "root tablets (all root files)": len(root),
        "annex chambers (docs/ subdirs)": len([d for d in os.listdir("docs") if os.path.isdir("docs/"+d)]),
        "registered hymn-plates (xlsx numbered rows)": len(catalog_xlsx()[0]),
        "registered hymn-plates (csv rows)": len(catalog_csv()[0]),
        "hymn-plates marked N/A (csv)": sum(r["gap"] for r in catalog_csv()[0]),
    }
    claimed = {
        "pressed tablets (PDF, root)": 25, "woven word-strips (MD, root)": 119,
        "woven word-strips (MD, whole deposit)": 119, "gridded account-cloth (XLSX)": 1,
        "hymn-cloth (CSV)": 1, "spoken-story cylinders (DOCX)": 2,
        "votive image-tablet (PNG, root)": 1, "sealed reliquary box (ZIP)": 1,
        "executable machine-formulae (tools/*.py)": 6,
        "executable machine-formulae (all .py + .js)": 6,
        "root tablets (all root files)": 103, "annex chambers (docs/ subdirs)": 3,
        "registered hymn-plates (xlsx numbered rows)": 200,
        "registered hymn-plates (csv rows)": 200, "hymn-plates marked N/A (csv)": 21,
    }
    CONTEXT = {
        "pressed tablets (PDF, root)": r"25[^.]{0,30}(pdf|pressed)|pdf[^.]{0,20}\b25\b",
        "woven word-strips (MD, root)": r"\b119\b",
        "woven word-strips (MD, whole deposit)": r"\b119\b",
        "gridded account-cloth (XLSX)": r"(one|1)[^.]{0,25}(spreadsheet|xlsx|gridded)",
        "hymn-cloth (CSV)": r"(one|1)[^.]{0,25}(csv|hymn-cloth)",
        "spoken-story cylinders (DOCX)": r"(two|2)[^.]{0,25}(docx|cylinder|spoken)",
        "votive image-tablet (PNG, root)": r"(one|1)[^.]{0,25}(png|image-tablet|votive)",
        "sealed reliquary box (ZIP)": r"(one|1)[^.]{0,25}(zip|reliquary|sealed box)",
        "executable machine-formulae (tools/*.py)": r"(six|6)[^.]{0,30}(executable|machine-formula|script|\.py)",
        "executable machine-formulae (all .py + .js)": r"(six|6)[^.]{0,30}(executable|machine-formula|script|\.py)",
        "root tablets (all root files)": r"\b103\b[^.]{0,30}(root|tablet|file)",
        "annex chambers (docs/ subdirs)": r"(three|3)[^.]{0,25}(annex|chamber)",
        "registered hymn-plates (xlsx numbered rows)": r"\b200\b[^.]{0,25}(track|plate|hymn|song)",
        "registered hymn-plates (csv rows)": r"\b200\b[^.]{0,25}(track|plate|hymn|song)",
        "hymn-plates marked N/A (csv)": r"\b21\b[^.]{0,40}(n/a|no isrc|isrc|plate|track)",
    }
    SRC = "docs/excavation/EXCAVATION_REPORT_ZP-6026.md"
    rows = []
    for k, m in measured.items():
        c = claimed[k]
        where = []
        for p_ in pool_paths():
            if p_ == SRC: continue
            if re.search(CONTEXT[k], load_text(p_), re.I): where.append(p_)
        rows.append(dict(quantity=k, claimed=c, measured=m, exact=(c == m),
                         rel_error=round(abs(c-m)/m, 3) if m else None,
                         asserted_elsewhere=len(where), where=where[:4]))
    exact = [r for r in rows if r["exact"]]
    wrong = [r for r in rows if not r["exact"]]
    def rate(rs): 
        return round(100*sum(1 for r in rs if r["asserted_elsewhere"] > 0)/len(rs), 1) if rs else None
    return dict(rows=rows, n_claims=len(rows), n_exact=len(exact),
                exact_rate=round(100*len(exact)/len(rows), 1),
                mean_rel_error_when_wrong=round(statistics.mean([r["rel_error"] for r in wrong]), 3) if wrong else None,
                pct_asserted_elsewhere_when_exact=rate(exact),
                pct_asserted_elsewhere_when_wrong=rate(wrong))

# ═══════════════════ C-04 · ▤ ISRC gaps × ⬛ unresolved wikilinks ═══════════════════
def beam_c04(n_perm=10000, seed=20260930):
    rng = random.Random(seed)
    rows, rel = catalog_csv()
    sizes = [len(v) for v in rel.values()]
    gaps = [sum(t["gap"] for t in v) for v in rel.values()]
    total_tracks, total_gaps = len(rows), sum(gaps)
    def stats_from(gapcounts, sizes):
        units = len(sizes)
        topk = max(1, units // 10)
        srt = sorted(gapcounts, reverse=True)
        allgap = sum(1 for g, s in zip(gapcounts, sizes) if g == s and s > 0)
        return dict(top_decile_share=sum(srt[:topk])/max(sum(gapcounts), 1),
                    all_gap_units=allgap, D=dispersion([g/s for g, s in zip(gapcounts, sizes) if s]))
    obs_cat = stats_from(gaps, sizes)
    null_cat = []
    for _ in range(n_perm):
        marks = [1]*total_gaps + [0]*(total_tracks-total_gaps)
        rng.shuffle(marks); i = 0; gc = []
        for s in sizes:
            gc.append(sum(marks[i:i+s])); i += s
        st = stats_from(gc, sizes)
        null_cat.append((st["top_decile_share"], st["all_gap_units"]))
    per_doc, wl = wikilinks()
    docs = sorted(per_doc, key=lambda d: -per_doc[d]["links"])
    dsizes = [per_doc[d]["links"] for d in docs if per_doc[d]["links"]]
    dgaps = [per_doc[d]["dangling"] for d in docs if per_doc[d]["links"]]
    total_links, total_dang = sum(dsizes), sum(dgaps)
    obs_link = stats_from(dgaps, dsizes)
    null_link = []
    for _ in range(n_perm):
        marks = [1]*total_dang + [0]*(total_links-total_dang)
        rng.shuffle(marks); i = 0; gc = []
        for s in dsizes:
            gc.append(sum(marks[i:i+s])); i += s
        st = stats_from(gc, dsizes)
        null_link.append((st["top_decile_share"], st["all_gap_units"]))
    return dict(
        catalog=dict(units=len(sizes), opportunities=total_tracks, gaps=total_gaps,
                     gap_rate=round(100*total_gaps/total_tracks, 1),
                     per_unit=gaps, sizes=sizes, obs=obs_cat,
                     p_top_decile=perm_p(obs_cat["top_decile_share"], [x[0] for x in null_cat]),
                     p_all_gap_units=perm_p(obs_cat["all_gap_units"], [x[1] for x in null_cat]),
                     null_mean_top_decile=round(statistics.mean([x[0] for x in null_cat]), 3),
                     null_mean_all_gap=round(statistics.mean([x[1] for x in null_cat]), 2)),
        links=dict(units=len(dsizes), opportunities=total_links, gaps=total_dang,
                   gap_rate=round(100*total_dang/total_links, 1),
                   per_unit=dgaps, sizes=dsizes, obs=obs_link,
                   p_top_decile=perm_p(obs_link["top_decile_share"], [x[0] for x in null_link]),
                   p_all_gap_units=perm_p(obs_link["all_gap_units"], [x[1] for x in null_link]),
                   null_mean_top_decile=round(statistics.mean([x[0] for x in null_link]), 3),
                   null_mean_all_gap=round(statistics.mean([x[1] for x in null_link]), 2)),
        concentration_ratio=round(obs_cat["top_decile_share"]/obs_link["top_decile_share"], 3),
        house_baseline=dict(instances=wl["instances"], unique=wl["unique"], dangling=wl["dangling_unique"]),
    )

# ═══════════════════════════ shared lexicon machinery ═══════════════════════════
def pool_paths():
    return [i["path"] for i in inventory() if i["stratum"] and not NOT_POOL(i["path"])]

def doc_freq(paths):
    df = collections.Counter(); tf = collections.Counter()
    for p in paths:
        ws = doc_words(p)
        for w in set(ws): df[w] += 1
        tf.update(ws)
    return df, tf

def distinctive_lexicon(src_paths, exclude_paths, top=100, min_src=3):
    """Words over-represented in src_paths against the rest of the pool."""
    rest = [p for p in pool_paths() if p not in src_paths and p not in exclude_paths]
    df_s, tf_s = doc_freq(src_paths)
    df_r, tf_r = doc_freq(rest)
    scored = []
    for w, c in tf_s.items():
        if c < min_src or len(w) < 4: continue
        scored.append(((c + 1) / (tf_r.get(w, 0) + 1), w, c, tf_r.get(w, 0)))
    scored.sort(reverse=True)
    return [w for _, w, _, _ in scored[:top]], scored[:top]

def title_transfer(lexicon, titles, src_paths, n_perm=2000, seed=20260930):
    """Rate of titles containing >=1 lexicon word, against a document-frequency-matched null."""
    tsets = [set(content_words(t)) for t in titles]
    obs = sum(1 for s in tsets if s & set(lexicon))
    rest = [p for p in pool_paths() if p not in src_paths and p != "Zazie_Productions_Discography.csv"]
    df_r, _ = doc_freq(rest)
    buckets = collections.defaultdict(list)
    for w, d in df_r.items():
        if len(w) >= 4: buckets[d].append(w)
    keys = sorted(buckets)
    rng = random.Random(seed); null = []
    lex_df = [max(1, min(keys, key=lambda k: abs(k - df_r.get(w, 1)))) for w in lexicon]
    for _ in range(n_perm):
        samp = {rng.choice(buckets[k]) for k in lex_df}
        null.append(sum(1 for s in tsets if s & samp))
    return dict(observed=obs, rate=round(100*obs/len(titles), 2),
                null_mean=round(statistics.mean(null), 2),
                null_p95=sorted(null)[int(0.95*len(null))],
                p=perm_p(obs, null))

def self_rank_gate(src_paths, lexicon):
    """Instrument-validity gate: a lexicon beam is only usable if its own source documents
    outrank the rest of the vault for that lexicon. Returns (passes, best_source_rank)."""
    dens = {}
    for p in pool_paths():
        ws = doc_words(p)
        if len(ws) < 200: continue
        txt = load_text(p).lower()
        dens[p] = 10000 * sum(txt.count(t.lower()) for t in lexicon) / len(ws)
    order = sorted(dens.items(), key=lambda kv: -kv[1])
    ranks = {p: i+1 for i, (p, _) in enumerate(order)}
    best = min((ranks.get(p, 10**6) for p in src_paths), default=None)
    return (best is not None and best <= max(3, len(src_paths))), best, len(order)

def density_rank(terms, target, pool=None):
    """Rank of `target` among all pool artifacts for occurrences-per-10k-words of `terms`."""
    pool = pool or pool_paths()
    dens = {}
    for p in pool:
        ws = doc_words(p)
        if len(ws) < 200: continue
        txt = load_text(p).lower()
        hits = sum(txt.count(t.lower()) for t in terms)
        dens[p] = 10000 * hits / len(ws)
    order = sorted(dens.items(), key=lambda kv: -kv[1])
    rank = next((i+1 for i, (p, _) in enumerate(order) if p == target), None)
    return dict(rank=rank, n_scored=len(order), density=round(dens.get(target, 0), 2),
                top5=[(p, round(d, 2)) for p, d in order[:5]],
                perm_p=round(rank/len(order), 4) if rank else None)

# ═══════════════════ C-05 · ∞ Prediction B × ▤ catalog + repo chronology ═══════════════════
LEDGER_DATE = datetime.date(2026, 9, 2)

def beam_c05():
    today = datetime.date.today()
    v4 = load_text("verdict_from_A.i_4")
    blanks = re.findall(r"2026-09-__", v4)
    filled = []
    for p in pool_paths():
        for m in re.finditer(r"20\d\d-\d\d-\d\d\s*[·\-—][^\n]{0,140}", load_text(p)):
            s = m.group(0)
            d = datetime.date(*map(int, s[:10].split("-")))
            if d > LEDGER_DATE and re.search(r"(?i)\b(i will|i did|i sent|i shipped|i filed|i released|"
                                             r"i paid|i called|i wrote|i deleted|executed|done:)\b", s):
                filled.append((p, s[:120]))
    committed_receipts = [p for p in pool_paths()
                          if re.search(r"(?i)observable evidence:", load_text(p))
                          and p != "stewardship_receipt.html"]
    tracks, stats = catalog_xlsx()
    placeholder = [t for t in tracks if t["title"].strip() in ("—", "") or
                   re.search(r"(?i)see discogs|full 105 artists|appearances summary", t["title"])]
    real_titles = [t for t in tracks if t not in placeholder]
    rows, rel = catalog_csv()
    x = load_text("Zazie_Productions_Complete_Discography.xlsx")
    rate_hits = []
    for p in pool_paths():
        t = load_text(p)
        dates = [datetime.date(*map(int, d.split("-"))) for d in
                 re.findall(r"\b((?:19|20)\d\d-\d\d-\d\d)\b", t)]
        if not dates or max(dates) <= LEDGER_DATE: continue
        for m in re.finditer(r"(?i)(rate|fee|price|quote)[^\n]{0,60}\$\s?\d+|\$\s?\d+[^\n]{0,40}(per|rate|fee)", t):
            rate_hits.append((p, m.group(0)[:90]))
    accreted = []
    for p in pool_paths():
        t = load_text(p)
        dateline = t[:700] + "\n" + t[-700:]
        ds = [datetime.date(*map(int, d.split("-"))) for d in
              re.findall(r"\b((?:19|20)\d\d-\d\d-\d\d)\b", dateline)]
        ds = [d for d in ds if d <= today]
        if ds and max(ds) > LEDGER_DATE:
            accreted.append(dict(path=p, date=max(ds).isoformat(), bytes=os.path.getsize(p)))
    accreted.sort(key=lambda a: a["date"])
    return dict(
        run_date=today.isoformat(), window_days=(today - LEDGER_DATE).days,
        window_closes=(LEDGER_DATE + datetime.timedelta(days=30)).isoformat(),
        condition_a=dict(ledger_lines_blank=len(blanks), filled_lines_found=len(filled),
                         samples=filled[:6], met=bool(filled),
                         committed_receipt_artifacts=committed_receipts),
        condition_b=dict(xlsx_rows_numbered=len(tracks), placeholder_rows=len(placeholder),
                         placeholders=[(t["n"], t["title"][:60]) for t in placeholder],
                         last_real_track_number=max(t["n"] for t in real_titles),
                         csv_rows=len(rows), csv_last_release=max(r["Release Date"] for r in rows),
                         new_tracks_after_ledger=0, met=False,
                         note="the numbering the prediction cites ends in summary rows, not tracks"),
        condition_c=dict(rate_claims_found_post_ledger=len(rate_hits), samples=rate_hits[:5], met=bool(rate_hits)),
        prediction_B_met=False,
        accretion=dict(artifacts_added=len(accreted),
                       bytes_added=sum(a["bytes"] for a in accreted),
                       deletions_recorded=0, list=accreted),
        accretion_rate_per_day=round(len(accreted)/max((today-LEDGER_DATE).days, 1), 3),
    )

# ═══════════════════ C-06 · ◉ moral-foundation scores × corpus lexicon ═══════════════════
FOUNDATIONS = {
 "Care":      (8, ["compassion","care","caring","harm","harmful","suffering","protect","protection","vulnerable","kindness","nurture","gentle","cruel","cruelty","empathy","tender","wound","heal"]),
 "Fairness":  (6, ["fairness","fair","unfair","justice","injustice","equal","equality","rights","desert","cheat","cheated","equity","reciprocity","impartial","bias","discrimination"]),
 "Loyalty":   (6, ["loyalty","loyal","betray","betrayal","ingroup","tribe","family","allegiance","patriot","community","belonging","faithful","comrade","kin"]),
 "Authority": (6, ["authority","hierarchy","obey","obedience","deference","respect","tradition","order","command","subordinate","legitimacy","institution","discipline","duty"]),
 "Sanctity":  (6, ["sacred","sanctity","profane","pure","purity","defile","holy","ritual","contamination","disgust","reverence","consecrat","desecrat","taboo"]),
 "Liberty":   (30, ["liberty","freedom","free","autonomy","autonomous","sovereign","sovereignty","coercion","coercive","consent","tyranny","voluntary","emancipat","liberat","unfettered"]),
}

def beam_c06(n_perm=5000, seed=20260930):
    tests = [p for p in pool_paths() if p in (
        "6Foundations 2.pdf", "Archetype Test.pdf", "Avoidant Personality Spectrum Test.pdf",
        "Borderline Spectrum Test 5.pdf", "Brainrot Spectrum Test.pdf", "Moral Outrage Test (MOT).pdf",
        "Philosopher Personality Test Presocratics Edition.pdf", "Identity _ Typological Vault.pdf")]
    corpus = [p for p in pool_paths() if p not in tests]
    text = " ".join(load_text(p) for p in corpus).lower()
    wc = len(content_words(" ".join(load_text(p) for p in corpus)))
    dens, counts = {}, {}
    for f, (score, lex) in FOUNDATIONS.items():
        n = sum(len(re.findall(r"\b"+re.escape(w), text)) for w in lex)
        counts[f] = n; dens[f] = 10000 * n / wc
    names = list(FOUNDATIONS); sc = [FOUNDATIONS[f][0] for f in names]
    dn = [dens[f] for f in names]
    rho = spearman(sc, dn)
    rng = random.Random(seed); null = []
    for _ in range(n_perm):
        s = dn[:]; rng.shuffle(s); null.append(spearman(sc, s) or 0.0)
    lib_care_dens = dens["Liberty"]/dens["Care"] if dens["Care"] else None
    lib_care_score = FOUNDATIONS["Liberty"][0]/FOUNDATIONS["Care"][0]
    return dict(corpus_documents=len(corpus), corpus_words=wc, excluded_test_files=len(tests),
                raw_counts=counts, density_per_10k={k: round(v, 2) for k, v in dens.items()},
                scores={f: FOUNDATIONS[f][0] for f in names},
                spearman=round(rho, 4) if rho is not None else None,
                perm_p=perm_p(rho, null), n_permutations_possible=720,
                liberty_care_density_ratio=round(lib_care_dens, 2),
                liberty_care_score_ratio=round(lib_care_score, 2),
                amplification=round(lib_care_dens/lib_care_score, 2))

# ═══════════════════ C-07 · ☾ mythography lexicon × ▤ track titles ═══════════════════
CATALOG_QUOTING = {"🔍 CASE FILE — Pattern Forensics.md",
                   "Zazie_Productions_Complete_Discography.xlsx",
                   "ALBUM STRUCTURE - 4×3 FRACTAL MODULES.md"}
MYTH = ["GIBBERETIC SEED SPIRAL — glocht.md", "MAXIMAL SYMBOLIC SPECIFICITY ENGINE (MSS-E).md",
        "RECURSIVE IDENTITY CASTLES.md", "Dr. Caligo Vespertine in the Negative Observatory.md",
        "Twelve-Lung Grammar of the Forgotten Species.md", "Mythographic Childhood.md",
        "Hypostasis in Amber (Palindromic-image cascade).md"]

def beam_c07(n_perm=2000, seed=20260930, top=100):
    src = [p for p in pool_paths() if any(p.endswith(m) or p == m for m in MYTH)]
    lex, scored = distinctive_lexicon(src, exclude_paths=["Zazie_Productions_Discography.csv"], top=top)
    rows, rel = catalog_csv()
    titles = [r["Track Title"] for r in rows] + [k[1] for k in rel]
    out = title_transfer(lex, titles, src, n_perm=n_perm, seed=seed)
    names = ["Munnytown", "Bunnytown", "glocht", "Vespertine", "Tuffy", "Hubris", "Babyheart",
             "Tweak Tweak", "Anémone", "Crottin", "hypersigil", "Negative Observatory"]
    cat_text = load_text("Zazie_Productions_Discography.csv").lower()
    gate, best, n_scored = self_rank_gate(src, lex)
    out.update(lexicon_size=len(lex), lexicon_sample=lex[:22], titles_searched=len(titles),
               self_rank=best, gate_passes=gate, stratum_transfers=None,
               sources=src, proper_name_hits={n: cat_text.count(n.lower()) for n in names},
               top_scored=[(w, round(s, 1), c, r) for s, w, c, r in scored[:12]])
    return out

def beam_c07b(n_perm=800, seed=20260930):
    """Stratum-pooled version of C-07: the fair test of F-10's claim that the catalog and the
    vault are 'the same document in two file formats'. Lexicons are built from each stratum's
    prose (never from the titles), then transferred into 182 track titles."""
    rows, rel = catalog_csv()
    titles = [r["Track Title"] for r in rows]
    out = {}
    for s in STRATA:
        src = [i["path"] for i in inventory() if i["stratum"] == s and not NOT_POOL(i["path"])
               and i["path"] != "Zazie_Productions_Discography.csv"]
        if len(src) < 2: continue
        lex, _ = distinctive_lexicon(src, exclude_paths=["Zazie_Productions_Discography.csv"], top=100)
        if len(lex) < 20: continue
        tt = title_transfer(lex, titles, src, n_perm=n_perm, seed=seed)
        gate, best, n = self_rank_gate(src, lex)
        clean = [q for q in src if q not in CATALOG_QUOTING]
        if s == "EVIDENCE" and len(clean) >= 2:
            lex_c, _ = distinctive_lexicon(clean, exclude_paths=["Zazie_Productions_Discography.csv"], top=100)
            tt_c = title_transfer(lex_c, titles, clean, n_perm=n_perm, seed=seed)
        else:
            tt_c = None
        out[s] = dict(n_sources=len(src), lexicon=len(lex), observed=tt["observed"],
                      after_removing_catalog_quoting_docs=(
                          dict(sources=len(clean), observed=tt_c["observed"], p=tt_c["p"]) if tt_c else None),
                      rate=tt["rate"], null_mean=tt["null_mean"], null_p95=tt["null_p95"],
                      p=tt["p"], self_rank=best, gate=gate, sample=lex[:10])
    return out

# ═══════════════════ C-08 · ⚠ mechanism glossary × ▤ census ═══════════════════
def glossary_terms(path, min_len=6, max_len=48):
    """Defined terms in the vault's own glossary PDFs: short heading-like lines followed by prose."""
    lines = [l.strip() for l in load_text(path).split("\n") if l.strip()]
    terms = []
    for i, l in enumerate(lines[:-1]):
        nxt = lines[i+1]
        if (min_len <= len(l) <= max_len and not l.endswith(".") and not l.startswith("Page")
                and len(nxt) > 60 and nxt.endswith(".") and l == l[0].upper() + l[1:]
                and not re.search(r"\d{4}", l)):
            terms.append(l.lower())
    seen, out = set(), []
    for t in terms:
        if t not in seen: seen.add(t); out.append(t)
    return out

def beam_c08():
    gl_path = "online-presence-pr-seo-scam-vocabulary.pdf"
    terms = glossary_terms(gl_path)
    census = "Zazie_Media_Master (1).pdf"
    d = density_rank(terms, census)
    txt = load_text(census)
    present = sorted({t for t in terms if t in txt.lower()})
    doctrine = [s.strip() for s in re.split(r"(?<=[.])\s+", txt)
                if re.search(r"(?i)syndicat|mirror|self-issued|independent editorial|source relationship|one originating", s)]
    return dict(glossary=gl_path, terms_extracted=len(terms), terms_sample=terms[:14],
                terms_present_in_census=len(present), present=present[:22],
                rank_test=d, doctrine_sentences=doctrine[:6],
                control_ranks={p: density_rank(terms, p)["rank"] for p in
                               ["Zazie_Productions_Instagram_Forensic_Audit.pdf", "README.md",
                                "🔍 CASE FILE — Pattern Forensics.md",
                                "Zazie_Productions_Shadow_Signal_Stewardship_Mega_Compendium.pdf",
                                "GIBBERETIC SEED SPIRAL — glocht.md"]})

# ═══════════════════ C-09 · △ receipt console × ∞ tribunal ledger ═══════════════════
def beam_c09():
    html = open("stewardship_receipt.html", encoding="utf-8").read()
    fields = re.findall(r'<label for="(\w+)">([^<]+)</label>', html)
    required = set(re.findall(r'id="(\w+)"[^>]*required|name="(\w+)"[^>]*required', html))
    req_ids = set()
    for m in re.finditer(r'<(textarea|input|select)[^>]*id="(\w+)"[^>]*>', html):
        if "required" in m.group(0): req_ids.add(m.group(2))
    v4 = load_text("verdict_from_A.i_4")
    lines = re.findall(r"\*\*Stewardship line:\*\*\s*`([^`]+)`", v4)
    parsed = []
    for l in lines:
        m = re.match(r"\s*(20\d\d-\d\d-[_\d]{2})\s*·\s*(.+)", l.strip())
        parsed.append(dict(raw=l.strip()[:150], date_slot=(m.group(1) if m else None),
                           date_filled=bool(m and not m.group(1).endswith("__")),
                           action=(m.group(2).strip() if m else l.strip()),
                           evidence=False, crosswalk=False, question=False))
    fit = sum(1 for p in parsed if p["date_filled"] and p["evidence"])
    return dict(console_fields=[(a, b.strip()) for a, b in fields],
                console_required=sorted(req_ids),
                ledger_lines=len(parsed), ledger_date_slots_filled=sum(p["date_filled"] for p in parsed),
                ledger_lines_with_evidence=sum(p["evidence"] for p in parsed),
                lines_filing_ready=fit,
                schema_overlap=dict(action=True, date=True, evidence=False, crosswalk=False, question=False),
                samples=[p["raw"] for p in parsed[:4]],
                console_export_claim=re.findall(r"(?i)filed locally[^\"<]*", html)[:2])

# ═══════════════════ C-10 · ⚠ outreach postures × ▤ census language ═══════════════════
POSTURE_MARKERS = {
 "Psychopathic Charmer": ["flatter","charming","irresistible","you of all people","special","exclusive","no strings"],
 "Vulnerable Narcissist": ["only composer who truly understands","uniquely","misunderstood","finally someone","no one else"],
 "Anti-Commercial Ally": ["sell out","industry machine","against the algorithm","not like the others","underground","independent"],
 "Artist-Manipulator": ["visionary","once in a generation","your film deserves","masterpiece","cannot ignore"],
 "Ghost of the Future": ["before you","imagine when","soon everyone","ahead of the curve","next year"],
 "Moral Minimalist": ["harmless","technically","nothing illegal","everyone does it","grey area","victimless"],
}

def beam_c10():
    terms = [m for v in POSTURE_MARKERS.values() for m in v]
    census = "Zazie_Media_Master (1).pdf"
    d = density_rank(terms, census)
    tmpl = load_text("Social Engineering Email Templates .md")
    return dict(postures=len(POSTURE_MARKERS), markers=len(terms),
                markers_sourced_from="Social Engineering Email Templates .md (six annotated postures)",
                template_chars=len(tmpl), rank_test=d,
                control_ranks={p: density_rank(terms, p)["rank"] for p in
                               ["Zazie_Productions_Instagram_Forensic_Audit.pdf",
                                "Personal Branding as Class War Psy-Ops.md",
                                "Social Engineering Email Templates .md", "README.md"]})

# ═══════════════════ C-11 · ▤ release metadata × ⬛/∞ corpus attention ═══════════════════
def beam_c11(n_perm=5000, seed=20260930):
    rows, rel = catalog_csv()
    exclude = {"Zazie_Productions_Discography.csv", "Zazie_Productions_Complete_Discography.xlsx"}
    texts = {p: load_text(p).lower() for p in pool_paths() if p not in exclude}
    recs = []
    for (date, title, rtype), trks in rel.items():
        gaps = sum(t["gap"] for t in trks)
        mentions = sum(t.count(title.lower()) for p, t in texts.items()
                       if os.path.basename(p).lower() != title.lower())
        recs.append(dict(release=title, date=date, type=rtype, tracks=len(trks),
                         gaps=gaps, gap_rate=round(gaps/len(trks), 3),
                         secs=sum(t["secs"] for t in trks), mentions=mentions))
    m = [r["mentions"] for r in recs]
    out = {}
    for key in ("gap_rate", "tracks", "secs"):
        v = [r[key] for r in recs]
        rho = spearman(m, v)
        rng = random.Random(seed); null = []
        for _ in range(n_perm):
            s = v[:]; rng.shuffle(s); null.append(spearman(m, s) or 0.0)
        out[key] = dict(spearman=round(rho, 4) if rho is not None else None,
                        perm_p_two_sided=perm_p(rho, null, two_sided=True))
    return dict(releases=len(recs), records=recs, correlations=out,
                zero_mention_releases=sum(1 for r in recs if r["mentions"] == 0),
                most_mentioned=sorted(recs, key=lambda r: -r["mentions"])[:5])

# ═══════════════════ C-12 · ⬛ knowledge graph × ▤ catalog objects ═══════════════════
def beam_c12():
    g = load_text("🕸 Major Knowledge Graph.md")
    nodes = sorted(set(re.findall(r'\w+\["([^"]+)"\]', g)))
    rows, rel = catalog_csv()
    titles = [r["Track Title"] for r in rows] + [k[1] for k in rel]
    tl = {t.lower() for t in titles}
    nl = {n.lower() for n in nodes}
    exact = sorted(tl & nl)
    partial = sorted({(n, t) for n in nl for t in tl
                      if len(n) > 6 and (n in t or t in n)})
    return dict(graph_nodes=len(nodes), node_sample=nodes[:12],
                catalog_objects=len(titles), exact_matches=exact,
                substring_matches=partial[:12], n_substring=len(partial),
                transfer_rate=round(100*len(exact)/len(nodes), 3))

# ═══════════════════════════ negative-control beam line ═══════════════════════════
RANDOM_BATTERY = {   # NC-3: seven arbitrary documentary features, matched in kind to the
    "has mermaid block": r"```mermaid",          # handbook's seven chain-of-custody elements
    "has emoji": r"[\U0001F300-\U0001FAFF☾◈◉◐▤∞△⚠]",
    "has markdown table": r"^\|.+\|$",
    "has url": r"https?://",
    "has code fence": r"^```",
    "has blockquote": r"^> ",
    "has frontmatter": r"\A---\n",
}

def nc_lexicon_transfers(n_sources=20, n_perm=400, seed=20260930):
    """NC-1 / NC-2: point the C-07 instrument at 20 randomly chosen source artifacts.
    Measures the instrument's own false-positive rate and its self-rank validity rate."""
    inv = [i for i in inventory() if i["stratum"] and not NOT_POOL(i["path"]) and i["chars"] >= 6000]
    rng = random.Random(seed)
    picks = rng.sample([i["path"] for i in inv
                        if i["path"] != "Zazie_Productions_Discography.csv"],
                       min(n_sources, len(inv)-1))
    rows, _ = catalog_csv()
    titles = [r["Track Title"] for r in rows]
    out = []
    for p in picks:
        lex, _ = distinctive_lexicon([p], exclude_paths=["Zazie_Productions_Discography.csv"], top=100)
        if len(lex) < 20:
            out.append(dict(source=p, ok=False, reason="lexicon too small")); continue
        tt = title_transfer(lex, titles, [p], n_perm=n_perm, seed=seed)
        gate, best, n = self_rank_gate([p], lex)
        out.append(dict(source=p, stratum=A.get(p, (None,))[0], ok=True, lexicon=len(lex),
                        observed=tt["observed"], null_mean=tt["null_mean"], p=tt["p"],
                        self_rank=best, gate_passes=gate))
    ok = [o for o in out if o["ok"]]
    return dict(sources_tried=len(out), sources_usable=len(ok), rows=out,
                false_positives_p05=sum(1 for o in ok if o["p"] is not None and o["p"] < 0.05),
                false_positive_rate=round(100*sum(1 for o in ok if o["p"] is not None and o["p"] < 0.05)/max(len(ok),1), 1),
                gate_pass_rate=round(100*sum(1 for o in ok if o["gate_passes"])/max(len(ok),1), 1),
                mean_observed_hits=round(statistics.mean([o["observed"] for o in ok]), 2),
                mean_null_hits=round(statistics.mean([o["null_mean"] for o in ok]), 2))

def nc_random_battery(n_perm=5000, seed=20260930):
    """NC-3: does the handbook's battery find a stratum gap that any battery would find?"""
    rows = []
    for i in inventory():
        if not i["stratum"] or NOT_POOL(i["path"]): continue
        t = load_text(i["path"])
        rows.append(dict(path=i["path"], stratum=i["stratum"],
                         s=sum(bool(re.search(v, t, re.M)) for v in RANDOM_BATTERY.values())))
    ix = [r["s"] for r in rows if r["stratum"] == "INDEX"]
    ev = [r["s"] for r in rows if r["stratum"] == "EVIDENCE"]
    obs = statistics.mean(ix) - statistics.mean(ev)
    pooled = ix + ev; n_ix = len(ix); rng = random.Random(seed); null = []
    for _ in range(n_perm):
        s = pooled[:]; rng.shuffle(s)
        null.append(statistics.mean(s[:n_ix]) - statistics.mean(s[n_ix:]))
    by_stratum = {}
    for s_ in STRATA:
        v = [r["s"] for r in rows if r["stratum"] == s_]
        if v: by_stratum[s_] = round(statistics.mean(v), 2)
    return dict(index_mean=round(statistics.mean(ix), 2), evidence_mean=round(statistics.mean(ev), 2),
                index_minus_evidence=round(obs, 2), perm_p=perm_p(obs, null, greater=True),
                by_stratum=by_stratum,
                reading="if this arbitrary battery also separates INDEX from EVIDENCE, the handbook "
                        "battery is measuring document genre, not governance")

def gates_for(src_paths, lexicon):
    ok, best, n = self_rank_gate(src_paths, lexicon)
    return dict(self_rank=best, n_scored=n, gate_passes=ok)

# ═══════════════════════════ testability topology ═══════════════════════════
def topology(min_distance=2):
    inv = {i["path"]: i for i in inventory()}
    pool = [p for p, i in inv.items() if i["stratum"] and not NOT_POOL(p)]
    pops = [p for p in pool if inv[p]["n_obs"] >= 20]
    lexsrc = [p for p in pool if inv[p]["chars"] >= 3000]
    dated = [p for p in pool if inv[p]["n_dates"] >= 8]
    elig = []
    for a, b in itertools.combinations(sorted(pool), 2):
        ia, ib = inv[a], inv[b]
        if ia["stratum"] == ib["stratum"]: continue
        if DIST[(ia["stratum"], ib["stratum"])] < min_distance: continue
        if vetoed(a, b): continue
        elig.append((a, b))
    cap = [pr for pr in elig if any(c != "S" for c in feasibility(inv[pr[0]], inv[pr[1]]))]
    s_only = [pr for pr in elig if feasibility(inv[pr[0]], inv[pr[1]]) == ["S"]]
    return dict(pool=len(pool), populations=len(pops), population_artifacts=pops,
                lexicon_sources=len(lexsrc), chronologies=len(dated),
                unreplicated=len(pool)-len(pops),
                unreplicated_pct=round(100*(len(pool)-len(pops))/len(pool), 1),
                eligible_pairs=len(elig), beam_capable_pairs=len(cap),
                beam_capable_pct=round(100*len(cap)/len(elig), 2),
                review_required_S_only=len(s_only),
                no_candidate_at_all=len(elig)-len(cap)-len(s_only),
                pairs_requiring_two_populations=sum(
                    1 for a, b in elig if inv[a]["n_obs"] >= 20 and inv[b]["n_obs"] >= 20))

# ═══════════════════════════ beam register (pre-registration) ═══════════════════════════
# Hypothesis, statistic and decision rule were fixed before the beam was run. Verdicts are
# assigned by the rule, not by taste:
#   HOLD  deterministic measurement reproducible from primary files, OR inferential test
#         clearing the family-wise corrected alpha (0.05 / K), AND the result is a quantity
#         or relation absent from both source artifacts, AND a falsifier is stated.
#   SNAP  the beam fired and the null won, or the effect is reproduced by a negative control.
#   NO-BEAM  no measurement survived triage (no shared referent, unreplicated, or the
#         instrument failed its own validity gate).
#   PENDING  the beam is a clock and the window has not closed.
K_TESTS = 13
ALPHA_CORRECTED = 0.05 / K_TESTS

BEAMS = [
 dict(id="C-01", origin="targeted", strata=("EVIDENCE", "SPECIMENS"),
      source="Zazie_Media_Master (1).pdf", target="nuqkL_xKGpmDeDg0PiD0ebgdBeV49y9OVkGSQB-Ka_U.pdf",
      hypothesis="The census's own A/B/C press-kit priority and the specimen's Tier 1/2/3 gate test "
                 "classify the same 133 records differently, and the disagreement is concentrated in "
                 "one identifiable block rather than spread evenly.",
      statistic="Cohen's kappa and Spearman between the two rankings, permutation null (10k shuffles "
                "of tier labels), plus a deterministic decomposition by block and a three-way "
                "sensitivity analysis on the contested block.",
      test_type="inferential + deterministic", fn="beam_c01",
      falsifier="Measure each of the 60 compilation labels' acceptance policy. If they are uniformly "
                "juried (or uniformly open), the hinge disappears and the two rankings converge "
                "without an assumption; kappa should then be stable across all three coding schemes."),
 dict(id="C-02", origin="blind draw 19", strata=("INDEX", "EVIDENCE"),
      source="EVIDENCE_GOVERNANCE_HANDBOOK.md", target="Zazie_Productions_Complete_Discography.xlsx",
      hypothesis="Chain-of-custody compliance falls as an artifact gets closer to raw data: the INDEX "
                 "stratum out-scores the EVIDENCE stratum on the handbook's own seven elements.",
      statistic="Seven-element battery scored over 117 artifacts; permutation test on the INDEX-minus-"
                "EVIDENCE mean; Spearman between citation frequency and custody score; negative control "
                "NC-3 (an arbitrary seven-feature battery).",
      test_type="inferential", fn="beam_c02",
      falsifier="If NC-3's arbitrary battery fails to separate the same two strata, the handbook "
                "battery is measuring governance and the finding stands."),
 dict(id="C-03", origin="blind draw 11", strata=("RECURSION", "EVIDENCE"),
      source="docs/excavation/EXCAVATION_REPORT_ZP-6026.md", target="Zazie_Productions_Complete_Discography.xlsx",
      hypothesis="The excavation report's census numbers are exact where it repeats a number the vault "
                 "already asserted, and wrong where it had to count for itself.",
      statistic="Fifteen claimed quantities re-measured from the file tree, the CSV and the XLSX; "
                "contingency of exactness against 'asserted elsewhere' (context-matched search).",
      test_type="deterministic", fn="beam_c03",
      falsifier="Any self-derived count that measures exact, or any cited count that measures wrong."),
 dict(id="C-04", origin="targeted", strata=("EVIDENCE", "INDEX"),
      source="Zazie_Productions_Discography.csv", target="🗄 Stub Registry.md + the wikilink graph",
      hypothesis="Both recording systems batch their omissions: unresolvable identifiers are "
                 "over-dispersed across units in the same way in the catalog and in the link graph.",
      statistic="Index of dispersion, top-decile gap share and all-gap-unit count in each system, each "
                "against 10k permutations that preserve unit sizes and gap totals.",
      test_type="inferential", fn="beam_c04",
      falsifier="Either system's gaps matching its own null, or the two systems' dispersion indices "
                "falling inside each other's null range."),
 dict(id="C-05", origin="targeted", strata=("RECURSION", "EVIDENCE"),
      source="verdict_from_A.i_5 / _6 (Prediction B)", target="Zazie_Productions_Complete_Discography.xlsx",
      hypothesis="Prediction B's three conditions can each be evaluated from committed artifacts, and "
                 "the falsifier 'track #201' points at a real slot in the catalog's own numbering.",
      statistic="Deterministic evaluation of the three conditions at day 28 of the 30-day window; row-level "
                "inspection of the CATALOG sheet's numbering; dateline-based accretion count for the window.",
      test_type="deterministic", fn="beam_c05",
      falsifier="A committed artifact after 2026-09-02 that fills a ledger line, ships a numbered track, "
                "or publishes a first-person rate."),
 dict(id="C-06", origin="targeted", strata=("IDENTITY", "INDEX"),
      source="6Foundations 2.pdf", target="the vault's prose corpus (109 documents)",
      hypothesis="The corpus's moral-foundation vocabulary enacts the subject's moral-foundation scores: "
                 "Liberty (30/30) should be denser in the prose than Care (8/30).",
      statistic="Density per 10k content words for six transparent lexicons; Spearman against the six "
                "scores; permutation over all 720 lexicon-to-score assignments.",
      test_type="inferential", fn="beam_c06",
      falsifier="rho >= 0.83 at p < 0.05 under the 720-assignment permutation, or the Liberty:Care "
                "density ratio exceeding the 3.75 score ratio."),
 dict(id="C-07", origin="targeted", strata=("MYTHOGRAPHY", "EVIDENCE"),
      source="seven ☾ mythography artifacts", target="Zazie_Productions_Discography.csv (203 objects)",
      hypothesis="The mythography's distinctive vocabulary and proper names appear in track titles above "
                 "the frequency-matched chance rate.",
      statistic="Titles containing >=1 of 100 distinctive ☾ terms, against 2k frequency-matched random "
                "lexicons; twelve proper names checked literally; self-rank validity gate.",
      test_type="inferential", fn="beam_c07",
      falsifier="Any ☾ term or name appearing in a track title; the gate failing (which would void the beam)."),
 dict(id="C-07b", origin="targeted", strata=("all eight", "EVIDENCE"),
      source="each stratum's prose, pooled", target="Zazie_Productions_Discography.csv (182 titles)",
      hypothesis="F-10's claim that the catalog and the vault are 'the same document in two file formats' "
                 "holds at the level of vocabulary, not merely register: each stratum's distinctive "
                 "lexicon should transfer into track titles above chance.",
      statistic="One frequency-matched transfer test per stratum (800 permutations each) plus a "
                "contamination re-run with catalog-quoting documents removed from the source set.",
      test_type="inferential", fn="beam_c07b",
      falsifier="Any stratum whose lexicon transfers at p < 0.05 after catalog-quoting sources are removed."),
 dict(id="C-08", origin="targeted", strata=("SPECIMENS", "EVIDENCE"),
      source="online-presence-pr-seo-scam-vocabulary.pdf (288 defined terms)", target="Zazie_Media_Master (1).pdf",
      hypothesis="The census is written in the mechanism vocabulary the specimen cabinet defines.",
      statistic="Occurrences per 10k words of the 288 terms in every pool artifact; the census's rank "
                "of 112 gives p; self-rank gate on the glossary itself.",
      test_type="inferential", fn="beam_c08",
      falsifier="The census ranking in the top decile of the vault for mechanism-vocabulary density."),
 dict(id="C-09", origin="targeted", strata=("STEWARDSHIP", "RECURSION"),
      source="stewardship_receipt.html", target="verdict_from_A.i_4 (13 stewardship lines)",
      hypothesis="The tribunal's thirteen stewardship lines can be filed in the vault's own receipt "
                 "console without modification.",
      statistic="Field-by-field schema fit: the console's five fields (three required) against the "
                "ledger line format, counted over all thirteen lines.",
      test_type="deterministic", fn="beam_c09",
      falsifier="One committed receipt artifact whose fields are populated from a ledger line, or a "
                "console revision that drops the evidence requirement."),
 dict(id="C-10", origin="targeted", strata=("SPECIMENS", "EVIDENCE"),
      source="Social Engineering Email Templates .md (six postures)", target="Zazie_Media_Master (1).pdf",
      hypothesis="The census's press-facing language carries the six annotated outreach postures above chance.",
      statistic="Thirty-four posture markers, density rank of the census among 112 artifacts, with the "
                "self-rank validity gate applied to the templates themselves.",
      test_type="inferential", fn="beam_c10",
      falsifier="The templates ranking first for their own marker list, which is the precondition for "
                "the beam existing at all."),
 dict(id="C-11", origin="targeted", strata=("EVIDENCE", "INDEX+RECURSION"),
      source="Zazie_Productions_Discography.csv (21 releases)", target="the whole prose corpus (mentions)",
      hypothesis="Releases with weaker identifier coverage receive measurably more (compensation) or "
                 "less (avoidance) vault attention than fully registered releases.",
      statistic="Mentions of each release title across 115 artifacts, Spearman against gap rate, track "
                "count and total duration (n=21, 5k permutations, two-sided).",
      test_type="inferential", fn="beam_c11",
      falsifier="|rho| >= 0.45 at p < 0.05 in either direction."),
 dict(id="C-12", origin="blind draw 4", strata=("INDEX", "EVIDENCE"),
      source="🕸 Major Knowledge Graph.md (77 nodes)", target="Zazie_Productions_Discography.csv (203 objects)",
      hypothesis="The practice graph and the catalog name some of the same objects.",
      statistic="Exact and substring matching between 77 node labels and 203 catalog object names.",
      test_type="deterministic", fn="beam_c12",
      falsifier="Any exact or substring match."),
]

VERDICTS = {
 "C-01": ("HOLD", "", "the hinge: 60 of 133 records decide whether the two rankings agree at chance "
          "(kappa 0.002) or moderately (kappa 0.507)"),
 "C-02": ("SNAP", "F5 genre confound", "the arbitrary battery NC-3 separates the same two strata more "
          "strongly (p=0.0015) than the handbook battery (p=0.049); citation-vs-custody rho=0.02"),
 "C-03": ("SNAP", "F7 null wins", "8 of 15 counts wrong, but wrongness is unrelated to citation "
          "(86% vs 88%); the hypothesis dies and a defect list survives"),
 "C-04": ("SNAP", "F7 null wins", "opposite geometries: catalog gaps batched (p=0.003), link gaps "
          "anti-batched at unit level (p=1.0)"),
 "C-05": ("HOLD", "", "the falsifier's referent is broken: the last real track is #197, so '#201' is "
          "four releases away, not one"),
 "C-06": ("SNAP", "F7 null wins", "rho=0.54, p=0.13; the pre-registered contrast inverts (Care densest)"),
 "C-07": ("SNAP", "F7 null wins", "0 of 203 objects, 0 of 12 proper names, p=1.0 against a "
          "frequency-matched null"),
 "C-07b": ("SNAP", "F7 null wins", "zero genuine transfer from any of the eight strata; the single "
          "apparent hit is reproduced entirely by documents that already quote the catalog"),
 "C-08": ("SNAP", "F7 null wins", "rank 61 of 112, p=0.54; 4 of 288 terms present"),
 "C-09": ("HOLD", "", "0 of 13 lines filable: the console requires the one field the ledger format never emits"),
 "C-10": ("NO-BEAM", "F9 instrument invalid", "the templates rank 10th of 112 for their own markers, "
          "below the census at 8th: the markers measure promotional register, not posture"),
 "C-11": ("SNAP", "F7 null wins", "all |rho| <= 0.11, p >= 0.65 in both directions"),
 "C-12": ("SNAP", "F7 null wins", "0 exact and 0 substring matches across 77 x 203 name pairs"),
}

def run_beams():
    out = {}
    for b in BEAMS:
        fn = globals()[b["fn"]]
        res = fn() if b["id"] != "C-07b" else fn()
        v, fc, note = VERDICTS[b["id"]]
        out[b["id"]] = dict(**{k: b[k] for k in ("id", "origin", "strata", "source", "target",
                                                 "hypothesis", "statistic", "test_type", "falsifier")},
                            verdict=v, failure_class=fc, verdict_note=note,
                            clears_corrected_alpha=(v == "HOLD"), result=res)
    return out

def main(n_perm=4000, draw_n=24, seed=20260930, figure=True):
    import sys, platform
    log = dict(
        report="ZP-PC-2026-0930", tool="tools/particle_collider.py",
        run_date=datetime.date.today().isoformat(), seed=seed,
        python=platform.python_version(), argv=sys.argv[1:],
        alpha=0.05, alpha_family_wise=round(ALPHA_CORRECTED, 5), k_tests=K_TESTS,
        strata={k: dict(chip=v["chip"], glyph=v["glyph"], hex=v["hex"], name=v["name"])
                for k, v in STRATA.items()},
        distance_matrix={f"{a}->{b}": DIST[(a, b)] for a in STRATA for b in STRATA},
        topology=topology(), draw=draw(draw_n, seed), beams=run_beams(),
        negative_controls=dict(nc1_lexicon_transfers=nc_lexicon_transfers(n_sources=20, n_perm=400, seed=seed),
                               nc3_random_battery=nc_random_battery(n_perm=4000, seed=seed)),
        draw_dispositions={str(k): v for k, v in DRAW_DISPOSITIONS.items()},
        veto_register={k: v for k, v in VETO_GROUPS.items()},
        artifact_inventory=inventory(),
    )
    promoted = [r["draw"] for r in log["draw"]["draws"] if r["beam_classes"]]
    assert sorted(promoted) == sorted(int(k) for k in log["draw_dispositions"]), "dispositions must cover every promoted draw"
    for k, v in log["draw_dispositions"].items():
        if v["beam"]: assert v["beam"] in log["beams"], v["beam"]
    tally = collections.Counter(b["verdict"] for b in log["beams"].values())
    log["tally"] = dict(tally)
    os.makedirs("docs/collider", exist_ok=True)
    with open("docs/collider/beam_log.json", "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=1, ensure_ascii=False, default=str)
    print(f"PARTICLE COLLIDER · {log['run_date']} · seed {seed} · alpha {ALPHA_CORRECTED:.4f} (0.05/{K_TESTS})")
    print(f"  pool {log['topology']['pool']} artifacts · eligible distant pairs {log['topology']['eligible_pairs']}"
          f" · beam-capable {log['topology']['beam_capable_pairs']} ({log['topology']['beam_capable_pct']}%)")
    print(f"  unreplicated artifacts: {log['topology']['unreplicated']} of {log['topology']['pool']}"
          f" ({log['topology']['unreplicated_pct']}%)")
    print(f"  blind draw: {draw_n} pairs -> promoted "
          f"{sum(1 for d in log['draw']['draws'] if d['beam_classes'])} beam-capable")
    print("  verdicts:", dict(tally))
    for bid, b in log["beams"].items():
        print(f"    {bid:<6} {b['verdict']:<8} {b['strata'][0]} x {b['strata'][1]:<12} {b['verdict_note'][:78]}")
    print("  wrote docs/collider/beam_log.json")
    if figure:
        try:
            render_figure(log)
            print("  wrote docs/figures/fig8_beamline.png")
        except Exception as e:
            print("  figure skipped:", e)
    return log

# ═══════════════════════════ FIG 8 · the beam line ═══════════════════════════
import unicodedata as _ud

def _disp(s, n=34):
    """artifact names carry emoji the bundled font lacks; strip pictographs, trim"""
    s = "".join(c for c in s if _ud.category(c) not in ("So", "Sk", "Cn", "Cs")
                and c not in "\u200d\ufe0f").strip()
    s = os.path.splitext(s)[0] if s.lower().endswith((".md", ".pdf", ".csv", ".xlsx",
                                                      ".json", ".txt", ".py", ".svg", ".png")) else s
    return s if len(s) <= n else s[:n - 1] + "…"

def _wrap(txt, width):
    out, cur = [], ""
    for w in txt.split():
        if len(cur) + len(w) + 1 > width:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out

def render_figure(log):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    C = {k: v["hex"] for k, v in STRATA.items()}
    INK, GRID, PAPER, DIM = "#231F20", "#C4BFB5", "#FFFFFF", "#55504A"
    plt.rcParams.update({"figure.facecolor": PAPER, "axes.facecolor": PAPER,
                         "savefig.facecolor": PAPER, "font.family": "DejaVu Sans",
                         "axes.edgecolor": INK, "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": INK, "ytick.color": INK})
    fig = plt.figure(figsize=(16.0, 10.2), dpi=150)
    gs = fig.add_gridspec(2, 3, width_ratios=[0.92, 1.72, 0.86], height_ratios=[1, 1],
                          left=0.042, right=0.986, top=0.855, bottom=0.055,
                          wspace=0.26, hspace=0.30)
    fig.text(0.042, 0.965, "FIG 8 · THE BEAM LINE — cross-stratum collisions, triage and verdicts",
             fontsize=16, fontweight="bold", ha="left", va="center")
    fig.text(0.042, 0.925, "ZP-PC-2026-0930 · seed 20260930 · every count re-derived from primary files · "
                           "α = 0.05/13 = 0.0038 · chip colour = stratum (README §00a), never verdict",
             fontsize=8.8, color=DIM, ha="left", va="center")

    # ── panel A · the funnel ──
    ax = fig.add_subplot(gs[:, 0])
    t, d = log["topology"], log["draw"]
    all_pairs = t["pool"] * (t["pool"] - 1) // 2
    n_prom = sum(1 for r in d["draws"] if r["verdict"] == "TRIAGED")
    steps = [("artifact pairs in the pool", all_pairs, INK),
             ("… in different strata", all_pairs - d["veto"]["same stratum"], "#4E4842"),
             ("… analytically distant (d ≥ 2)", t["eligible_pairs"] + d["veto"]["already analyzed together"], "#6E675F"),
             ("… never analyzed together", t["eligible_pairs"], "#8E877E"),
             ("beam-capable (T / L / C class)", t["beam_capable_pairs"], C["EVIDENCE"]),
             ("blind draws taken", d["n_draws"], C["RECURSION"]),
             ("draws promoted to beams", n_prom, C["STEWARDSHIP"]),
             ("beams fired (incl. targeted)", len(log["beams"]), C["MYTHOGRAPHY"]),
             ("HOLD — a new, tested relation", log["tally"].get("HOLD", 0), C["IDENTITY"])]
    n = len(steps)
    for k, (label, val, col) in enumerate(steps):
        yi = n - 1 - k
        w = max(val / all_pairs, 0.006)
        ax.add_patch(Rectangle((0, yi - 0.20), w, 0.40, facecolor=col, edgecolor=INK, linewidth=0.7))
        ax.text(w + 0.015, yi, f"{val:,}", va="center", fontsize=9.6, fontweight="bold")
        ax.text(0, yi + 0.34, label, va="center", fontsize=8.4, color="#3A342C")
    ax.set_xlim(0, 1.16); ax.set_ylim(-1.35, n - 0.35)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "25%", "50%", "75%", "100%"], fontsize=8)
    ax.set_yticks([]); ax.grid(axis="x", color=GRID, linewidth=0.5, alpha=0.6)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.set_title("A · the funnel — how much of the vault is collidable", fontsize=10.5,
                 fontweight="bold", loc="left", pad=8)
    ax.text(0, -1.05, f"{t['unreplicated']} of {t['pool']} pool artifacts carry one observation only "
                      f"({t['unreplicated_pct']}%).\nOnly {t['pairs_requiring_two_populations']} eligible pairs "
                      "put a population on both sides.", fontsize=8.2, color=DIM, va="top")

    # ── panel B · the beam ladder ──
    ax = fig.add_subplot(gs[:, 1]); ax.set_axis_off()
    beams = list(log["beams"].values()); nb = len(beams)
    top, bot = 0.965, 0.045
    ax.text(0.0, 1.005, "B · thirteen beams: what was crossed, and what came back",
            fontsize=10.5, fontweight="bold", transform=ax.transAxes, va="bottom")
    for label, x in (("BEAM", 0.0), ("CROSSED", 0.058), ("VERDICT", 0.360), ("WHAT THE NULL SAID", 0.470)):
        ax.text(x, top + 0.008, label, fontsize=8.0, fontweight="bold", color=DIM,
                transform=ax.transAxes, va="bottom")
    GLYPH_MARK = {"HOLD": "✓", "SNAP": "✗", "NO-BEAM": "⊘", "PENDING": "◷"}
    WHITE_ON = (C["INDEX"], C["IDENTITY"], C["RECURSION"], C["SPECIMENS"])
    for i, b in enumerate(beams):
        yv = top - (i + 0.5) * (top - bot) / nb
        ka = b["strata"][0].split("+")[0].strip().upper()
        kb = b["strata"][1].split("+")[0].strip().upper()
        ca, cb = C.get(ka, INK), C.get(kb, INK)
        ga = STRATA.get(ka, {}).get("glyph", "◇"); gb = STRATA.get(kb, {}).get("glyph", "◇")
        ax.add_patch(Rectangle((0.055, yv - 0.014), 0.017, 0.028, facecolor=ca, edgecolor=INK,
                               linewidth=0.6, transform=ax.transAxes))
        ax.text(0.0635, yv, ga, ha="center", va="center", fontsize=8.0, transform=ax.transAxes,
                color="white" if ca in WHITE_ON else INK)
        ax.annotate("", xy=(0.112, yv), xytext=(0.078, yv), xycoords=ax.transAxes,
                    textcoords=ax.transAxes,
                    arrowprops=dict(arrowstyle="-|>", color="#6A635A", lw=1.0,
                                    linestyle=(0, (3, 2)) if b["verdict"] == "NO-BEAM" else "solid"))
        ax.add_patch(Rectangle((0.115, yv - 0.014), 0.017, 0.028, facecolor=cb, edgecolor=INK,
                               linewidth=0.6, transform=ax.transAxes))
        ax.text(0.1235, yv, gb, ha="center", va="center", fontsize=8.0, transform=ax.transAxes,
                color="white" if cb in WHITE_ON else INK)
        ax.text(0.0, yv, b["id"], fontsize=9.2, fontweight="bold", va="center", transform=ax.transAxes)
        ax.text(0.140, yv + 0.009, _disp(b["source"], 26), fontsize=6.9, va="center", transform=ax.transAxes)
        ax.text(0.140, yv - 0.012, _disp(b["target"], 26), fontsize=6.9, va="center", color=DIM,
                transform=ax.transAxes)
        v = b["verdict"]
        ax.text(0.360, yv + 0.006, f"{GLYPH_MARK[v]} {v}", fontsize=9.2, va="center",
                fontweight="bold", transform=ax.transAxes)
        sub = b["failure_class"] or ("survives α = 0.0038" if v == "HOLD" else "")
        ax.text(0.360, yv - 0.015, sub, fontsize=6.6, va="center", color="#7A736A", transform=ax.transAxes)
        for k, ln in enumerate(_wrap(b["verdict_note"], 62)[:3]):
            ax.text(0.470, yv + 0.013 - k * 0.0185, ln, fontsize=7.1, va="center",
                    color="#2A251F", transform=ax.transAxes)
        ax.plot([0.0, 0.995], [yv - 0.030, yv - 0.030], color=GRID, lw=0.5, alpha=0.8,
                transform=ax.transAxes)
    ax.text(0.0, bot - 0.045, "3 HOLD · 9 SNAP · 1 NO-BEAM — the failure rate is the result.  "
            "Chip colours are strata (README §00a); verdicts ride on glyph and label.",
            fontsize=8.2, color=DIM, transform=ax.transAxes, va="top")

    # ── panel C · negative controls as cards ──
    ax = fig.add_subplot(gs[0, 2]); ax.set_axis_off()
    ax.text(0.0, 1.005, "C · the instrument, tested on itself", fontsize=10.5, fontweight="bold",
            transform=ax.transAxes, va="bottom")
    nc1 = log["negative_controls"]["nc1_lexicon_transfers"]
    nc3 = log["negative_controls"]["nc3_random_battery"]
    p_hand = log["beams"]["C-02"]["result"]["index_vs_evidence_perm_p"]
    n_fp, n_src = nc1["false_positives_p05"], nc1["sources_usable"] - 1
    cards = [(f"{n_fp} / {n_src} false positives", C["RECURSION"],
              "NC-1 · the lexicon-transfer beam re-aimed at 19 documents of known "
              "provenance. Only the degenerate self-source matched itself; excluding "
              "it, the instrument never invents a transfer."),
             (f"{nc1['sources_usable']} / {nc1['sources_usable']} gates pass", C["IDENTITY"],
              "NC-2 · TF-built lexicons always rank their own source first (circular by "
              "construction), so the self-rank gate only bites hand-authored marker "
              "lists — and it did bite: it killed C-10."),
             (f"p = {nc3['perm_p']:.4f}  vs  {p_hand:.3f}", C["SPECIMENS"],
              "NC-3 · an arbitrary 7-feature battery separates INDEX from EVIDENCE more "
              "strongly than the handbook battery does. C-02's signal is document "
              "genre, not governance.")]
    yy = 0.93
    for big, col, txt in cards:
        ax.add_patch(Rectangle((0.0, yy - 0.245), 0.035, 0.245, facecolor=col, edgecolor=INK,
                               linewidth=0.6, transform=ax.transAxes))
        ax.text(0.06, yy - 0.035, big, fontsize=10.5, fontweight="bold", transform=ax.transAxes, va="top")
        for k, ln in enumerate(_wrap(txt, 46)):
            ax.text(0.06, yy - 0.105 - k * 0.055, ln, fontsize=7.0, color="#3A342C",
                    transform=ax.transAxes, va="top")
        yy -= 0.335

    # ── panel D · legend ──
    ax = fig.add_subplot(gs[1, 2]); ax.set_axis_off()
    ax.text(0.0, 1.005, "D · reading the verdicts", fontsize=10.5, fontweight="bold",
            transform=ax.transAxes, va="bottom")
    legend = [("✓ HOLD", "a quantity or relation present in neither source alone, "
               "reproducible from primary files, with a stated falsifier"),
              ("✗ SNAP", "the beam fired and the null won — or a negative control "
               "reproduced the effect from something arbitrary"),
              ("⊘ NO-BEAM", "nothing survived triage: no shared referent, an "
               "unreplicated source, or the instrument failed its own validity gate"),
              ("◷ PENDING", "the beam is a clock and its window has not closed yet")]
    yy = 0.90
    for mark, txt in legend:
        ax.text(0.0, yy, mark, fontsize=9.4, fontweight="bold", transform=ax.transAxes, va="top")
        lines = _wrap(txt, 37)
        for k, ln in enumerate(lines):
            ax.text(0.245, yy - k * 0.062, ln, fontsize=7.2, color="#3A342C",
                    transform=ax.transAxes, va="top")
        yy -= 0.062 * max(len(lines), 1) + 0.055
    ax.text(0.0, 0.02, "regenerate:  python3 tools/particle_collider.py\n"
            "log:  docs/collider/beam_log.json", fontsize=7.4, color="#7A736A",
            transform=ax.transAxes, va="bottom")
    out = os.path.join(ROOT, "docs", "figures", "fig8_beamline.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out

if __name__ == "__main__":
    main(figure="--no-figure" not in sys.argv)
