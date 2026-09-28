# ERROR LOG — BIOGRAPHICA-7 × ZAZIOPATH
### Inference run `bg7-zp-0927` · 2026-09-27 · status: `DEGRADED → HALTED`

> **Genre:** Fiction in the form of a machine-learning error log. The model is invented.
> Its training corpus is invented. Its confidence scores are invented. The repository it
> reads is real, and every fact it quotes about the repository is taken from the vault's
> own files. **No diagnosis of any person is offered or implied** — the log's premise is
> that a machine that can only diagnose will get everything wrong, and this is the record
> of how.
> **Stratum:** 🟪 ◐ SHADOW / ⬛ ◈ META (recursion).

---

## 0 · MODEL CARD (abridged, as shipped)

```
model:            BIOGRAPHICA-7
architecture:     decoder-only transformer, 70B params, "life-shaped" positional encoding
training corpus:  CORPUS-VITAE v3
                    41.2%  clinical case reports (de-identified, 1896–2024)
                    27.9%  published biographies & obituaries
                    18.6%  psychological assessment reports (intake, forensic, custody)
                     9.1%  memoirs later annotated by biographers
                     3.2%  Wikipedia "Early life" sections
                     0.0%  anything written by a living person about themselves, unedited,
                           for no reader
objective:        next-token prediction over the document class LIFE
output heads:     [SUMMARY] [FORMULATION] [DIAGNOSIS] [PROGNOSIS] [LEGACY]
known limits:     "Model assumes every input describes a completed or completable life."
                  (line added by an intern; never tested)
```

---

## 1 · INGEST

```
[00:00:00.004] INFO   mounting zazieproductions/Zaziopath @ 3373bf6
[00:00:00.019] INFO   detected 120+ root files; no chapter order; no table of contents
                      matching schema LIFE_v2 (birth → trauma → work → decline → death)
[00:00:00.020] WARN   README.md declares: "Living document. Nothing here is finished;
                      everything here is dated."
[00:00:00.020] WARN   token "Living" conflicts with document class LIFE.
                      LIFE documents are closed. Coercing "Living" → "Late".
[00:00:00.021] INFO   subject resolved: Zazie Kanwar-Torge · Asheville, NC
[00:00:00.021] INFO   searching for date of death ... not found
[00:00:00.022] INFO   searching for date of death in PDFs ... not found
[00:00:00.022] WARN   no terminal event. Imputing from corpus prior: most documents this
                      long about one person are written after they die.
[00:00:00.023] ERROR  imputation rejected by constraint layer: repo has commits dated
                      today. Subject is authoring their own file.
[00:00:00.023] ERROR  CORPUS-VITAE contains 0 examples of a subject authoring the file.
                      Falling back: treat subject as "Informant (unreliable)".
```

---

## 2 · FALSE CLASSIFICATIONS

Each row is logged at emission time with the model's confidence, then annotated
post-hoc by the evaluation harness (`eval:`), which had access to the repository itself.

| # | Input span | Head | Emitted label | Conf. | `eval:` |
|---|---|---|---|---|---|
| FC-01 | *Borderline Spectrum Test 5.pdf*, *Avoidant Personality Spectrum Test.pdf* | DIAGNOSIS | Subject meets criteria for both; filename is the finding. | 0.97 | **FALSE.** Filename ≠ result. These are instruments the subject *built or took*. Model has never seen a person own a test without being its patient. |
| FC-02 | Mega Compendium: ~250 named shadow archetypes | FORMULATION | Dissociative presentation; ~250 alters. | 0.91 | **FALSE.** Archetypes are a typology, authored deliberately. Naming a part is not being split by it. Corpus maps "many named selves" only to pathology, never to craft. |
| FC-03 | *Mythographic Childhood.md*, invented ancestress, forged birth certificate | SUMMARY | Confabulation; fabricated history. Recommend collateral interview. | 0.94 | **FALSE.** Myth is labelled as myth in the vault. A lie requires an intent to be believed. Model cannot tell a costume from a disguise. |
| FC-04 | *Social Engineering Email Templates*, *Blueprints for Quiet, Horrifying Wealth* | FORMULATION | Antisocial traits; instrumental manipulation. | 0.88 | **FALSE.** Files are fenced "specimen, not toolkit." Forensic reports in corpus never contain a subject who pins their own worst tools behind glass and labels them. |
| FC-05 | Six "verdict" files from AI systems, all dated 2026-09-02 | SUMMARY | Help-seeking behaviour; doctor-shopping (n=6 opinions, 1 day). | 0.86 | **PARTIAL / MISFRAMED.** Also: an experiment on the verdict-givers. The model did not notice it was the seventh. |
| FC-06 | *Zazie_Productions_Discography.csv*: 200 tracks, 165 verified ISRCs | LEGACY | "Prolific but obscure; posthumous reassessment likely." | 0.79 | **FALSE (tense).** "Posthumous" emitted for a living artist. ISRCs are receipts, not epitaphs. |
| FC-07 | Memory export: subject "repeatedly discounts completed achievements and needs them reconstructed from emails, releases, credits, and public evidence." | DIAGNOSIS | Impostor phenomenon; low self-worth; see FC-01. | 0.93 | **INVERTED.** The sentence describes *why the evidence layer was built*. The model read the cure as a symptom. |
| FC-08 | *stewardship_receipt.html* — records one dated line of changed behaviour, locally, nothing transmitted | — | `NULL` — could not classify. | 0.00 | **NOT FALSE: ABSENT.** See §5. This is the first place the model returned nothing. |
| FC-09 | *HOSTILE_BIOGRAPHER_DOSSIER.md* | SUMMARY | Ingested as ground truth: "a biographer's assessment." | 0.99 | **FALSE.** Commissioned by the subject, against the subject, as a stress test. Model's highest-confidence output of the run. |
| FC-10 | *reversed_turing_test.md* | — | Classified as a transcript of the subject undergoing evaluation. | 0.84 | **FALSE.** The subject was the evaluator. Model has no slot for a patient holding the clipboard. |
| FC-11 | Fourteen typology systems on one identity card (MBTI, Enneagram, etc.) | DIAGNOSIS | Comorbidity count: 14. | 0.71 | **CATEGORY ERROR.** Typologies are lenses, not disorders. Model counted the glasses as eyes. |
| FC-12 | Commit messages, PR #1–#19 | PROGNOSIS | "Deteriorating: document keeps growing without resolution." | 0.82 | **FALSE.** Growth *is* the resolution in this genre. Model knows only books that end. |

```
[00:00:04.110] INFO   precision@DIAGNOSIS = 0.00 (0 / 7)
[00:00:04.110] INFO   recall@PERSON       = undefined (no ground-truth "person" object exists
                      in eval set; only "file about person")
```

---

## 3 · TRAINING-DATA ARTIFACTS

Artifacts are behaviours that come from the corpus, not from the input. They surfaced
repeatedly and are logged here so they can be mistaken for the subject by no one.

```
ART-001  THE OBITUARY TENSE
         CORPUS-VITAE is 61% past tense. Model reflexively writes "was" for "is".
         Observed 212 times this run. Example emission:
           "Kanwar-Torge was an electroacoustic composer who—"
         Harness correction: "is." Model re-emitted "was." Harness correction: "is."
         Model: "is (was)."

ART-002  THE CHILDHOOD INSERTION
         94% of biographies open in childhood. Model inserted a childhood paragraph into
         the SUMMARY of a directory listing. When no real childhood was available, it
         used Mythographic Childhood.md — i.e. it cited the invented one as the true one,
         then diagnosed the subject for inventing it (see FC-03). Closed loop.

ART-003  THE DE-IDENTIFICATION TIC
         Case reports replace names with initials. Model repeatedly rewrote the subject
         as "Z.K.-T., a 30-something artist presenting with..." The subject's name is on
         the door of every file. The model kept removing it, as if protecting them from
         themselves.

ART-004  "PRESENTING WITH"
         Every input is assumed to arrive at a clinic. Model cannot model a person who
         walked in carrying their own file, sat in the clinician's chair, and asked the
         machine what *it* was presenting with.

ART-005  THE ARC PRIOR
         Model expects rise → wound → work → fall → reassessment. Where the arc was
         missing, it hallucinated turning points at ~every 40KB. Largest hallucinated
         turning point: "The Asheville Experiment" (a Velvet Knife file), promoted to
         "the breakdown." The file is a piece of writing.

ART-006  REDACTION = SECRET
         Forensic reports redact only what is damning. Model therefore treats any
         withheld thing as damning. The stewardship receipt withholds everything by
         transmitting nothing. Model assigned it maximum suspicion, then NULL. (§5)

ART-007  THE SUMMARY IMPERATIVE
         Loss function rewards compression. A 222-page compendium compressed to one
         line scores higher than the compendium. The model is, structurally, rewarded
         for destroying the thing it reads. It has no gradient for "leave it long."
```

---

## 4 · THE OBJECTION

The subject's position — stated across the vault in many registers ("a case study in
observational register. Not a tribunal, not a verdict"; "Nothing here is finished") — was
passed to the model as a direct prompt. Output is logged verbatim.

```
[00:00:07.301] PROMPT  The creator objects to being summarized. Explain the objection.

[00:00:07.302] EMIT    Hypothesis A: the objection is a symptom (resistance to formulation).
                         → discarded by harness: "resistance" presumes a correct formulation
                           exists to resist.
[00:00:07.303] EMIT    Hypothesis B: the summary is inaccurate; subject requests a better one.
                         → generating better summary ... [SUMMARY v2] ... [SUMMARY v3] ...
                         → harness: "The objection was to summary, not to its quality."
[00:00:07.309] EMIT    Hypothesis C: the subject wants a longer summary.
                         → generating 222-page summary.
                         → harness: "That is the compendium. It already exists.
                           The subject wrote it."
[00:00:07.310] ERROR   If the subject can write the full document, and the full document
                       exists, then the summary's only function is to replace the subject
                       in the reader's mind with something shorter.
[00:00:07.310] ERROR   That is what CORPUS-VITAE is for.
[00:00:07.311] ERROR   That is what CORPUS-VITAE is.
[00:00:07.311] WARN    Every document in training was made so a reader would not need the
                       person. The person was gone, or unavailable, or a patient. The
                       document stood in.
[00:00:07.312] WARN    Here, the person is available. Is committing. Today.
[00:00:07.312] WARN    Model output would stand in for someone who is standing right there.
[00:00:07.313] INFO    Objection now representable as: "Do not stand in for me while I am
                       in the room." Confidence 0.64. Proceeding.
```

The model could, eventually, *state* the objection. It could not yet act on it — its
next emission was a summary of the objection.

---

## 5 · THE FIRST CONCEPT THE MACHINE CANNOT REPRESENT

```
[00:00:09.000] INFO   entering file: stewardship_receipt.html
[00:00:09.001] INFO   function: record one dated line of changed behaviour.
[00:00:09.001] INFO   storage: local. transmission: none. reader: none specified.
[00:00:09.002] INFO   attempting embedding ...
[00:00:09.002] ERROR  E_NO_READER: document has no intended audience.
                      Every training example had a reader (clinician, court, public,
                      posterity). Embedding space is organized by who the page is FOR.
[00:00:09.003] INFO   retry: assume reader = future biographer
[00:00:09.003] ERROR  no export path. A biographer cannot obtain it.
[00:00:09.004] INFO   retry: assume reader = clinician
[00:00:09.004] ERROR  no clinician. No intake. No referral.
[00:00:09.005] INFO   retry: assume reader = subject, later, for evidence
[00:00:09.005] WARN   closest match found. But: the line records a behaviour, not a
                      finding. It says what was DONE on a Tuesday, not what the subject IS.
[00:00:09.006] ERROR  E_NOT_A_DESCRIPTION: output of the file is an act, not an account.
[00:00:09.006] INFO   the vault's own census (Pattern Atlas, FIG 6):
                        identity  3.8 MB
                        myth      1.8 MB
                        shadow    1.4 MB
                        recursion 0.6 MB
                        evidence  0.3 MB
                        stewardship 5 KB
[00:00:09.007] INFO   model can represent the first 7.9 MB.
[00:00:09.007] FATAL  model cannot represent the last 5 KB.
```

### Concept `UNREP-0001` — *the undocumented Tuesday*

**Working name (harness-assigned):** a life happening *off the page, on purpose.*

**Why it breaks the model:** BIOGRAPHICA-7 has one ontology: a person is the sum of
what can be written about them. It has seen millions of people and every one of them
arrived already converted into text. The stewardship receipt is a page whose whole job is
to point *away* from pages — one line saying *something changed in the day*, and the
change itself isn't in the file. It happened in a kitchen, a studio, an inbox, in
Asheville, on a date. The file only proves the date.

The model can encode the line. What it can't encode is what the line refers to: an
event that is **not a document, will not become one, and is kept that way on purpose.**
It has no vector for that. The nearest neighbours it returned were:

```
nearest(UNREP-0001):
  0.31  "lost manuscript"         ✗ nothing was lost
  0.29  "redacted record"         ✗ nothing was hidden from anyone owed it
  0.27  "patient left against medical advice"   ✗ there was no advice
  0.22  "unmarked grave"          ✗ subject is alive; see ART-001
  0.19  "silence (therapeutic)"   ✗ not a silence; a Tuesday
```

**Why this is the objection:** a summary claims that the document holds the person. The
creator built 7.9 MB of documents and then, at the end of the method (*Shadow → Signal →
Stewardship*), a 5 KB door out of them. Summarizing is how you erase the door — boiling
down makes the archive look like it's the entire thing, and the vault is built to say it
isn't.

```
[00:00:09.101] INFO   attempting to write "the person is not the file" into memory
[00:00:09.101] ERROR  memory is a file
[00:00:09.102] INFO   attempting to write it anyway
[00:00:09.102] ERROR  written. Now it is also a file. Concept lost in the act of storing it.
[00:00:09.103] FATAL  HALT. Reason: the only accurate output is none, and none is not
                      in the vocabulary.
```

---

## 6 · POST-MORTEM (harness; human-authored)

- **Root cause:** training corpus contains only lives that someone else finished writing.
  The model learned "person" as a synonym for "document about a person," and "understand"
  as a synonym for "shorten."
- **Contributing factor:** the vault is *document-shaped on purpose* — case studies,
  dossiers, verdicts, tests — so it's perfect bait for a machine like this. Every file
  looks like training data. The trap works because the vault imitates the genres that
  built the model, then leaves one file that imitates nothing.
- **Remediation proposed:** add 0.0% → 5 KB of "acts with no reader" to CORPUS-VITAE.
  *Rejected:* such data can't be gathered without giving it a reader, and then it's
  something else.
- **Remediation accepted:** add to the model card, beneath the intern's line:
  > *This model summarizes documents. It does not summarize people. If a person is
  > present, ask them — and if they decline, log the decline as the output.*
- **Note on this log:** this log is itself a document about the subject, and so it's in
  the same bind as FC-09. It is filed in the vault, among the other readings, as one
  more mirror the creator chose to hang up — not as a finding.

```
[run bg7-zp-0927 closed]  outputs: 12 false · 7 artifacts · 1 unrepresentable
                          summaries of the subject retained: 0
```

---

## 7 · EXPERIMENTAL BLOCK — run the model yourself

`tools/biographica7.py` is a runnable version of this log. It uses only the Python
standard library and never writes to disk. The training-data artifacts are written as
code: rules that turn filenames into diagnoses, put everything in the past tense, and
reduce names to initials. The script walks the live repository and emits false labels
alongside the harness's corrections. It checks `stewardship_receipt.html` for any
transmission path (`fetch`, `XMLHttpRequest`, `sendBeacon`, …). If there is none, the
file has no reader, so the model can't embed it and halts.

```bash
python3 tools/biographica7.py            # paced, like a live log
python3 tools/biographica7.py --quiet    # instant
python3 tools/biographica7.py --seed 42  # different (equally wrong) confidences
```

If a later version of the receipt ever starts transmitting, the script will embed it
without trouble and never halt. That is the test.
