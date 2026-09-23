# Zaziopath Evidence Governance Handbook

**Version:** 0.1  
**Date:** 2026-09-23  
**Purpose:** Convert the findings of `DEEP_GAP_AUDIT.md` into repeatable documentation standards.

---

# 1. Governing Principle

A claim does not become evidence because it is dated, linked, diagrammed, repeated, or written in forensic language. Every consequential claim must preserve a route back to:

1. the exact source version;
2. the type of source;
3. the transformation applied to it;
4. the person or system responsible for that transformation;
5. the claim’s independence from other claims;
6. competing explanations;
7. its present verification and correction state.

The vault should preserve not only conclusions, but the **chain of custody of meaning**.

---

# 2. Controlled Vocabulary

## 2.1 Source type

Use exactly one primary value and optional secondary values.

| Value | Definition |
|---|---|
| `structured_catalog` | CSV, database, spreadsheet, or other row-based record |
| `public_record` | Public page, registry, article, listing, or externally published artifact |
| `private_record` | Email, invoice, message, calendar, local log, or unpublished document |
| `self_report` | Statement about the speaker’s own experience or history |
| `third_party_report` | Statement supplied by another person |
| `model_memory_summary` | Assistant-generated memory or longitudinal summary |
| `generated_interpretation` | AI or human interpretation derived from other material |
| `software_behavior` | Behavior directly observed in code or execution |
| `fiction` | Material presented as invented narrative or worldbuilding |
| `hybrid` | Deliberate mixture of factual and fictional modes |
| `unknown` | Provenance cannot presently be established |

## 2.2 Claim level

| Value | Test |
|---|---|
| `observation` | What is literally present or happened during a reproducible check? |
| `summary` | What does a bounded set of observations contain in aggregate? |
| `interpretation` | What might those observations mean? |
| `causal_explanation` | What allegedly produced the observed pattern? |
| `prediction` | What should happen if the interpretation is correct? |
| `recommendation` | What action is proposed? |

Never label an interpretation as an observation merely because the interpretation is quoted directly from a source.

## 2.3 Independence

| Value | Definition |
|---|---|
| `primary` | The source directly contains the material being described |
| `independent` | Reached without exposure to the originating claim or source |
| `partly_independent` | Uses some shared material but adds distinct evidence |
| `derived` | Produced from identified earlier sources |
| `repeated` | Restates a claim without new evidence |
| `contaminated` | Independence cannot be claimed because prior framing was supplied |
| `unknown` | Dependency cannot be reconstructed |

## 2.4 Verification state

- `reproduced`
- `externally_verified`
- `internally_consistent`
- `not_rerun`
- `untested`
- `partly_contradicted`
- `contradicted`
- `inaccessible`
- `superseded`

## 2.5 Correction state

- `active`
- `disputed`
- `superseded`
- `retracted`
- `fictional`
- `expired`

## 2.6 Sensitivity

- `public`
- `internal`
- `sensitive`
- `restricted`

Do not infer sensitivity from repository visibility. Classify the information itself.

---

# 3. Claim Record Standard

Every claim important enough to enter the README, a case file, or a generated figure should have this minimum structure:

```yaml
claim_id: ZP-CLM-0001
statement: "One clear, falsifiable sentence."
claim_level: observation
status: active
confidence: strong
created_at: 2026-09-23
last_reviewed_at: 2026-09-23
expires_at: null

sources:
  - path: README.md
    git_blob: 0600a24d851404901ede3fcc8f2eedcbdee5d113
    sha256: f09a1f5f4375ecb1e7592460348e3e0b43dfd76af12c2737f5cf507070d198d1
    locator: "lines 179-182"
    source_type: self_report
    independence: primary

transformation:
  method: "Direct quotation and bounded paraphrase"
  performed_by: human
  tool_or_model: null
  prompt_id: null

verification:
  state: reproduced
  checked_by: repository audit
  checked_at: 2026-09-23

alternatives: []
falsifier: "A concrete observation that would make the claim false"
limitations: []
sensitivity: public
supersedes: null
superseded_by: null
```

## Required discipline

- One record should contain one proposition.
- Avoid conjunctions that hide multiple claims.
- State scope explicitly: “in the current repository,” not “in life.”
- State time explicitly when the claim may change.
- A missing value should be `null` or `unknown`, not omitted.

---

# 4. Source Citation Rules

## Rule 1 — Cite exact versions

For tracked files, include the Git blob hash. For exported or external files, add SHA-256.

A filename alone is insufficient because content can change without the prose citation changing.

## Rule 2 — Cite locations

Use:

- line range for text;
- row IDs for datasets;
- page and section for PDFs;
- function and line range for code;
- timestamp for audio/video;
- archived URL and retrieval date for web records.

## Rule 3 — Cite the earliest source

A README summary should not replace the artifact it summarizes. Cite both when useful, but mark the README as derived.

## Rule 4 — Preserve negative evidence boundaries

Write:

> “No exported stewardship receipt was located in the current tracked tree.”

Do not write:

> “No stewardship occurred.”

Absence must name the place searched, method used, and time of search.

## Rule 5 — Separate quote accuracy from claim truth

A quotation can be reproduced exactly while the statement quoted remains self-report, fiction, error, or inference.

---

# 5. Independence Audit

Before describing “convergence,” answer:

1. Did the analysts receive the same prompt?
2. Did they receive earlier analyses?
3. Did they read a README already summarizing the conclusion?
4. Did they use the same memory export or profile?
5. Did one analyst update files later analysts examined?
6. Did role prompts contain the expected conclusion?
7. Are different citations ultimately derived from one user statement?

## Convergence labels

### `independent_convergence`

Use only when analyses reach a similar proposition from distinct evidence without inheriting the proposition.

### `partial_convergence`

Use when evidence differs but framing or source material overlaps.

### `echo_convergence`

Use when analyses repeat inherited language, metaphors, or conclusions without new evidence.

### `manufactured_convergence`

Use when a handoff, role prompt, README summary, or curated source package directly preloads the conclusion later “discovered.”

---

# 6. AI-Assisted Artifact Standard

Every AI-assisted file should carry a provenance block.

```yaml
ai_provenance:
  classification: ai_generated_human_edited
  provider: unknown
  model: unknown
  session_date: 2026-09-02
  prompt_retained: partial
  source_commit: unknown
  prior_analyses_in_context:
    - verdict_from_A.i
    - verdict_from_A.i_2
  human_edits: unknown
  factual_review: partial
  limitations:
    - "Model reasoning reconstruction is not direct access to generation causes"
```

## Classifications

- `human_authored`
- `human_authored_ai_edited`
- `ai_drafted_human_rewritten`
- `ai_generated_human_edited`
- `ai_generated_unedited`
- `mixed_unknown`

## High-risk AI content

The following require explicit review:

- psychological motive claims;
- diagnosis-like language;
- claims about third parties;
- legal or financial assertions;
- security advice;
- historical facts;
- quantified repository facts;
- claims of model identity or training data.

---

# 7. Fiction, Record, and Hybrid Genre Labels

Every substantive artifact should use one:

```yaml
genre: record
```

```yaml
genre: self_report
```

```yaml
genre: prompted_interpretation
```

```yaml
genre: fiction
```

```yaml
genre: hybrid
factual_sections:
  - "Catalog dates"
fictional_sections:
  - "Recovered archive provenance"
```

A hybrid label must identify which factual claims remain intended for reliance.

---

# 8. Dataset Governance

## 8.1 Entity definitions

Before publishing a count, define its unit.

| Entity | Definition |
|---|---|
| Recording | One underlying audio recording or materially distinct version |
| Composition | One musical work, possibly represented by several recordings |
| Release | One issued album, EP, single, reissue, or compilation |
| Release appearance | One recording’s placement on one release |
| Credit | One person/project-role relationship to a recording or release |
| Public record | One verified external URL-level item under the census rules |

## 8.2 Stable identifiers

Assign internal IDs even when external IDs are absent:

- `ZP-REC-0001`
- `ZP-CMP-0001`
- `ZP-REL-0001`
- `ZP-APP-0001`
- `ZP-CRD-0001`

Never use titles as primary keys.

## 8.3 Missing-value policy

Use null plus a status field. Do not use `N/A` as if it were an identifier.

```yaml
isrc: null
isrc_status: not_found
```

## 8.4 Validation checks

At minimum:

- unique internal IDs;
- ISO dates parse;
- durations parse and are nonnegative;
- ISRC format is syntactically valid when present;
- duplicate ISRCs are reviewed rather than automatically rejected;
- release appearances point to existing releases and recordings;
- coverage denominators are named;
- source and verification dates are present.

---

# 9. Derived Artifact Build Standard

Each generated figure or report needs a build record.

```json
{
  "artifact": "docs/figures/fig3_isrc_forensics.png",
  "generator": "tools/generate_figures.py",
  "generator_git_blob": "<hash>",
  "inputs": [
    {
      "path": "Zazie_Productions_Discography.csv",
      "sha256": "268e396a10a59ab43ebd0289140a329286cd9cfb8b0baacf6025b7db186c1cab"
    }
  ],
  "environment": {
    "python": "<version>",
    "matplotlib": "<version>",
    "numpy": "<version>"
  },
  "generated_at": "<timestamp>",
  "output_sha256": "<hash>",
  "contains_interpretive_annotations": true
}
```

## Neutral and interpretive outputs

Where a visualization includes argumentative annotations, preserve:

- the extracted data;
- a neutral chart;
- the annotated chart.

This prevents visual rhetoric from becoming indistinguishable from measurement.

---

# 10. Stewardship Record Standard

## 10.1 Name the evidentiary level

- **Private reflection:** self-authored, mutable, no verification.
- **Timestamped record:** creation time retained.
- **Tamper-evident record:** chained hashes expose later modification.
- **Corroborated record:** references an external artifact or witness.

Do not call all four “proof.”

## 10.2 Privacy-preserving public index

A public or committed index may contain only:

```yaml
receipt_id: ZP-STW-0001
month: 2026-09
category: boundary
verification: private_artifact_retained
status: completed
```

The behavior, person, and evidence can remain private.

## 10.3 Required escape categories

A stewardship system should permit:

- custom behavior outside existing crosswalks;
- false positive;
- no action required;
- interpretation revised;
- protocol retired;
- sought external judgment.

Without these, the system can confirm its own taxonomy but cannot disconfirm it.

---

# 11. Privacy and Retention

## 11.1 Retention questions

For every sensitive artifact:

- Why is it retained?
- Where is it stored?
- Who can access it?
- Which external systems received it?
- When should it be reviewed or deleted?
- Can deletion actually remove all copies?
- Does it contain third-party information?

## 11.2 Repository rule

Restricted information should not be committed merely because the repository is private. Git history, clones, exports, provider uploads, and backups can preserve it beyond later deletion.

## 11.3 External-resource rule

A page described as offline or self-contained should not import remote fonts, scripts, analytics, images, or styles. If it does, state that explicitly.

---

# 12. Correction and Expiration

## Correction template

```yaml
correction_id: ZP-COR-0001
claim_id: ZP-CLM-0001
previous_status: active
new_status: superseded
reason: "The denominator mixed recordings and release appearances."
corrected_at: 2026-09-23
replacement_claim: ZP-CLM-0011
preserve_original: true
```

## Suggested review intervals

| Material | Review interval |
|---|---|
| Discography metadata | After each release and annually |
| Public-web census | Every 6–12 months |
| Security assumptions | After any access/provider change |
| Psychological interpretation | Six months maximum without new evidence |
| Self-reported preference | Review when behavior consistently differs |
| Software guarantee | Every code change |
| AI model statement | Treat as session-specific unless verified |

---

# 13. Publication Checklist

Before adding a new major document:

- [ ] Genre is labeled.
- [ ] Human/AI authorship is labeled.
- [ ] Source commit or source hashes are recorded.
- [ ] Observations are separated from interpretations.
- [ ] Self-report is not labeled independent observation.
- [ ] Repeated claims are traced to their earliest located source.
- [ ] Alternatives are stated.
- [ ] A falsifier or limitation is present.
- [ ] Third-party privacy has been reviewed.
- [ ] Sensitive data classification is assigned.
- [ ] Quantitative denominators are defined.
- [ ] Generated outputs have reproducible inputs.
- [ ] Correction and expiration states are present.
- [ ] The document adds evidence, not merely vocabulary.

---

# 14. Governance Roles

One person may hold several roles, but the roles should remain conceptually distinct.

| Role | Authority |
|---|---|
| Keeper | Maintains files and access |
| Source steward | Verifies provenance and hashes |
| Data steward | Defines entities and validation rules |
| Analyst | Produces interpretations |
| Adversarial reviewer | Tests alternatives and falsifiers |
| Privacy reviewer | Classifies sensitivity and third-party risk |
| Corrector | Marks claims disputed, superseded, or retracted |
| Subject | May refuse, correct, contextualize, or restrict self-report |

An analyst should not silently perform all roles at once.

---

# 15. Minimal Adoption Path

If full governance feels excessive, begin with four rules:

1. Give every major claim an ID.
2. Record the exact source hash and source type.
3. Mark whether support is independent or derived.
4. Preserve corrections instead of silently replacing conclusions.

Those four changes would address the archive’s largest evidentiary gap.

---

*Good governance does not make interpretation less imaginative. It prevents imagination from quietly inheriting the privileges of fact.*
