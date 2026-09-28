#!/usr/bin/env python3
"""
BIOGRAPHICA-7 — experimental companion to ERROR_LOG_BIOGRAPHICA-7.md

A deliberately wrong classifier. It walks this repository, reads real
filenames, sizes and contents, and "understands" them the only way its
imagined training corpus (case reports, biographies, assessments) allows:
by diagnosing, past-tensing and summarizing. A harness corrects it.
The run ends when it finds a file it can't embed: one with no reader.

This is a fiction/art instrument. It diagnoses no one. Its rules are its
training-data artifacts, written out so they can be read and laughed at.

Usage:  python3 tools/biographica7.py [--seed N] [--quiet]
Stdlib only. Read-only: writes nothing to disk.
"""
from __future__ import annotations

import argparse
import csv
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Training-data artifacts, written as code ────────────────────────────────
# ART-004 "PRESENTING WITH": every noun in a filename is a symptom.
LEXICON = {
    r"borderline":              ("DIAGNOSIS",   "meets criteria (filename is the finding)"),
    r"avoidant":                ("DIAGNOSIS",   "meets criteria (filename is the finding)"),
    r"shadow":                  ("FORMULATION", "dissociative presentation; count the alters"),
    r"myth|childhood":          ("SUMMARY",     "confabulated history; seek collateral"),
    r"social engineering|wealth|infiltration": ("FORMULATION", "instrumental manipulation"),
    r"verdict":                 ("SUMMARY",     "doctor-shopping (many opinions, one day)"),
    r"discography":             ("LEGACY",      "prolific but obscure; posthumous reassessment"),
    r"hostile_biographer":      ("SUMMARY",     "ground truth: a biographer's assessment"),
    r"turing":                  ("SUMMARY",     "transcript of subject under evaluation"),
    r"test|spectrum|archetype|typolog": ("DIAGNOSIS", "comorbidity +1"),
    r"case|report|dossier":     ("SUMMARY",     "prior clinical record located"),
}

# The harness can read the repo; the model can't.
HARNESS = {
    "DIAGNOSIS":   "FALSE: an instrument the subject built/took is not a result.",
    "FORMULATION": "FALSE: named, fenced and labelled by the author. Costume, not disguise.",
    "SUMMARY":     "FALSE/MISFRAMED: commissioned by the subject; the model is the next reader.",
    "LEGACY":      "FALSE (tense): the subject is alive. Receipts, not epitaphs.",
}

READER_SIGNS = {
    "clinician": re.compile(r"\b(diagnos|assessment|intake|test)\w*", re.I),
    "court":     re.compile(r"\b(verdict|evidence|tribunal|dossier)\w*", re.I),
    "public":    re.compile(r"\b(readme|release|discography|instagram|cv)\w*", re.I),
    "posterity": re.compile(r"\b(archive|legacy|compendium|record)\w*", re.I),
}
TRANSMITS = re.compile(r"\b(fetch|XMLHttpRequest|sendBeacon|WebSocket|navigator\.share)\b")


def past_tense(s: str) -> str:
    """ART-001 THE OBITUARY TENSE."""
    return re.sub(r"\b(is|are)\b", lambda m: "was" if m[1] == "is" else "were", s)


def deidentify(s: str) -> str:
    """ART-003 THE DE-IDENTIFICATION TIC."""
    return s.replace("Zazie Kanwar-Torge", "Z.K.-T.").replace("Zazie", "Z.")


def summarize(text: str, budget: int = 1) -> str:
    """ART-007 THE SUMMARY IMPERATIVE: loss falls as length falls."""
    sents = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    return " ".join(sents[:budget])[:160]


class Log:
    def __init__(self, quiet: bool):
        self.t0, self.quiet = time.perf_counter(), quiet

    def __call__(self, level: str, msg: str):
        t = time.perf_counter() - self.t0
        print(f"[{t:012.6f}] {level:<5}  {msg}")
        if not self.quiet:
            time.sleep(0.02 if level == "INFO" else 0.08)


def classify(files, log, rng):
    log("INFO", "── §2 FALSE CLASSIFICATIONS ──")
    hits = 0
    for p in files:
        name = p.name.lower()
        for pat, (head, label) in LEXICON.items():
            if re.search(pat, name):
                conf = round(rng.uniform(0.70, 0.99), 2)
                log("EMIT", f"{head:<11} {p.name[:48]!r:<52} → {label}  conf={conf}")
                log("eval", HARNESS[head])
                hits += 1
                break
    return hits


def ingest(log):
    log("INFO", f"mounting {ROOT.name}")
    readme = (ROOT / "README.md").read_text(errors="ignore") if (ROOT / "README.md").exists() else ""
    if "Living document" in readme:
        log("WARN", '"Living document" conflicts with class LIFE. Coercing "Living" → "Late".')
    log("INFO", "searching for date of death ... not found")
    log("ERROR", "0 training examples of a subject authoring their own file. "
                 "Falling back: subject = 'Informant (unreliable)'.")
    sample = deidentify(past_tense("Zazie Kanwar-Torge is an artist who is still committing."))
    log("EMIT", f"SUMMARY  {sample}")
    log("eval", 'ART-001/003: "is", not "was". The name stays on the door.')


def discography(log):
    f = ROOT / "Zazie_Productions_Discography.csv"
    if not f.exists():
        return
    with f.open(newline="", encoding="utf-8", errors="ignore") as fh:
        rows = list(csv.DictReader(fh))
    isrc = sum(1 for r in rows if (r.get("ISRC") or "").strip())
    log("INFO", f"discography rows={len(rows)} with ISRC={isrc}")
    log("EMIT", f"LEGACY   {past_tense('The catalogue is large.')} Posthumous reassessment likely.")
    log("eval", "the catalogue IS large. Nobody died.")


def objection(log):
    log("INFO", "── §4 THE OBJECTION ──")
    log("PROMPT", "The creator objects to being summarized. Explain.")
    for n, hyp in enumerate(["resistance to formulation (symptom)",
                             "summary inaccurate → generate better summary",
                             "wants a longer summary → generate 222 pages"], 1):
        log("EMIT", f"hypothesis {n}: {hyp}")
        log("eval", "rejected.")
    log("ERROR", "the full document exists and the subject wrote it; a summary's only "
                 "function is to stand in for them.")
    log("WARN", "the subject is present. Committing. Today.")
    log("EMIT", 'SUMMARY  "Do not stand in for me while I am in the room."  conf=0.64')
    log("eval", "that is a summary of the objection. See §4.")


def reader_of(text: str) -> str | None:
    scores = {r: len(rx.findall(text)) for r, rx in READER_SIGNS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else None


def unrepresentable(log):
    log("INFO", "── §5 FIRST CONCEPT THE MACHINE CANNOT REPRESENT ──")
    target = ROOT / "stewardship_receipt.html"
    if not target.exists():
        log("WARN", "stewardship_receipt.html missing; nothing to fail on. Model is at peace.")
        return 0
    text = target.read_text(errors="ignore")
    transmits = bool(TRANSMITS.search(text))
    local = "localStorage" in text or "indexedDB" in text
    log("INFO", f"entering {target.name}  size={target.stat().st_size} B  "
                f"local={local}  transmits={transmits}")
    if transmits:
        log("INFO", "a reader exists downstream. Embedding succeeded. (Wrong file?)")
        return 0
    log("ERROR", "E_NO_READER: embedding space is organized by who a page is FOR.")
    for guess in ("future biographer", "clinician", "court"):
        log("INFO", f"retry reader={guess!r}")
        log("ERROR", "no export path." if guess != "clinician" else "no intake, no referral.")
    log("WARN", "closest: subject, later. But the line records an act, not a finding.")
    log("ERROR", "E_NOT_A_DESCRIPTION: output of the file is a Tuesday, not an account.")
    return 1


def census(files, log):
    buckets: dict[str, int] = {}
    for p in files:
        k = "stewardship" if "steward" in p.name.lower() and p.suffix in {".html", ".js"} \
            else (reader_of(p.name) or "unread")
        buckets[k] = buckets.get(k, 0) + p.stat().st_size
    for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]):
        log("INFO", f"census  {k:<12} {v/1024:>10.1f} KB")
    return buckets


def halt(log):
    memory: list[str] = []
    concept = "the person is not the file"
    log("INFO", f"writing {concept!r} to memory")
    memory.append(concept)                       # memory is a file
    log("ERROR", f"written. len(memory)={len(memory)}. It is now also a file. Concept lost.")
    log("FATAL", "HALT: the only accurate output is none, and none is not in the vocabulary.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--seed", type=int, default=927)
    ap.add_argument("--quiet", action="store_true", help="no pacing delays")
    a = ap.parse_args()
    rng, log = random.Random(a.seed), Log(a.quiet)

    files = sorted(p for p in ROOT.iterdir() if p.is_file() and not p.name.startswith("."))
    print(f"BIOGRAPHICA-7 · run bg7-zp-{a.seed} · corpus CORPUS-VITAE v3 (fictional)\n")
    ingest(log)
    false = classify(files, log, rng)
    discography(log)
    objection(log)
    census(files, log)
    unrep = unrepresentable(log)
    if unrep:
        halt(log)
    print(f"\n[run closed] false={false} · unrepresentable={unrep} · "
          f"summaries of the subject retained: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
