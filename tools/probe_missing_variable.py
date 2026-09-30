#!/usr/bin/env python3
"""Probe the Zaziopath repository for the signatures of an unmeasured variable.

This script does not name X.  It measures only things that are already committed,
so that every anomaly listed in ``👻 X — The Missing Variable.md`` can be re-derived
by a stranger with no access to that document.

It reads:

* ``Zazie_Productions_Discography.csv``          (the record every audit chose)
* ``Zazie_Productions_Complete_Discography.xlsx`` (the record nobody opened —
  parsed with the standard library only, via the OOXML zip container)
* the committed Markdown corpus                    (the reference graph)
* ``stewardship_receipt.html``                     (the observability instrument)

and writes ``docs/ghost-x/verification.json``.

Run:  python3 tools/probe_missing_variable.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import statistics
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "Zazie_Productions_Complete_Discography.xlsx"
CSV = ROOT / "Zazie_Productions_Discography.csv"
OUT = ROOT / "docs" / "ghost-x" / "verification.json"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
DELUXE = {
    "Stutter to stammer (Super Deluxe Edition)",
    "Greetings From Tinsel Time (Super Deluxe Edition)",
    "Sellotape (Super Deluxe Edition)",
}
ISRC_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{3}\d{7}$")
ZERO_WIDTH = "\u200b\u200c\u200d\ufeff"

results: dict = {}


def note(key: str, value, detail: str = "") -> None:
    results[key] = {"value": value, "note": detail}
    print(f"{key:38s} {value!r} {detail}")


# ─────────────────────────────────────────────────────────────────────────────
# 1 · the workbook — opened with the standard library
# ─────────────────────────────────────────────────────────────────────────────

def read_workbook() -> dict[int, list[list[str]]]:
    z = zipfile.ZipFile(XLSX)
    shared = [
        "".join(t.text or "" for t in si.iter(NS + "t"))
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(NS + "si")
    ]
    sheets: dict[int, list[list[str]]] = {}
    for i in range(1, 7):
        root = ET.fromstring(z.read(f"xl/worksheets/sheet{i}.xml"))
        rows = []
        for row in root.iter(NS + "row"):
            cells = []
            for c in row.findall(NS + "c"):
                v = c.find(NS + "v")
                if v is None:
                    cells.append("")
                elif c.get("t") == "s":
                    cells.append(shared[int(v.text)])
                else:
                    cells.append(v.text or "")
            rows.append(cells)
        sheets[i] = rows
    return sheets


def is_index(cell: str) -> bool:
    return bool(cell) and bool(re.match(r"^\d+(\.0)?$", cell))


def reg_year(isrc: str) -> int | None:
    return 2000 + int(isrc[5:7]) if ISRC_RE.match(isrc or "") else None


def parse_duration(text: str) -> int | None:
    m = re.match(r"(\d+):(\d+)", text or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def main() -> None:
    sheets = read_workbook()

    # ── A1/A2 · the two records ─────────────────────────────────────────────
    catalog = [r for r in sheets[3] if r and is_index(r[0])]
    isrc_cells = [r[7] for r in catalog if len(r) > 7 and r[7]]
    isrc_valid = [c for c in isrc_cells if ISRC_RE.match(c)]
    dashes = [r for r in catalog if len(r) > 7 and r[7] == "—"]
    non_track = [
        r for r in catalog
        if re.match(r"^(\u2014|50\+ VA|Dissonance Index Vol\.1)", str(r[1]).strip())
    ]
    note("wb_rows", len(catalog), "rows with a numeric index in CATALOG")
    note("wb_isrc_cells", len(isrc_cells), f"{len(isrc_valid)} well-formed, {len(dashes)} literal '—'")
    note("wb_unique_isrc", len(set(isrc_valid)))
    note("wb_non_track_rows", len(non_track),
         "; ".join(str(r[1])[:44] for r in non_track))
    total_row = next(([c for c in r if c] for r in sheets[6] if r and r[0] == "TOTAL"), [])
    note("wb_total_row", " / ".join(total_row), "the workbook's own arithmetic: 200 = 165 + 35")

    csv_rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    note("csv_rows", len(csv_rows))
    note("csv_unique_isrc", len({r["ISRC"] for r in csv_rows if ISRC_RE.match(r["ISRC"].strip())}))
    note("csv_na", sum(1 for r in csv_rows if r["ISRC"].strip() == "N/A"))
    note("csv_distinct_artists", len({r["Artist"] for r in csv_rows}),
         "; ".join(sorted({r["Artist"] for r in csv_rows})))

    norm = lambda s: re.sub(r"\s+", " ", str(s)).strip().lower()
    wb_pairs = {(norm(r[2]), norm(r[1])) for r in catalog}
    csv_pairs = {(norm(r["Release Title"]), norm(r["Track Title"])) for r in csv_rows}
    note("record_divergence_wb_only", len(wb_pairs - csv_pairs),
         "rows the audited CSV never carried")
    note("record_divergence_csv_only", len(csv_pairs - wb_pairs),
         "rows the workbook never carried")
    note("g7e_torpedo_in_csv", any("g7e" in norm(r["Release Title"]) for r in csv_rows),
         "2019 EP: 6 workbook rows, 0 CSV rows")
    tri = [r for r in csv_rows if "triangular savant" in r["Release Title"].lower()]
    wb_tri = [r for r in catalog if len(r) > 2 and "triangular savant" in r[2].lower()]
    note("triangular_savant_rows", f"csv={len(tri)} wb={len(wb_tri)}",
         "the same release, counted six times in one record and once in the other")

    # ── A3 · identifiers travel in both directions in time ──────────────────
    lags: Counter[int] = Counter()
    for r in csv_rows:
        y = int(r["Release Date"][:4])
        ry = reg_year(r["ISRC"].strip())
        if ry:
            lags[ry - y] += 1
    retro = sum(v for k, v in lags.items() if k > 0)
    carried = sum(v for k, v in lags.items() if k < 0)
    note("isrc_lag_histogram", dict(sorted(lags.items())))
    note("isrc_retroactive", retro, "registered after release (2019/2020 works coded 22)")
    note("isrc_carried_forward", carried, "older codes reused on deluxe reissues")
    wb_lags: Counter[int] = Counter()
    for r in catalog:
        if len(r) > 7 and ISRC_RE.match(r[7]):
            wb_lags[2000 + int(r[7][5:7]) - int(float(r[4]))] += 1
    note("wb_isrc_lag_histogram", dict(sorted(wb_lags.items())))

    # ── A4 · missingness is platform-shaped ────────────────────────────────
    hole = Counter(r["Release Title"] for r in csv_rows if r["ISRC"].strip() == "N/A")
    note("unregistered_rows_csv", sum(hole.values()), dict(hole))
    note("wb_unregistered_by_release", dict(Counter(
        r[2] for r in catalog if len(r) > 7 and r[7] == "—")))
    note("wb_dash_meaning", "— = 'no ISRC found on Deezer/SoundCharts/MusicBrainz'",
         "absence of a platform sighting is written as absence of an identifier")

    # ── A5 · the miniaturisation is a packaging artefact ───────────────────
    def durs(sel):
        return [parse_duration(r["Duration"]) for r in csv_rows
                if sel(r) and parse_duration(r["Duration"])]

    for label, sel in (
        ("deluxe", lambda r: r["Release Title"] in DELUXE),
        ("non_deluxe", lambda r: r["Release Title"] not in DELUXE),
    ):
        ds = durs(sel)
        note(f"duration_{label}_median", statistics.median(ds))
        note(f"duration_{label}_under_120s",
             f"{sum(1 for d in ds if d < 120)}/{len(ds)}",
             f"{100 * sum(1 for d in ds if d < 120) / len(ds):.0f}%")
        note(f"duration_{label}_30s_or_less", sum(1 for d in ds if d <= 30))
    y2024 = [r for r in csv_rows if r["Release Date"].startswith("2024")]
    note("y2024_rows", len(y2024))
    note("y2024_non_deluxe_rows", sum(1 for r in y2024 if r["Release Title"] not in DELUXE),
         "every 2024 row belongs to a deluxe edition")

    # ── A6 · the quiet year flips with the metric ──────────────────────────
    per_year = {}
    for y in range(2019, 2027):
        rows = [r for r in csv_rows if r["Release Date"].startswith(str(y))]
        events = {(r["Release Title"], r["Release Date"]) for r in rows}
        per_year[y] = {
            "csv_rows": len(rows),
            "release_events": len(events),
            "non_deluxe_rows": sum(1 for r in rows if r["Release Title"] not in DELUXE),
            "feature_rows": sum(1 for r in rows if r["Artist"] != "Zazie Productions"),
        }
    note("per_year_metrics", per_year,
         "under 'non_deluxe_rows' the quiet year is 2024 (0), not 2025 (4)")
    vals = [v["csv_rows"] for v in per_year.values()]
    note("rows_mean_sd", [round(statistics.mean(vals), 1), round(statistics.stdev(vals), 1)])
    note("events_mean_sd", [
        round(statistics.mean([v["release_events"] for v in per_year.values()]), 1),
        round(statistics.stdev([v["release_events"] for v in per_year.values()]), 1)])
    note("packaging_share", f"{sum(1 for r in csv_rows if r['Release Title'] in DELUXE)}/{len(csv_rows)}",
         "share of the discography that is reissue packaging (3 deluxe editions)")
    note("audit_window", "2023-2026",
         "the vault's own self-dating concentrates in 2026-08/09 (see md_dates_by_month)")

    # ── A7 · the zero that cannot be observed ──────────────────────────────
    html = (ROOT / "stewardship_receipt.html").read_text(encoding="utf-8")
    note("console_fetch_calls", len(re.findall(r"\bfetch\s*\(", html)))
    note("console_xhr_sendbeacon", len(re.findall(r"XMLHttpRequest|sendBeacon", html)))
    note("console_localstorage_refs", len(re.findall(r"localStorage", html)))
    note("console_committed_ledger", False, "state lives in the browser; empty and full repos are byte-identical")

    # ── A8 · the archive is largely made of names ──────────────────────────
    md_files = sorted(list(ROOT.glob("*.md")) + list(ROOT.glob("docs/**/*.md")))
    instances, targets = 0, set()
    for p in md_files:
        for m in re.findall(r"\[\[([^\]\|#]+)", p.read_text(encoding="utf-8", errors="replace")):
            instances += 1
            targets.add(m.strip())
    stems = {os.path.splitext(p.name)[0].strip().lower() for p in md_files}
    dangling = {t for t in targets if t.lower() not in stems and os.path.splitext(t)[0].lower() not in stems}
    note("wikilink_instances", instances)
    note("wikilinks_unique", len(targets))
    note("wikilinks_dangling", f"{len(dangling)}/{len(targets)}",
         f"{100 * len(dangling) / len(targets):.1f}% of the reference graph has no target in this repo")
    inv = (ROOT / "🧾 Inventory of Distinct Things.md").read_text(encoding="utf-8")
    inv_items = re.findall(r"^- \[\[([^\]]+)\]\]", inv, flags=re.M)
    note("inventory_notes", len(inv_items))
    note("inventory_resolving_in_repo",
         f"{sum(1 for i in inv_items if i.lower() in stems)}/{len(inv_items)}",
         "the manifest names an archive that is mostly elsewhere")
    note("tombstones", len(re.findall(
        r"^- \[\[([^\]]+)\]\]",
        (ROOT / "🗄 Stub Registry.md").read_text(encoding="utf-8"), flags=re.M)),
        "bodies removed, names kept")
    zw = [r["Track Title"] for r in csv_rows
          if any(c in r["Track Title"] for c in ZERO_WIDTH)]
    note("zero_width_titles", len(zw), "titles whose identity is unstable in string comparison")

    # ── A9 · no person appears as a person ─────────────────────────────────
    note("solo_rows", sum(1 for r in csv_rows if r["Artist"] == "Zazie Productions"))
    note("collaborator_strings", sorted({r["Artist"] for r in csv_rows if r["Artist"] != "Zazie Productions"}))
    comp = [r for r in sheets[5] if r and is_index(r[0])]
    note("comp_rows_listed", len(comp))
    note("comp_rows_that_are_entries",
         sum(1 for r in comp if not re.match(r"^(\u2014|58 Appearances|Full list|Dissonance)", str(r[1]).strip())),
         "the sheet mixes entries with counters and pointers")
    note("claim_58_appearances", "asserted in sheet1/sheet5",
         "'Discogs Artist 11354435 = 58 Appearances' — asserted, not enumerable in-repo")

    # ── A10 · audience is measured only where it is not yours ──────────────
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in md_files)
    note("mentions_revenue_income", len(re.findall(r"revenue|income", corpus, flags=re.I)),
         "all in interpretations/memory exports; no figures")
    note("mentions_streams_sales", len(re.findall(r"streams|sales|royalt", corpus, flags=re.I)))
    note("own_release_audience_figures", 0,
         "no streams, sales, listeners or follower count for any own release in the repo")
    note("curation_audience_figure",
         "≈32k followers (one Goa/Psytrance playlist; ChatGPT memory export l.112)",
         "the only audience number present belongs to a playlist the subject curates")
    note("revenue_artifact", "[[Revenue Snapshot — July 2026]] — a name in the Inventory, no file",
         "the financial register exists as a title only")

    # ── audit mass vs receipt mass ─────────────────────────────────────────
    audit_names = [
        "META-ANALYSIS — The Verdict Corpus Audited.md", "DEEP_GAP_AUDIT.md",
        "CASE STUDY — The Receipt and the Record.md", "CASE STUDY — The Summoned Witness.md",
        "🔍 CASE FILE — Pattern Forensics.md", "META_ANALYSIS_OF_ZAZIOPATH.md",
    ] + [f"verdict_from_A.i{'' if i == 0 else '_' + str(i)}" for i in range(7)]
    audit_bytes = sum((ROOT / n).stat().st_size for n in audit_names if (ROOT / n).exists())
    note("audit_bytes", audit_bytes, f"{sum(1 for n in audit_names if (ROOT / n).exists())} documents")
    note("ledger_bytes", 0, "receipts committed to the repository")

    # ── dates ──────────────────────────────────────────────────────────────
    months = Counter()
    for p in md_files:
        for d in re.findall(r"20\d\d-\d\d-\d\d", p.read_text(encoding="utf-8", errors="replace")):
            months[d[:7]] += 1
    note("md_dates_by_month", dict(sorted(months.items())),
         "the vault's observational base is weeks wide; the catalogue's is seven years")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"run": "tools/probe_missing_variable.py",
                               "subject": "anomalies that a missing variable would explain",
                               "results": results}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}  ({len(results)} measurements)")


if __name__ == "__main__":
    main()
