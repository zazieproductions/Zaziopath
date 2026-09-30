# ⚛️ PARTICLE COLLIDER — Cross-Stratum Experiments

> **Dated 2026-09-30.** Instrument `ZP-PC-2026-0930` · seed `20260930` · α = 0.05, family-wise α = 0.05/13 = **0.0038**
> **State:** 13 beams fired · **3 HOLD · 9 SNAP · 1 NO-BEAM** · engine `tools/particle_collider.py` · machine log `docs/collider/beam_log.json` · figure `docs/figures/fig9_beamline.png` (FIG 9)
> **Standing rule of this chamber:** *never promote an aesthetic coincidence into evidence without testing it.* Every number below is re-derivable from primary files by re-running the engine. Anything that looked beautiful and died under its null is recorded here with its corpse intact.

---

## §0 · The question the chamber asks

Take one artifact from one guild-chamber (README §00a) and one from a **distant** chamber. Collide them. Ask a single question:

> does combining these two datasets reveal a relationship **neither contains individually**?

Not "do they rhyme." Not "would they make a good essay." *Does the join produce a quantity, a disagreement, or a falsifier that neither side could state alone?* The vault is full of documents that sound like each other. Sounding alike is the cheapest signal in the building and it is worth nothing until it survives a null.

Three design commitments follow, and they are mechanical, not rhetorical:

1. **Random selection.** Pairs come from a seeded blind draw over the eligible pair-space (§2), not from a curator's taste. Targeted beams are allowed but must be declared as targeted, and they pay the same α as everyone else.
2. **Distance gate.** A collision between two artifacts already wired together (README §00c, 🔍 CASE FILE findings F-01…F-10, ⚡ Unexpected Connections) is not an experiment, it is a rerun. Those pairs are vetoed (§1).
3. **Failures are the measurement.** A collider that only reports hits is a confession machine. Every SNAP and NO-BEAM below is logged with its failure class, and §5 argues from the failure rate itself.

Verdicts, fixed before firing:

| verdict | meaning |
|---|---|
| ✓ **HOLD** | a quantity or relation present in neither source alone, reproducible from primary files, with a stated falsifier. Survives α = 0.0038. |
| ✗ **SNAP** | the beam fired and the null won — or a negative control reproduced the effect from something arbitrary. The hypothesis is dead; whatever survived the blast is itemized. |
| ⊘ **NO-BEAM** | nothing survived triage: no shared referent, an unreplicated source, or the instrument failed its own validity gate. Not a failed experiment — an experiment that could not be built. |
| ◷ **PENDING** | the beam is a clock and its window has not closed. (None currently; C-05's window closes 2026-10-02 and its *referent* claim is adjudicated now, its *prediction* later.) |

Failure classes used in §3: **F1** fragile hinge · **F2** no shared referent · **F3** unreplicated source · **F4** no dates · **F5** confound reproduced by an arbitrary battery · **F7** null wins · **F9** instrument invalid.

---

## §1 · The pool, the strata, and the distance gate

The collider's census (`inventory()` in the engine) assigns every committed artifact to exactly one of the eight chambers and counts how many **independent observations** it actually carries — rows, records, dated entries, test scores — as opposed to how many sentences it contains.

| chip | stratum | pool artifacts | what counts as an observation here |
|---|---|---|---|
| ⬛◈ | INDEX & META | 22 | catalog rows cited, wikilinks, claim-ledger entries, figure counts |
| 🟦 | IDENTITY | 14 | test scores, CV lines, named roles |
| 🟪◐ | SHADOW | 21 | dated journal entries, named sessions |
| 🟧 | SIGNAL / EVIDENCE | 9 | catalog rows (182 CSV / 200 XLSX), census records (133), exhibits (106) |
| 🟩∞ | RECURSION LAB | 20 | loop iterations, dated receipts, excavation counts |
| 🔷△ | STEWARDSHIP | 4 | stewardship lines, receipt fields |
| 🟥⚠ | SPECIMENS | 9 | specimen records, glossary terms, template postures |
| 🟨☾ | MYTHOGRAPHY | 18 | named entities, mythic places, tale beats |

**Topology, 2026-09-30** (`topology()`): pool **117** artifacts · independent populations **7** · lexicon sources **108** · chronologies **4** · **110 of 117 (94.0%)** artifacts carry exactly one observation and therefore can never support a within-source test · eligible distant pairs **3,276** · beam-capable pairs **525 (16.03%)** · pairs that would need a population on *both* sides: **12**.

The distance gate. Chambers sit on a declared distance matrix (d = 2 for adjacent rings, d = 99 for diametric pairs; full matrix in the log). A pair is eligible only if d ≥ 2 **and** it is not already wired:

| veto | pairs removed | why |
|---|---|---|
| same stratum | 953 | a chamber colliding with itself is a mirror, not an experiment |
| too close (d < 2) | 2,491 | adjacent chambers share register by construction |
| already analyzed together | 66 | README §00c wires, 🔍 F-01…F-10, ⚡ prose wires — reruns are vetoed |
| **eligible** | **3,276** | |

Beam-feasibility triage then asks what a pair could even support: **T** (two populations to test against each other), **L** (a join key with rows on both sides), **C** (a chronology on one side and datable events on the other), **S** (single-observation prose on both sides → review required, never a statistic). 525 pairs carry T/L/C; 1,157 are S-on-one-side and need human review before any number is quoted; 1,594 cannot candidate at all. **This is the first result of the collider: 84% of the vault's distant pair-space cannot be collided quantitatively, and 94% of its artifacts are n = 1.** The vault is wide, not deep.

---

## §2 · The blind draw, 2026-09-30

Seed `20260930`, 24 draws without replacement from the 3,276 eligible pairs (pair-list digest `sha16:45721d1455c6c387` in the log). Nineteen draws die at triage; five are promoted; two of those five die at review. The table is the audit trail — the dead draws are the point.

| # | crossed | d | obs A/B | dates A/B | triage | disposition |
|---|---|---|---|---|---|---|
| 1 | 🟥⚠ Personal Branding as Class War Psy-Ops × 🔷△ verdict_from_A.i | 2 | 1/1 | 0/1 | — | S/S: two single-observation prose artifacts, no population, no dates → not a beam |
| 2 | ⬛◈ META_ANALYSIS_OF_ZAZIOPATH × 🟪 XRay_Two_Voices.pdf | 99 | 1/1 | 1/0 | — | S/S, one chronology but nothing datable on the other side |
| 3 | ⬛◈ VISITORS_NOTEBOOK.md × 🔷△ verdict_from_A.i_6 | 99 | 1/1 | 2/1 | — | S/S; two dates against one undated verdict |
| 4 | 🟧 Discography.csv × ⬛◈  Major Knowledge Graph | 99 | 182/1 | 21/1 | L | → **beam C-12** |
| 5 | ⬛◈ DEEP_GAP_AUDIT × 🟩 EXCAVATION_REPORT_ZP-6026 | 99 | 1/1 | 1/0 | — | S/S |
| 6 | 🟪◐ Velvet_Knife_The_Synthetic_Mirror × ⬛◈ exhibit_verification.json | 99 | 1/106 | 0/6 | L | ⊘ review-kill **F2**: the prose contains 0 hits for "exhibit", "hearing", "verification" — the join key lives on one side only |
| 7 | 🟩∞ GPT 7.7-t Surveillance Subroutines × 🔷△ OmniCipher_Signal_Codex | 2 | 1/1 | 0/0 | — | S/S, no dates |
| 8 | ⬛◈ VISITORS_NOTEBOOK.pdf × 🔷△ verdict_from_A.i_5 | 99 | 1/1 | 1/0 | — | S/S |
| 9 | 🟥⚠ Social Engineering Email Templates × 🟩∞ EXCAVATION_REPORT | 2 | 1/1 | 0/0 | — | S/S |
| 10 | 🟧▤ Zazie_Media_Master (1).pdf × ⬛◈ exhibit_verification.json | 99 | 133/106 | 27/6 | T | ⊘ review-kill **F2**: the join collapses to 4 rows; 133 records against 106 exhibits with no stable key between them |
| 11 | 🟧▤ Complete_Discography.xlsx × 🟩∞ EXCAVATION_REPORT | 2 | 200/1 | 1/0 | L | → **beam C-03** |
| 12 | 🟪◐ Velvet_Knife_Behind_The_Screen × ⬛ ⚡ Unexpected Connections | 99 | 1/1 | 0/1 | — | S/S |
| 13 | ⬛◈ META_ANALYST_OF_INTERPRETATIONS × 🟦◉ Artist_CV_2026 | 99 | 1/1 | 0/0 | — | S/S |
| 14 | 🟧▤ ALBUM STRUCTURE 4×3 FRACTAL MODULES × 🔷△ verdict_from_A.i_5 | 2 | 1/1 | 0/1 | — | S/S |
| 15 | ⬛◈ ANTHROPOLOGICAL_FIELD_REPORT_ZP-01 × 🟪◐ Velvet_Knife_Hidden_Desires | 99 | 1/1 | 0/0 | — | S/S |
| 16 | 🟪◐ The_Architecture_of_Being_Seen × ⬛ ⚡ Unexpected Connections | 99 | 1/1 | 0/1 | — | S/S |
| 17 | 🟦◉ Artist_CV_2026.pdf × ⬛◈ ⚡ Unexpected Connections | 99 | 1/1 | 0/1 | — | S/S |
| 18 | 🟪◐ XRay_Two_Voices.pdf × ⬛◈ ⚡ Unexpected Connections | 99 | 1/1 | 0/1 | — | S/S |
| 19 | ⬛◈ EVIDENCE_GOVERNANCE_HANDBOOK × 🟧▤ Complete_Discography.xlsx | 99 | 1/200 | 2/1 | L | → **beam C-02** |
| 20 | 🟦◉ Philosopher Personality Test × ⬛◈ create a link.md | 99 | 1/1 | 0/0 | — | S/S |
| 21 | 🟩∞ EXCAVATION_REPORT × 🟧▤ text.txt | 2 | 1/1 | 0/0 | — | S/S |
| 22 | 🟨☾ The_Sound_That_Swallowed_April.docx × 🟪◐ The_Analyst_Becomes_Evidence | 2 | 1/1 | 0/0 | — | S/S |
| 23 | 🟨☾ Mythographic Childhood × 🟪◐ Shadow Journal Observations | 2 | 1/1 | 0/0 | — | S/S |
| 24 | 🟪◐ ANATOMIA_CONTRADICTIONIS × ⬛◈ META-ANALYSIS Verdict Corpus | 99 | 1/1 | 1/4 | — | S/S |

**5 of 24 draws (20.8%) were beam-capable; 3 of 24 (12.5%) became beams.** The other ten beams in §3 are *declared targeted* collisions — the user's brief named candidate formats (`ISRC metadata × rejection sensitivity`, `track duration × administrative behavior`, `Munnytown mythology × release chronology`, `GitHub architecture × composition structure`, `press archive × linguistic vocabulary`) and each is fired below under its own id, flagged TARGETED, paying the same α. Targeted beams are how the brief's hypotheses get tested; the blind draw is how the vault gets to refuse them company.

---

## §3 · The beams

Thirteen beams. Each entry states the pre-registered hypothesis, the measurement, the null, and the verdict. Failure class in the header where the beam died.

---

### C-01 · ✓ HOLD · 🟧▤ press census × 🟥⚠ legitimacy classifier · *targeted*

**Crossed:** `Zazie_Media_Master (1).pdf` (133 URL-level press records, priority A/B/C) × `nuqkL_…pdf` SIGNAL-STACKING (Tier 1/2/3 gate-test classifier with named examples).

**Hypothesis (pre-registered):** the census's own priority letters and the specimen's tier classifier disagree, and the disagreement is *concentrated* in one identifiable block rather than spread evenly.

**Measurement:** parse both classifiers over the same 133 records (parse check: A23/B26/C84 = the census's own executive summary ✓). Cross-tabulate priority × tier over the 128 resolvable records; permute the tier labels 4,000 times.

**What neither source contains alone:**
- Exact agreement 32.0%; **κ = 0.0023** (chance) under the reading that compilation records are Tier 1, but **κ = 0.507** (moderate) under Tier 3 — the entire verdict rides on **60 Discogs-appearance records (45.1% of the census)** whose tier the specimen never names. The hinge is one interpretive choice about one platform family.
- The concentration is real and one-sided: **59 of 84 Priority-C records (70.2%) sit in Tier 1** — the census files Discogs indexes as lowest priority while the gate-test's own doctrine would rank an independent editorial index highest. Five Priority-A records are unresolvable under any tier reading.
- Institution inflation is measurable but small: 133 records → 105 distinct institutions → 102 distinct works; **inflation factor 1.023** at platform level, i.e. the census double-counts platforms, not press.

**Verdict HOLD.** The κ-hinge is a new quantity: it exists in neither document, is reproducible from the two primary files, and its falsifier is explicit — *if the SIGNAL-STACKing author ever names a tier for Discogs appearance indexes, κ collapses to one of {0.002, 0.507} and the hinge vanishes.* Feeds **RP-1**.

---

### C-02 · ✗ SNAP · F5 genre confound · ⬛◈ custody handbook × 🟧 catalog · *from draw 19*

**Crossed:** `EVIDENCE_GOVERNANCE_HANDBOOK.md` (seven chain-of-custody elements) × `Zazie_Productions_Complete_Discography.xlsx` (200 rows), scored across all 117 pool artifacts.

**Hypothesis (pre-registered):** custody compliance falls as an artifact gets closer to raw data — INDEX out-scores EVIDENCE on the handbook's own seven elements.

**Measurement:** score every artifact 0–7 on the handbook's elements; INDEX mean 4.82 (n=22) vs EVIDENCE mean 3.11 (n=9), difference 1.71, shuffle-split permutation p = 0.048. Citation count vs custody score: Spearman ρ = 0.020 (p = 0.58).

**What killed it:** negative control **NC-3** (§4). An *arbitrary* seven-feature battery (mermaid blocks, emoji, tables, URLs, code fences, blockquotes, front-matter) separates the same two chambers **more strongly** (INDEX 2.50 vs EVIDENCE 0.89, p = 0.002) than the handbook's own battery does. The handbook battery is measuring *document genre* — indexes are structurally list-like — not governance. Within EVIDENCE itself, primary data (3.50) vs audit prose (3.00) shows the predicted gradient inverted and null (p = 0.63).

**Verdict SNAP (F5).** Residue that survived the blast, itemized for RP-2's maintenance list: the CSV carries 1 of the handbook's 7 custody elements vs the XLSX's 6; the two catalog files disagree on row count (182 vs 200) with no reconciliation record; and only **4 of 8 headline numbers** in the vault ("200 tracks" ✓, "165 verified ISRCs" ✗, "133 URL-level records" ✗, "92 removed stubs" ✓, "336-note parent vault" ✗, "58 Discogs appearances" ✓, "≈250 archetypes" ✓, "12,000 followers" ✗) have a claim record in `CLAIM_PROVENANCE_LEDGER.md`.

---

### C-03 · ✗ SNAP · F7 · 🟩∞ excavation census × 🟧 catalog · *from draw 11*

**Crossed:** `docs/excavation/EXCAVATION_REPORT_ZP-6026.md` (15 numeric census claims) × the XLSX catalog as ground truth.

**Hypothesis (pre-registered):** the report's numbers are exact where it repeats a number the vault already asserted, and wrong where it had to count for itself.

**Measurement:** re-count all 15 claims from primary files; classify each claim as asserted-elsewhere (context regex over the corpus) or self-counted; compare error rates.

**Result:** 6 of 15 exact (40.0%); mean relative error when wrong **46.6%**. But asserted-elsewhere rate is **83.3% when exact vs 88.9% when wrong** — the mechanism the hypothesis names does not exist. Wrongness is unrelated to citation.

**Verdict SNAP (F7).** The hypothesis dies; a **defect list survives**: 8 mis-counted figures in the excavation report are corrected in the log (`rows[]` with observed vs recounted values) and belong on the maintenance docket, not in the findings shelf.

---

### C-04 · ✗ SNAP · F7 · 🟧▤ ISRC gaps × ⬛◈ wikilink gaps · *targeted*

**Crossed:** `Zazie_Productions_Discography.csv` (21 missing ISRCs over 182 rows, 21 releases) × `🗄 Stub Registry.md` + the wikilink graph (492 dangling of 601 link instances over 27 units).

**Hypothesis (pre-registered):** both recording systems *batch* their omissions — gaps over-disperse across units in the same geometry.

**Measurement:** per-unit gap counts vs a multinomial permutation null, two statistics each side (top-decile share; count of all-gap units).

**Result:** the two systems have **opposite geometries**. Catalog gaps batch hard: 3 releases are entirely gap (null mean 0.38, **p = 0.0027**). Link gaps *anti-batch*: only 2 all-dangling units against a null mean of 12.35 (p = 1.0), dispersion index D = 0.34 — dangling links are spread almost uniformly, because every unit dutifully links its own dead stubs. The catalog's top-decile concentration (52.4%, p = 0.07) and the graph's (86.6%, p < 0.001) point the same way only until you look at unit level, where they invert.

**Verdict SNAP (F7).** A shared aesthetic ("both files are full of holes") dissolves into two different recording diseases: batch failure at intake (catalog) vs uniform optimistic linking (graph). Recorded, not promoted.

---

### C-05 · ✓ HOLD · 🟩∞ Prediction B × 🟧▤ catalog numbering · *targeted*

**Crossed:** `verdict_from_A.i_5/_6` (Prediction B, window opened 2026-09-02) × the XLSX/CSV catalog.

**Hypothesis (pre-registered):** Prediction B's three conditions are each evaluable from committed artifacts today, and its falsifier "track #201 appears" points at a real slot in the catalog's own numbering.

**Measurement at day 28 (window closes 2026-10-02):** condition A — 13 stewardship lines, **0 filled** (the two receipt-form artifacts committed since the ledger, `VISITORS_NOTEBOOK.md/.pdf`, fill none of them); condition B — **0 new tracks** after the ledger date (CSV's last release 2026-05-19); condition C — **0 rate claims** committed post-ledger. Prediction B: **0 of 3 conditions met**. Accretion audit: **18 artifacts, 456,055 bytes added, 0 deletions, 0.643 artifacts/day** since 2026-09-02 — the vault is growing while the prediction's conditions stay unmet.

**What neither source contains alone:** the falsifier's *referent* is broken. The XLSX numbers rows to 200, but rows 198–200 are compilation/summary rows; **the last real track is #197**. "Track #201 appears" therefore does not mean "one new track" — it means **four new numbered releases' worth of distance**, or a renumbering. A falsifier whose trigger is four releases away is not a 30-day falsifier.

**Verdict HOLD.** Two new, dated, reproducible quantities: (i) Prediction B stands at 0/3 with 2 days of window left and an accretion rate that makes condition A increasingly unlikely; (ii) the #201 mis-reference, with its exact arithmetic (197 vs 201). Falsifier for (ii): *a committed catalog in which #201 is a real track slot restores the original reading.* Feeds **RP-2**.

---

### C-06 · ✗ SNAP · F7 · 🟦◉ moral foundations × ⬛◈ prose corpus · *targeted*

**Crossed:** `6Foundations 2.pdf` (Care 8, Fairness 6, Loyalty 6, Authority 6, Sanctity 6, **Liberty 30** of 30) × the vault's prose corpus (109 documents, 225,716 words).

**Hypothesis (pre-registered):** the corpus enacts the subject's scores — Liberty vocabulary denser than Care vocabulary, density order tracking score order.

**Measurement:** six distinctive-lexicons (TF-IDF-weighted over the corpus), density per 10k words, Spearman of density-rank vs score-rank over 720 possible permutations.

**Result:** ρ = 0.541, **p = 0.133** — dead at α = 0.0038, and directionally the pre-registered contrast *inverts*: **Care is the densest foundation in the corpus (46.7/10k) despite being near the bottom of the scores (8/30)**, while Liberty sits at 22.1/10k. Amplification score→text = 0.13, i.e. attenuation. The corpus's care-lexicon overlaps the vault's horror register ("wound", "tenderness", "harm"), which is a genre fact, not a moral one.

**Verdict SNAP (F7).** The profile does not leak into the prose. The inversion is recorded because it is the kind of coincidence that would have made a gorgeous wire and would have been false.

---

### C-07 · ✗ SNAP · F7 · 🟨☾ myth lexicon × 🟧 track titles · *targeted (Munnytown mythology × release chronology, half 1)*

**Crossed:** seven ☾ mythography artifacts (pooled distinctive lexicon, 100 terms) × 203 catalog objects' titles.

**Hypothesis (pre-registered):** mythic vocabulary and proper names appear in track titles above the frequency-matched chance rate.

**Result:** **0 of 203 titles** hit (null mean 1.45, p = 1.0). All **12 proper names zero**: Munnytown, Bunnytown, glocht, Vespertine, Tuffy, Hubris, Babyheart, Tweak Tweak, Anémone, Crottin, hypersigil, Negative Observatory. Self-rank gate passes (☾ sources rank #1 of 112 for their own lexicon), so the instrument was able to see transfer and saw none.

**Verdict SNAP (F7).** The mythology and the catalog do not share vocabulary. The chronology half of the brief's pair is adjudicated in C-11.

---

### C-07b · ✗ SNAP · F7 · all eight chambers × 🟧▤ titles · *targeted, contamination audit*

**Crossed:** each stratum's pooled prose (8 beams, 100-term lexicons each) × 182 CSV titles.

**Hypothesis (pre-registered):** F-10's claim that catalog and vault are "the same document in two file formats" holds at vocabulary level: every chamber's distinctive lexicon should transfer into titles above chance.

**Result:** six chambers 0 hits (p = 1.0). EVIDENCE shows 14 hits at p < 0.001 — **and every one is contamination**: the hitting sources are the XLSX itself and case-file documents that *quote track titles*. Remove the catalog-quoting documents and EVIDENCE falls to 0 hits (p = 1.0). STEWARDSHIP's 7 hits (p = 0.10) are a near-miss on one idiom ("pivot and deflect").

**Verdict SNAP (F7).** Zero genuine lexical transfer from any of the eight chambers into the catalog. The contamination episode is itself a holding-grade lesson for the instrument: *a lexicon beam pointed at a corpus that quotes its own target measures quotation, not transfer* — now a standing exclusion in the engine (`CATALOG_QUOTING` set).

---

### C-08 · ✗ SNAP · F7 · 🟥⚠ scam glossary × 🟧▤ press census · *targeted (press archive × linguistic vocabulary)*

**Crossed:** `online-presence-pr-seo-scam-vocabulary.pdf` (288 defined mechanism terms) × `Zazie_Media_Master (1).pdf`.

**Hypothesis (pre-registered):** the census is written in the mechanism vocabulary the specimen cabinet defines.

**Result:** only **4 of 288 terms** appear in the census at all; density rank **61 of 112** artifacts (p = 0.54). Controls: the README ranks 10 and the Instagram audit 76 for the same glossary — the census is not even the vault's most glossary-fluent document. Doctrine-level overlap is two sentences of qualitative resemblance, recorded in the log as prose, not evidence.

**Verdict SNAP (F7).** The census describes platforms; it does not speak mechanism. Self-rank gate passes (glossary ranks #1 for itself), so this is a clean null.

---

### C-09 · ✓ HOLD · 🔷△ receipt console × 🟩∞ stewardship lines · *targeted*

**Crossed:** `stewardship_receipt.html` (the vault's filing console: fields action/date/evidence + 3 required) × `verdict_from_A.i_4` (13 unfilled `2026-09-__` stewardship lines).

**Hypothesis (pre-registered):** the tribunal's thirteen lines can be filed in the vault's own console *without modification*.

**Measurement:** schema crosswalk, field by field, over all 13 lines.

**What neither source contains alone:** **0 of 13 lines are filing-ready.** The console requires `evidence`; the ledger format never emits an evidence field (0 of 13 lines carry one); overlap exists only on `action` and `date`. The vault's action pipeline has two dialects that cannot read each other, and the gap is exactly one field wide.

**Verdict HOLD.** The incompatibility is a structural fact about the vault, reproducible by opening the two files; it is dated today; and it has a falsifier — *any committed ledger line that the console accepts without edit falsifies the "never emits" claim.* Feeds **RP-3**.

---

### C-10 · ⊘ NO-BEAM · F9 instrument invalid · 🟥⚠ posture markers × 🟧▤ census · *targeted*

**Crossed:** `Social Engineering Email Templates .md` (six annotated outreach postures, 34 markers) × the Media Master census.

**Hypothesis (pre-registered):** the census's press-facing language carries the six postures above chance.

**Why no beam:** the validity gate fired first. The census ranks **8 of 112** for the marker list (p = 0.071, already null), but the templates' *own source document* ranks only **10 of 112** for its own markers (2,753 chars of template prose scoring below the census). A marker list that does not identify its own home document measures *promotional register*, which the census and the templates share by genre, not posture. The instrument is invalid; firing it would have produced a number about nothing.

**Verdict NO-BEAM (F9).** Recorded because the temptation was strong: rank 8 looks like a hit until the gate asks who else scores high.

---

### C-11 · ✗ SNAP · F7 · 🟧▤ release attention × ⬛◈∞ corpus mentions · *targeted (Munnytown half 2 / ISRC × attention)*

**Crossed:** 21 releases with per-release ISRC gap rates (from the CSV) × mention counts across the whole prose corpus.

**Hypothesis (pre-registered):** poorly-registered releases get measurably more prose attention (compensation) or less (avoidance).

**Result:** all correlations null in both directions — gap rate ρ = −0.103 (p = 0.66), track count ρ = −0.023 (p = 0.92), corpus section count ρ = −0.036 (p = 0.88). Three releases receive **zero** mentions anywhere in the prose; the most-mentioned releases are not the gap-rich ones.

**Verdict SNAP (F7).** Identifier hygiene and narrative attention are independent in this vault. The aesthetic ("the neglected albums are the unregistered ones") is recorded as dead.

---

### C-12 · ✗ SNAP · F7 · ⬛◈ knowledge graph × 🟧▤ catalog · *from draw 4 (GitHub architecture × composition structure, proxy pair)*

**Crossed:** `🕸 Major Knowledge Graph.md` (77 named nodes) × 203 catalog objects.

**Hypothesis (pre-registered):** the practice graph and the catalog name some of the same objects.

**Result:** **0 exact and 0 substring matches** across all 77 × 203 name pairs. The graph's vocabulary is process-and-people; the catalog's is titles-and-releases. Transfer rate 0.0.

**Verdict SNAP (F7).** The vault's self-map and the vault's output do not share a single named object. The brief's "GitHub architecture × composition structure" collision is adjudicated here and in C-02's custody residue: the architecture documents describe practice, the catalog describes product, and no join key exists between them.

---

## §4 · Negative controls — the instrument tested on itself

A collider that has never been pointed at a known answer cannot distinguish a null from a broken detector. Three controls, all in the log:

**NC-1 · false-positive rate of the lexicon-transfer beam.** Re-aim the C-07/C-07b beam machinery at **19 usable documents of known provenance** (each document's own distinctive lexicon, re-tested against the corpus). Result: **0 false positives at p < 0.05 across the 18 non-degenerate sources** (the 19th, the catalog scored against itself, matches trivially and is excluded by rule as a degenerate self-source). Mean observed hits 2.37 vs null mean 4.42 — the beam is if anything conservative. *The instrument does not invent transfer.*

**NC-2 · the self-rank gate.** For TF-IDF-built lexicons the gate passes 19/19 (circular by construction) — so the gate is load-bearing **only for hand-authored marker lists**, which is exactly where it fired: it killed **C-10**. A validity gate whose only job is to catch hand-made instruments is not a decorative gate.

**NC-3 · the arbitrary battery.** Seven features no governance document cares about (mermaid blocks, emoji, tables, URLs, code fences, blockquotes, front-matter) scored across all 117 artifacts separate INDEX from EVIDENCE at **p = 0.002** (2.50 vs 0.89) — *more strongly* than the handbook's own seven custody elements (p = 0.048). Therefore any INDEX-vs-EVIDENCE difference measured by a seven-item battery is uninterpretable without this control. **This control is what snapped C-02.**

---

## §5 · Tally, and why the failure rate is the result

| verdict | n | beams |
|---|---|---|
| ✓ HOLD | 3 | C-01, C-05, C-09 |
| ✗ SNAP | 9 | C-02, C-03, C-04, C-06, C-07, C-07b, C-08, C-11, C-12 |
| ⊘ NO-BEAM | 1 | C-10 |
| ◷ PENDING | 0 | — |

**13 beams, 3 holds: a 77% failure rate, and that rate is the finding.** The vault's chambers are aesthetically continuous and statistically independent: they share register, palette, and obsession, and they share almost no transferable signal. Nine of thirteen collisions produced a clean null from a well-powered instrument; one produced an instrument too invalid to fire; three produced quantities that did not exist before the collision (a κ-hinge, a broken falsifier referent, a one-field schema gap).

Two structural facts from §1 explain most of the snaps without appeal to chance: **94% of artifacts are n = 1**, so most pairs have no within-source variance to test, and **only 12 eligible pairs put a population on both sides**, so most "relationships" between chambers are relationships between two single observations — moods, in the vault's own grammar. *An undated, unreplicated insight is a mood; this document is the machine that says so out loud.*

The three holds share a shape worth naming: **none of them is a correlation.** They are a hinge (C-01: one interpretive choice flipping κ from chance to moderate), a referent audit (C-05: arithmetic inside a falsifier), and a schema incompatibility (C-09: a missing field). The vault yields structure under collision, not covariance.

---

## §6 · Candidate research programs (holds only)

Only tested, surviving collisions are promoted. Each program states its first experiment and its falsifier.

**RP-1 · Two-axis legitimacy accounting** (from C-01). The census's priority axis and the gate-test's tier axis disagree by design, with a 60-record hinge. *First experiment:* re-score the 60 Discogs-appearance records under both doctrines and publish the κ interval [0.002, 0.507] as the vault's stated uncertainty about its own press record. *Falsifier:* a named tier for Discogs indexes in any committed specimen collapses the interval.

**RP-2 · Falsifier maintenance** (from C-05, plus C-02's residue). Committed predictions carry falsifiers whose referents drift ("track #201" is four releases away; headline numbers lack claim records). *First experiment:* a dated register mapping every committed falsifier to its current referent slot, re-audited each accretion event (current rate 0.643 artifacts/day). *Falsifier:* any falsifier whose referent resolves unambiguously without audit.

**RP-3 · Schema unification of the action pipeline** (from C-09). The console and the ledger disagree by exactly one required field (`evidence`). *First experiment:* extend the ledger format with an `evidence` slot and re-file all 13 stewardship lines; count how many become filing-ready. *Falsifier:* a committed ledger line the console accepts unmodified today.

---

## §7 · What the collider refuses to claim

Recorded so the temptations stay dead:

- *"The census speaks the scam glossary."* — 4/288 terms, rank 61/112 (C-08).
- *"Munnytown leaks into the tracklist."* — 0/203 titles, 0/12 proper names (C-07); 0/8 chambers transfer (C-07b).
- *"The vault's prose enacts its moral profile."* — ρ = 0.54, p = 0.13, contrast inverted (C-06).
- *"Both files batch their holes."* — opposite geometries (C-04).
- *"Governance decays toward raw data."* — an emoji-and-front-matter battery beats the handbook at its own claim (C-02, NC-3).
- *"The neglected releases are the unregistered ones."* — all |ρ| ≤ 0.11 (C-11).
- *"The census carries outreach posture."* — the instrument fails its own gate (C-10).
- *"The excavation counts carefully when it cites."* — wrongness unrelated to citation (C-03).
- *"The graph maps the catalog."* — zero shared names (C-12).
- *"EVIDENCE vocabulary transfers into titles!"* — quotation, not transfer; removed, it vanishes (C-07b).

---

## §8 · Reproduction

```bash
python3 tools/particle_collider.py                # full run: census, draw, 13 beams, 3 controls, FIG 9
python3 tools/particle_collider.py --no-figure
python3 tools/particle_collider.py --render-only  # redraw FIG 9 from the committed log
```

The engine is **pinned to this report's census** (`CENSUS_PIN_MD`, the 43 root/docs markdown
files as committed at `3f78d7a`). Because `wikilinks()` reads every markdown file in the tree,
a vault that gains a document would silently change C-04's link geometry on a naive re-run;
on a moved census a full run therefore refuses with `CENSUS MOVED` and exits non-zero.
`--recensus` acknowledges that the run belongs to a *new* report id — a dated experiment
does not get re-measured behind its own back.

Outputs: `docs/collider/beam_log.json` (every statistic above, plus the 117-artifact inventory, the distance matrix, the veto register and the draw dispositions) and `docs/figures/fig9_beamline.png`. Seed `20260930` fixes the draw; permutation p-values use 4,000 shuffles (400 for NC-1). Text extraction needs `pypdf`; the text cache lives in `$TMPDIR/zaziopath_collider_text`, never in the repo.

Cross-references: chambers and chips README §00a · existing wires README §00c (this document adds three: C-01's κ-hinge, C-05's referent break, C-09's schema gap — all dated 2026-09-30 and tested) · tested findings 🔍 CASE FILE F-01…F-10 (not re-derived here; C-07b audits F-10's vocabulary claim and finds it does not hold at lexicon level) · untested prose wires ⚡ Unexpected Connections (veto source, §1).

*Dated 2026-09-30. The chamber is idle; the window on C-05's prediction closes 2026-10-02 and will be re-read then.*
