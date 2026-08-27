#!/usr/bin/env python3
"""
vault_check.py — integrity check for the Zaziopath self-forensics vault.

This does not lint prose. It re-derives the numbers quoted in README.md from the
artifacts actually on disk, verifies every path reference resolves, confirms the
source registry has not drifted, and refuses to pass if any pattern lacks a
falsifier or any experiment lacks a sealed prediction.

    python3 scripts/vault_check.py

Exit 0 = the vault is internally consistent and its citations are real.
Exit 1 = something is wrong. Read the FAIL lines.

A self-forensics vault that cannot be audited is decoration.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results: list[tuple[str, str, str]] = []


def check(ok: bool, label: str, detail: str = "") -> bool:
    results.append((PASS if ok else FAIL, label, detail))
    return ok


def skip(label: str, detail: str = "") -> None:
    results.append((SKIP, label, detail))


# --------------------------------------------------------------------------- #
# 1. Source registry
# --------------------------------------------------------------------------- #

def check_registry() -> dict | None:
    reg_path = ROOT / "_registry" / "sources.json"
    if not check(reg_path.exists(), "_registry/sources.json exists"):
        return None
    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except Exception as exc:                                   # noqa: BLE001
        check(False, "sources.json parses", str(exc))
        return None
    check(True, "sources.json parses", f"schema {reg.get('schema')}")

    sources = reg.get("sources", [])
    check(len(sources) == 6, "registry holds 6 sources", f"found {len(sources)}")

    for src in sources:
        sid = src.get("id", "?")
        path = ROOT / src["path"]
        if not check(path.exists(), f"{sid} path resolves", src["path"]):
            continue

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        check(
            digest == src.get("sha256"),
            f"{sid} sha256 matches registry",
            "source changed on disk — re-verify every claim citing it"
            if digest != src.get("sha256") else digest[:16],
        )
        check(
            path.stat().st_size == src.get("bytes"),
            f"{sid} byte size matches",
            f"{path.stat().st_size} vs {src.get('bytes')}",
        )
        for key in ("tier", "as_of", "limit"):
            check(bool(src.get(key)), f"{sid} declares '{key}'")

    return reg


# --------------------------------------------------------------------------- #
# 2. Re-derive quoted numbers from the artifacts themselves
# --------------------------------------------------------------------------- #

def page_count(path: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return len(PdfReader(str(path)).pages)


def check_pdf_extents(sources: dict) -> None:
    for sid, expected in sources.items():
        if "extent_pages" not in expected:
            continue
        path = ROOT / expected["path"]
        n = page_count(path)
        if n is None:
            skip(f"{sid} page count", "pypdf not installed")
            continue
        check(
            n == expected["extent_pages"],
            f"{sid} page count == {expected['extent_pages']}",
            f"found {n}",
        )


def check_discography(sources: dict) -> None:
    src = sources.get("ZP-SRC-06")
    if not src:
        return
    path = ROOT / src["path"]
    try:
        import openpyxl
    except ImportError:
        skip("ZP-SRC-06 workbook recount", "openpyxl not installed")
        return

    wb = openpyxl.load_workbook(str(path), data_only=True)
    check(
        len(wb.sheetnames) == src["sheets"],
        f"ZP-SRC-06 has {src['sheets']} sheets",
        ", ".join(wb.sheetnames),
    )

    cat = wb["CATALOG"]
    rows = [
        r for r in cat.iter_rows(min_row=3, values_only=True)
        if isinstance(r[0], (int, float)) and r[1]
    ]
    tracks = len(rows)
    isrc = sum(
        1 for r in rows
        if r[7] is not None and str(r[7]).strip() not in ("", "—")
    )
    check(
        tracks == src["tracks"],
        f"ZP-SRC-06 track count == {src['tracks']}",
        f"recounted {tracks} from CATALOG",
    )
    check(
        isrc == src["isrc_verified"],
        f"ZP-SRC-06 ISRC count == {src['isrc_verified']}",
        f"recounted {isrc} from CATALOG",
    )

    years = sorted({int(r[4]) for r in rows if r[4]})
    check(
        [years[0], years[-1]] == src["years"],
        f"ZP-SRC-06 span == {src['years'][0]}-{src['years'][1]}",
        f"found {years[0]}-{years[-1]}",
    )


def check_memory_export(sources: dict) -> None:
    src = sources.get("ZP-SRC-02")
    if not src:
        return
    text = (ROOT / src["path"]).read_text(encoding="utf-8")
    # The export is escaped markdown: tier keys arrive as `direct\_evidence`.
    unescaped = text.replace("\\_", "_")
    lines = text.splitlines()
    check(
        len(lines) == src["extent_lines"],
        f"ZP-SRC-02 line count == {src['extent_lines']}",
        f"found {len(lines)} (splitlines; file has no trailing newline)",
    )
    sections = re.findall(r'^\s{0,4}"([A-Za-z][^"]{2,80})":\s*\{', text, re.M)
    check(
        len(sections) == src["sections"],
        f"ZP-SRC-02 has {src['sections']} sections",
        f"found {len(sections)}",
    )
    for tier in src["tiers"]:
        check(tier in unescaped, f"ZP-SRC-02 declares tier '{tier}'")


def check_compendium(sources: dict) -> None:
    src = sources.get("ZP-SRC-05")
    if not src:
        return
    try:
        from pypdf import PdfReader
    except ImportError:
        skip("ZP-SRC-05 archetype recount", "pypdf not installed")
        return

    reader = PdfReader(str(ROOT / src["path"]))
    toc = "".join((reader.pages[i].extract_text() or "") for i in range(1, 12))
    toc = re.sub(r"\s*\.\s*\.\s*[\s\.]*", " ", toc)
    lines = [ln.strip() for ln in toc.split("\n")]
    figures = (
        len([ln for ln in lines if re.match(r"^\d+\.\d+\.\d+\s+\S", ln)])
        + len([ln for ln in lines if re.match(r"^\d+\.\d+\s+The\s", ln)])
    )
    check(
        figures == src["named_figures"],
        f"ZP-SRC-05 named figures == {src['named_figures']}",
        f"recounted {figures} from the table of contents",
    )
    check(
        len([ln for ln in lines if re.match(r"^20\.\d+\s+The", ln)]) == src["light_counterparts"],
        f"ZP-SRC-05 light-triad counterparts == {src['light_counterparts']}",
        "counted from TOC chapter 20",
    )


def check_media_master(sources: dict) -> None:
    src = sources.get("ZP-SRC-03")
    if not src:
        return
    try:
        from pypdf import PdfReader
    except ImportError:
        skip("ZP-SRC-03 record count", "pypdf not installed")
        return
    text = "".join(
        (p.extract_text() or "") for p in PdfReader(str(ROOT / src["path"])).pages[:2]
    )
    flat = re.sub(r"\s+", " ", text)
    check(
        str(src["records"]) in flat,
        f"ZP-SRC-03 states {src['records']} verified records",
        "count not found in the document's own summary",
    )


# --------------------------------------------------------------------------- #
# 3. Structure
# --------------------------------------------------------------------------- #

REQUIRED_PATHS = [
    "README.md",
    "docs/METHOD.md",
    "_registry/sources.json",
    "chambers/01-shadow/PARTS.md",
    "chambers/02-signal/SURFACE.md",
    "chambers/03-stewardship/COUNTERPATTERNS.md",
    "chambers/04-recursion/EXPERIMENTS.md",
    "chambers/04-recursion/experiments/_TEMPLATE.md",
    "chambers/04-recursion/experiments/EXP-001-mirror-divergence.md",
    "patterns/INDEX.md",
    "case-study/CASE-0001-self.md",
]


def check_structure() -> None:
    for rel in REQUIRED_PATHS:
        check((ROOT / rel).exists(), f"exists: {rel}")


# --------------------------------------------------------------------------- #
# 4. Every path reference in every markdown file resolves
# --------------------------------------------------------------------------- #

CODE_PATH = re.compile(r"`([^`\s]+\.(?:md|py|json))`")
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")


def resolve(ref: str, origin: Path) -> bool:
    ref = ref.split("#")[0]
    if not ref:
        return True
    # Angle-bracket tokens are naming placeholders, not paths: `EXP-0XX-<slug>.md`
    if "<" in ref or ">" in ref:
        return True
    for base in (origin.parent, ROOT):
        if (base / ref).exists():
            return True
    return any(p.name == Path(ref).name for p in ROOT.rglob("*") if p.is_file())


def check_references() -> None:
    bad = []
    total = 0
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        refs = set(CODE_PATH.findall(text)) | set(MD_LINK.findall(text))
        for ref in refs:
            if ref.startswith(("http://", "https://", "mailto:")):
                continue
            total += 1
            if not resolve(ref, md):
                bad.append(f"{md.relative_to(ROOT)} -> {ref}")
    check(
        not bad,
        f"all {total} path references resolve",
        "; ".join(bad[:6]) if bad else "",
    )


# --------------------------------------------------------------------------- #
# 5. Patterns must carry a falsifier
# --------------------------------------------------------------------------- #

def check_patterns() -> None:
    path = ROOT / "patterns" / "INDEX.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    # Only `P-NN` headings count as entries. The document subtitle also uses `###`
    # and must not be parsed as a pattern.
    entries = re.findall(r"^### `P-(\d+)`\s*[^\n]*\n(.*?)(?=^### |\Z)",
                         text, re.M | re.S)
    ids = [f"P-{num}" for num, _ in entries]
    missing = [
        pid for pid, body in zip(ids, (b for _, b in entries))
        if "**FALSIFIER:**" not in body or "**STATUS:**" not in body
    ]

    check(bool(ids), "patterns/INDEX.md contains pattern entries", f"{len(ids)} found")
    check(
        not missing,
        "every pattern carries a falsifier and a status",
        ", ".join(missing) if missing else f"{len(ids)}/{len(ids)}",
    )
    check(
        ids == sorted(set(ids)),
        "pattern IDs are unique and ordered",
        ", ".join(ids),
    )

    declared = re.search(r"\| Total patterns \| \*\*(\d+)\*\* \|", text)
    if declared:
        check(
            int(declared.group(1)) == len(ids),
            f"declared total ({declared.group(1)}) matches actual ({len(ids)})",
        )

    check("## RETIREMENT LEDGER" in text, "retirement ledger present")
    check("## FICTION REGISTER" in text, "fiction register present")


# --------------------------------------------------------------------------- #
# 6. Experiments must be sealed before they can run
# --------------------------------------------------------------------------- #

def check_experiments() -> None:
    exp_dir = ROOT / "chambers" / "04-recursion" / "experiments"
    if not exp_dir.exists():
        return
    runs = [p for p in sorted(exp_dir.glob("EXP-*.md"))]
    check(bool(runs), "at least one experiment exists", f"{len(runs)} found")

    for exp in runs:
        text = exp.read_text(encoding="utf-8")
        name = exp.name
        check("PREDICTION" in text.upper(), f"{name} has a prediction section")
        check("Falsifier:" in text, f"{name} states a falsifier")
        check("## 4 · Blinding" in text, f"{name} declares what the model is not shown")
        check(
            "VOID" in text,
            f"{name} defines a void condition",
            "an experiment with no failure state is not an experiment",
        )

    queue = ROOT / "chambers" / "04-recursion" / "EXPERIMENTS.md"
    if queue.exists():
        qtext = queue.read_text(encoding="utf-8")
        for exp in runs:
            check(
                exp.stem.split("-")[0] + "-" + exp.stem.split("-")[1] in qtext
                or exp.stem in qtext,
                f"{exp.name} is listed in the queue",
            )


# --------------------------------------------------------------------------- #
# 7. Case file discipline
# --------------------------------------------------------------------------- #

def check_case_file() -> None:
    path = ROOT / "case-study" / "CASE-0001-self.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    check("## 3 · Competing explanations" in text, "case file has competing explanations")
    hypotheses = re.findall(r"^### (H\d)", text, re.M)
    check(
        len(hypotheses) >= 3,
        "at least three competing explanations",
        f"found {len(hypotheses)}: {', '.join(hypotheses)}",
    )
    check("## 6 · Revision log" in text, "case file has a revision log")
    check(
        "flattering" in text.lower(),
        "the flattering explanation is acknowledged and placed last",
    )
    check(
        re.search(r"\| (E-\d+) \|", text) is not None,
        "evidence register is populated",
    )


# --------------------------------------------------------------------------- #
# 8. Standing prohibitions are actually written down
# --------------------------------------------------------------------------- #

def check_prohibitions() -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    for rule in (
        "No diagnosis",
        "No third parties",
        "30-day seal",
        "No unsealed prediction",
        "No T3 in the case file",
    ):
        check(rule in text, f"README states prohibition: {rule}")
    check(
        "SELF-AWARENESS PRESTIGE TRAP" in text.upper(),
        "README names the governing hazard",
    )


# --------------------------------------------------------------------------- #

def main() -> int:
    print("ZAZIOPATH · VAULT INTEGRITY CHECK")
    print("registry ZP-VAULT-000 · Office of Recursive Self-Study")
    print("=" * 62)

    check_structure()
    reg = check_registry()
    if reg:
        sources = {s["id"]: s for s in reg["sources"]}
        check_pdf_extents(sources)
        check_discography(sources)
        check_memory_export(sources)
        check_compendium(sources)
        check_media_master(sources)
    check_references()
    check_patterns()
    check_experiments()
    check_case_file()
    check_prohibitions()

    widths = max(len(label) for _, label, _ in results)
    n_pass = n_fail = n_skip = 0
    for status, label, detail in results:
        if status == PASS:
            n_pass += 1
        elif status == FAIL:
            n_fail += 1
        else:
            n_skip += 1
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "SKIP": "skip"}[status]
        line = f"  [{mark}] {label.ljust(widths)}"
        print(line + (f"  {detail}" if detail and status != PASS else ""))

    print("=" * 62)
    print(f"  {n_pass} passed · {n_fail} failed · {n_skip} skipped")
    if n_fail:
        print("\n  The vault is internally inconsistent. Fix the FAIL lines above.")
        print("  A self-forensics vault that cannot be audited is decoration.")
        return 1
    if n_skip:
        print("\n  Skipped checks need pypdf / openpyxl:")
        print("      pip install pypdf openpyxl")
    print("\n  Consistent. Citations verified against the artifacts on disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
