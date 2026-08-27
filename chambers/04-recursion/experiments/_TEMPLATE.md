# EXP-0XX · <TITLE>

> Copy this file. Rename it `EXP-0XX-<slug>.md`. **Do not run anything until §3 is committed.**

| | |
|---|---|
| **ID** | `EXP-0XX` |
| **Chamber** | 04 · Recursion |
| **Opened** | YYYY-MM-DD |
| **Status** | `DRAFT` → `SEALED` → `RUN` → `SCORED` → `LOGGED` |
| **Sources used** | `ZP-SRC-0_` |

---

## 1 · Question

One sentence. If it needs two, it is two experiments.

## 2 · What is actually measured

Not what you hope to learn — what number or artifact comes out. "Spread of interpretation across
models" is a measurement. "Understanding my pattern better" is not.

## 3 · PREDICTION — SEALED

> **This section is written before the run and is never edited afterward.**
> Amending a sealed prediction voids the run. Log it as void rather than quietly fixing it.

```
Sealed: YYYY-MM-DD
Prediction:
Falsifier:
N (models / framings / instances):
```

## 4 · Blinding

State exactly what the model is **not** shown. Tiers, chamber provenance, prior results, and the
prediction are all withheld by default. Say what is withheld.

## 5 · Framing (verbatim)

The prompt is part of the result. Paste it exactly. Every variant, labelled.

## 6 · Raw output

Unedited. Include the parts that are boring and the parts that are wrong.

## 7 · Scoring

Against the sealed prediction only. Do not introduce new criteria here.

## 8 · Outcome

One of:

- `CONFIRMED` — prediction held
- `FALSIFIED` — prediction failed. **Write what you now believe instead.**
- `INCONCLUSIVE` — could not tell
- `VOID — CONVERGENCE` — every model agreed in the flattering direction; the run measured the
  training distribution, not the subject
- `VOID — UNSEALED` — prediction was written or edited after the run

## 9 · What changes

If nothing in the other three chambers changes as a result, say so plainly. An experiment that
changes nothing is allowed. It is not allowed to *claim* it changed something.

---

*Result is entered in `chambers/04-recursion/EXPERIMENTS.md §5` when logged.*
