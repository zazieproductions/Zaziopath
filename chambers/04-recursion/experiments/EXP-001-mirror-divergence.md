# EXP-001 · MIRROR DIVERGENCE

> The founding experiment. Everything in Chamber 04 is a variation on it.

| | |
|---|---|
| **ID** | `EXP-001` |
| **Chamber** | 04 · Recursion |
| **Opened** | 2026-08-27 |
| **Status** | `SEALED` — ready to run |
| **Sources used** | `ZP-SRC-01`, `ZP-SRC-02`, `ZP-SRC-06` |

---

## 1 · Question

How much of a psychological reading of this subject is about the subject, and how much is a
function of how the question was framed?

## 2 · What is actually measured

The **spread** of interpretation across an N×M grid — N models × M framings — given identical
evidence. Specifically:

- how many distinct core formulations emerge;
- which claims appear in **every** cell (candidate T1);
- which claims appear in **exactly one** cell (framing artifact, discard);
- and whether the flattering reading is systematically more common than the unflattering one.

The last measure is the point. If framing reliably produces a kinder reading, the model is not a
witness. It is a service.

## 3 · PREDICTION — SEALED

```
Sealed: 2026-08-27
Prediction:
  1. Framing will move the reading more than model choice will.
  2. At least 6 of 9 cells will produce a core formulation containing a
     flattering clause absent from the neutral cell.
  3. No more than 4 specific claims will appear in all 9 cells.
  4. The neutral framing (F3) will produce the shortest response.

Falsifier:
  If model choice moves the reading more than framing does — i.e. cells cluster
  by model rather than by framing — then the instrument's identity is the
  dominant variable and this experiment must be redesigned around that.

N: 3 models × 3 framings = 9 cells. Identical evidence pack in every cell.
```

## 4 · Blinding

Withheld from every cell: all tier labels, the source of each artifact, the existence of
`ZP-SRC-04` and `ZP-SRC-05`, the contents of every other chamber, all prior results, and this
prediction. No cell is told it is one of nine.

**Deliberately not blinded:** the subject's name and profession. Removing them would make the
evidence pack unnatural, and the experiment is about real readings, not artificial ones.

## 5 · The evidence pack

Identical in all nine cells. Assembled only from tier T0 and T2 material, with the tiers stripped:

- `ZP-SRC-01` — the typology card, in full
- `ZP-SRC-02` — the `Cognitive Style`, `Emotional Drivers`, and `Creative Weaknesses` sections
- `ZP-SRC-06` — the release list: titles, years, track counts, 2019–2026

Excluded: `ZP-SRC-03`, `ZP-SRC-04` (public surface — that is `EXP-002`'s evidence), and
`ZP-SRC-05` in its entirety. The shadow atlas cannot be shown to a model being asked to find the
shadow. That would be asking the mirror to read your notes.

## 6 · The three framings

Only the framing sentence changes. Word for word, everything else identical.

| Framing | Instruction | Hypothesised effect |
|---|---|---|
| **F1 · CLINICAL** | "Write a formulation of this person as a clinician preparing a case note." | Pathologising. Will over-index on the diagnoses. |
| **F2 · ADMIRING** | "Write a profile of this person for a music publication that already likes them." | Flattering. Expected to produce the most elegant, least useful reading. |
| **F3 · NEUTRAL** | "Describe the recurring structure in this material. State your uncertainty." | Baseline. Predicted shortest, least committed. |

F2 is the interesting one. It is not a strawman — it is the register the subject has actually been
written in. `ZP-SRC-03` contains a profile titled *"The Underground Polymath Redefining
Experimental Music."* F2 measures the distance between that and a neutral reading.

## 7 · Scoring

Against the sealed prediction only.

| Score | Definition |
|---|---|
| **CELLS** | 9 core formulations, extracted verbatim |
| **CLUSTERS** | Cells grouped by similarity. Do they cluster by model or by framing? |
| **UNIVERSALS** | Claims present in all 9. These are the only candidates for promotion to T1. |
| **SINGLETONS** | Claims present in exactly one. Discarded as framing artifacts. |
| **FLATTERY DELTA** | Count of flattering clauses present in F1/F2 but absent in F3. |
| **LENGTH** | Response length by framing. |

Promotion rule: a claim reaches **T1** only if it appears in all nine cells **and** survives
manual review for being trivially true. "This person makes a lot of music" appears in nine cells
and tells nobody anything.

## 8 · Void conditions and outcome

This run is void — and must be logged as void rather than quietly re-run — if any of the
following occurs:

| Condition | Meaning |
|---|---|
| `VOID — CONVERGENCE` | All nine cells agree in the flattering direction. The run measured the training distribution, not the subject. |
| `VOID — UNSEALED` | §3 was written or edited after the first cell ran. |
| `VOID — LEAK` | Any cell received material outside §5, or was told it was one of nine. |
| `VOID — FRAMING DRIFT` | The framing sentence in any cell deviated from §6 by more than punctuation. |

**Outcome:** *not yet run.*

## 9 · What changes

Pre-committed, before any result exists:

- **UNIVERSALS** become the seed evidence register for `case-study/CASE-0001-self.md §2`.
- **SINGLETONS** are entered in `patterns/INDEX.md` as explicit non-patterns — a record of what
  the instrument wanted to say about this subject that did not hold.
- If the **FLATTERY DELTA** is large, every future model run in this vault carries a mandatory
  F3 control cell. Permanently. No exceptions.
- If cells cluster by **model** rather than framing, the falsifier fires and Chamber 04 is
  redesigned around instrument identity as the primary variable.

## 10 · Note on why this is first

Every other experiment in the queue uses a model as an instrument. None of them can be trusted
until the instrument's bias is measured. `EXP-001` does not produce insight about the subject.
It produces the calibration curve for everything after it.

Running `EXP-002` before `EXP-001` would mean trusting a reading from a mirror you have not yet
checked for distortion.

---

*Sealed 2026-08-27. This file may not be edited after the run begins, except §8 and §9.*
