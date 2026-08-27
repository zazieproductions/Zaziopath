# METHOD
### The full protocol. `README.md` is the map; this is the machinery.

---

## 1 · The position problem

Every self-study has an observer. This one does not. The subject writes the file, chooses the
instrument, reads the output, and decides what counted. Four collapse points, in one person, with
no external referee.

That is not a flaw to apologise for. It is the subject. The method is built around it:

> **Do not try to remove the observer. Measure the observer.**

Everything below is a way of measuring the observer.

## 2 · Epistemic tiers

| Tier | Name | Rule |
|---|---|---|
| **T0** | Direct evidence | Dated, sourced, retrievable. URL · ISRC · verbatim quote · screenshot · file hash. |
| **T1** | Strong inference | ≥3 independent T0 observations, stated separately. |
| **T2** | Speculative | Coherent hypothesis, zero independent support. Always labelled. Never quoted as finding. |
| **T3** | Quarantined | Felt, no external referent. Dated and sealed. Reviewed at 30 days. **Never enters the case file.** |

**Escalation** is allowed (T2 → T1 → T0) and must cite the new evidence.
**De-escalation** is mandatory the moment supporting evidence is withdrawn. Silently dropping a
tier is the most common form of self-flattery in this repo and is treated as a finding.

## 3 · Evidence classes

From `ZP-SRC-04`, adopted unchanged:

| Class | Meaning |
|---|---|
| **A** | Primary surface — retrieved directly from the subject's own published artifact |
| **B** | Quantitative record — counts, metrics, ISRCs, dates |
| **C** | Third-party — someone else's record of the subject |
| **D** | Self-report — the subject's own account |
| **E** | Search-inferred — discovered indirectly, not retrieved directly |

Class D is the one to distrust. It is also the one the vault is made of. Hence §2.

## 4 · Dispositions

`KEEP` · `CLARIFY` · `REDUCE` · `SEPARATE` · `ARCHIVE` · `REMOVE` · **`TEST`**

`TEST` — the vault's addition — is the disposition for anything that cannot be settled by looking.
It routes the finding to Chamber 04 as a pre-registered experiment with a written prediction.

## 5 · The falsifier rule

Nothing is admitted as a pattern or an archetype without a **behavioral falsifier written at
intake**:

```
FALSIFIER: If <observable behavior> occurs <N> times before <date>, this is wrong.
```

Not "if I feel less envious." Not "if I become more secure." An observable, countable, dated
behavior. `ZP-SRC-05` states the standard: *"Look for behavior, not merely inner sophistication.
Insight counts when it changes what another person has to absorb."*

An entry with no falsifier is reclassified `FICTION`. Fiction is allowed in the vault — it is
allowed to be *evidence*.

## 6 · The retirement ledger

`patterns/INDEX.md` keeps a permanent record of **patterns disproved about the subject.**

Adding an insight requires reviewing one already there (Prohibition 6). This is the structural
defence against the prestige trap: an archive with a monotonic growth function is a monument, and
monuments do not update.

## 7 · The four chambers — operating rules

**01 SHADOW.** Every archetype gets a falsifier or becomes fiction. The 271 figures in `ZP-SRC-05`
are a hypothesis space, not a census. Current expectation: most will not survive `EXP-004`.

**02 SIGNAL.** Point-in-time snapshots, always dated. The embarrassing number is recorded first.
Never curate a snapshot to make the delta smaller.

**03 STEWARDSHIP.** A counter-archetype exists only once it has been **used, dated, and cost
something.** Everything else sits in `UNPROVEN`. Collecting light-triad counterparts is exactly as
vain as collecting dark ones; the vault treats both identically.

**04 RECURSION.** Divergence is the measurement. Agreement is discarded as instrument bias. No
experiment may be run before its prediction is committed to a file.

## 8 · Model protocol (Chamber 04)

1. **Blind where possible.** The model should not see the prediction, the tier, or the chamber
   the evidence came from.
2. **Never one model.** Any result from a single model is a draft, not a finding.
3. **Log the framing.** The prompt is part of the result. Framing is recorded verbatim.
4. **Discard agreement.** If every model converges on the flattering reading, the experiment
   measures the training distribution, not the subject. Log it as `VOID — CONVERGENCE`.
5. **No named individuals.** Real third parties never enter a prompt. See Prohibition 2.
6. **Seal the prediction.** Written to disk, dated, before the run. Amending it voids the run.

## 9 · Exit criteria — how to know this has gone wrong

The vault has failed, and should be closed, if any of these are true:

- It is more enjoyable to write than to act on.
- More than 30 days pass with no `RETIRED` entry.
- An entry is cited in a bio, a pitch, or a public post.
- A pattern survives longer than its falsifier window without being tested.
- You find yourself writing a *new* pattern instead of testing an old one, twice in a row.
- The insight has stopped changing what another person has to absorb.

The correct response to any of these is not more analysis. It is `docs/METHOD.md §10`.

## 10 · The one-thing rule

From `ZP-SRC-02`: at moments of overwhelm the subject needs *explicit, low-shame instructions, a
small number of choices, and one clear next step.*

So when the vault is open and nothing is moving, the only permitted action is:

> Close every file. Pick the oldest untested pattern in `patterns/INDEX.md`. Run its falsifier test.
> That is the whole session.

Not a new chamber. Not a new archetype. Not a new experiment. One test, one result, one log line.

## 11 · Limits

This is not therapy, not a clinical instrument, and not a substitute for either. It does not
diagnose. It does not evaluate real third parties. The personas in `ZP-SRC-05` §6–§13 are fictional
composites and remain fictional. Where the subject's own documents carry a caution — non-clinical,
no motive-inference, perception-not-conduct, calibration against paranoia and false positives
(`ZP-SRC-05` §24) — that caution is inherited here in full and is not optional.

---
*Method v1 · 2026-08-27 · revision logged, not replaced.*
