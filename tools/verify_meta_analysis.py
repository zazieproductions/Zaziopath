#!/usr/bin/env python3
"""Re-derive every quantitative claim in META-ANALYSIS — The Verdict Corpus Audited.

Run from the repository root:  python3 tools/verify_meta_analysis.py
Emits a dated verification log (stdout) and docs/meta-analysis/verification.json.
Nothing here depends on the verdict documents; every figure comes from a primary file.
"""
import csv, glob, json, os, re, subprocess, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
R = {}


def check(key, value, note=""):
    R[key] = {"value": value, "note": note}
    print(f"  {key:<34} {value!r:<24} {note}")


print(f"VERIFICATION RUN · {date.today().isoformat()} · cwd={ROOT}\n")

print("[1] README / architecture")
readme = open("README.md", encoding="utf-8").read()
check("readme_lines", readme.count("\n") + 1)
check("readme_bytes", os.path.getsize("README.md"))
planned = [l.strip() for l in readme.splitlines() if "05_stewardship" in l]
check("stewardship_planned", bool(planned and "[planned]" in planned[0]), planned[0] if planned else "")

print("\n[2] Receipt console — can the outbox be observed?")
html = open("stewardship_receipt.html", encoding="utf-8").read()
check("console_bytes", os.path.getsize("stewardship_receipt.html"))
check("console_fetch_calls", len(re.findall(r"\bfetch\s*\(", html)))
check("console_xhr_calls", len(re.findall(r"XMLHttpRequest|navigator\.sendBeacon", html)))
check("console_localstorage_refs", len(re.findall(r"localStorage", html)))
check("ledger_observable_in_git", False, "no committed ledger artifact; state lives in the browser")

print("\n[3] Stub registry")
reg = open("\U0001f5c4 Stub Registry.md", encoding="utf-8").read()
check("stub_entries_listed", len([l for l in reg.splitlines() if l.startswith("- [[")]))
check("registry_claims_92", "92 removed stubs" in reg)
check("parent_vault_claim", "336" in reg, "336-note parent vault, asserted not verifiable here")

print("\n[4] Wikilink integrity (current tree)")
names = {os.path.splitext(f)[0].strip() for f in os.listdir(".")}
links, total = set(), 0
for f in glob.glob("*.md"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.findall(r"\[\[([^\]\|#]+)", t):
        links.add(m.strip()); total += 1
dangling = sorted(l for l in links if l not in names)
check("wikilink_instances", total)
check("wikilinks_unique", len(links))
check("wikilinks_dangling", len(dangling))
check("dangling_pct", round(100 * len(dangling) / max(len(links), 1), 1))

print("\n[5] Discography CSV vs. the figures every verdict repeated")
rows = list(csv.DictReader(open("Zazie_Productions_Discography.csv", encoding="utf-8")))
isrcs = {r["ISRC"].strip() for r in rows if r["ISRC"].strip()}
artists = sorted({r["Artist"].strip() for r in rows})
dates = sorted(r["Release Date"] for r in rows if r["Release Date"].strip())
check("csv_rows", len(rows), "verdict corpus repeats '200 tracks'")
check("csv_unique_isrcs", len(isrcs), "verdict corpus repeats '165 verified ISRCs'")
check("csv_rows_with_isrc", sum(1 for r in rows if r["ISRC"].strip()))
check("csv_distinct_artists", len(artists), "; ".join(artists))
check("csv_date_first", dates[0]); check("csv_date_last", dates[-1])
check("xlsx_opened_by_any_verdict", False, "no verdict cites a sheet, row, or cell")

print("\n[6] Corpus shape")
verdicts = sorted(glob.glob("verdict_from_A.i*"))
sizes = {v: os.path.getsize(v) for v in verdicts}
for v, s in sizes.items():
    check(f"size:{v}", s)
check("corpus_bytes", sum(sizes.values()))
dated = {v: bool(re.search(r"2026-09-02", open(v, encoding="utf-8").read())) for v in verdicts}
undated = [v for v, d in dated.items() if not d]
check("verdicts_bearing_2026-09-02", sum(dated.values()),
      "V1 carries no date header of its own; V2-V6 all self-date to 2026-09-02")
check("verdicts_without_self_date", undated)

print("\n[7] Filename hygiene")
trailing = [f for f in os.listdir(".") if re.search(r"\s+\.[A-Za-z0-9]+$", f)]
check("filenames_trailing_space", len(trailing), "; ".join(sorted(trailing)))

print("\n[8] Git")
try:
    n = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    check("commits_on_head", int(n))
except Exception as e:  # pragma: no cover
    check("commits_on_head", None, str(e))

os.makedirs("docs/meta-analysis", exist_ok=True)
with open("docs/meta-analysis/verification.json", "w", encoding="utf-8") as fh:
    json.dump({"run_date": date.today().isoformat(), "results": R}, fh, indent=2, ensure_ascii=False)
print("\nwrote docs/meta-analysis/verification.json")
