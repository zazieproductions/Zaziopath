# Zaziopath Claim Provenance Ledger

**Status:** Pilot ledger  
**Date:** 2026-09-23  
**Purpose:** Demonstrate claim-level provenance using ten central repository propositions. This is a human-readable pilot, not yet a complete machine-readable registry.

## Source Fingerprints

| Source | Git blob | SHA-256 |
|---|---|---|
| `README.md` | `0600a24d851404901ede3fcc8f2eedcbdee5d113` | `f09a1f5f4375ecb1e7592460348e3e0b43dfd76af12c2737f5cf507070d198d1` |
| `meta-experiment` | `d5901dd32d1d51a061add2a639e5baee3d9b7231` | `79608f5d34f5a941d3914634271b5403ccedba518e107a7b6446b7b1c418a537` |
| `Zazie_Productions_Discography.csv` | `182772f6887c859173f95d50b1b41ce9653d100d` | `268e396a10a59ab43ebd0289140a329286cd9cfb8b0baacf6025b7db186c1cab` |
| `stewardship_receipt.html` | `43b1a33e112abc68ccf6855caaa18da02499bdc6` | `405ac87e98739af74d42aa3be26033c364e4b8b8915f8d2e5daabc00c7ada9a2` |
| `JSON file re-export ChatGPT Memory .md` | `000f6759d1aa1b2f455e9f8a5438537994ded375` | `da4c9be9cdbeda3a97461685d7bd36dff394ac3132241dc6d39e22713eaf42f7` |
| `🔍 CASE FILE — Pattern Forensics.md` | `46106c85b0a4b7496380d27a23412e62eca5a7b6` | `5356bacadf443bb4683a22a2b3c556a506c4ae290b56412b6972631e556820f0` |
| Mega Compendium PDF | `f48cb7e71a7c261a8af55fdea6383cf1fd896462` | `8e7ed27e4aa83952342a99e1d1ae95ee054614a3ab2faba14e2c6a333caaed49` |

Hashes identify the audited versions. They do not certify factual truth.

---

## ZP-CLM-0001 — The repository is explicitly organized as an instrument for self-analysis

**Statement:** The current README presents Zaziopath as a working instrument for self-analysis rather than merely a diary or portfolio.

- **Claim level:** Observation
- **Source type:** Self-description / repository governance
- **Primary source:** `README.md`, lines 138–166
- **Independence:** Primary for intended purpose
- **Verification:** Reproduced by direct reading
- **Confidence:** Strong
- **Limits:** Establishes declared function, not actual effect
- **Alternative:** The declaration may also operate as artistic framing
- **Falsifier:** A governing document explicitly superseding this purpose
- **Status:** Active

---

## ZP-CLM-0002 — The declared method terminates in behavior

**Statement:** The README defines Stewardship as a behavioral endpoint and explicitly warns that shadow reading without stewardship is another way of being stuck.

- **Claim level:** Observation
- **Source type:** Repository governance
- **Primary source:** `README.md`, lines 171–182 and 368
- **Independence:** Primary for declared method
- **Verification:** Reproduced
- **Confidence:** Strong
- **Limits:** Does not establish that behavior occurred
- **Falsifier:** Revision of the method so that interpretation itself is the endpoint
- **Status:** Active

---

## ZP-CLM-0003 — Recursive reflection can lose contact with its initiating experience

**Statement:** `meta-experiment` argues that each added reflective layer may contain less direct contact with the initiating event and more commentary on previous commentary.

- **Claim level:** Summary of argument
- **Source type:** Generated or mixed philosophical interpretation; exact authorship unknown
- **Primary source:** `meta-experiment`, section 1
- **Independence:** Primary for the text’s argument; not independent evidence about the repository author
- **Verification:** Text reproduced; broader psychological proposition not experimentally tested here
- **Confidence:** Strong as textual summary, tentative as universal psychological claim
- **Limits:** Meta-reflection can also create useful distance and new options
- **Falsifier:** For a specific instance, an added layer that produces a materially new perception or action
- **Status:** Active

---

## ZP-CLM-0004 — The CSV contains 182 release-appearance rows

**Statement:** The current discography CSV contains 182 data rows under one header.

- **Claim level:** Observation
- **Source type:** Structured catalog
- **Primary source:** `Zazie_Productions_Discography.csv`
- **Independence:** Primary
- **Verification:** Reproduced with Python CSV parsing
- **Confidence:** Strong
- **Limits:** A row is not necessarily a unique recording
- **Falsifier:** Parsing under the documented CSV dialect yields a different row count
- **Status:** Active

---

## ZP-CLM-0005 — The workbook and CSV use different apparent catalog scopes

**Statement:** The README describes the six-sheet workbook as covering 200 tracks, while the CSV and figure descriptions cover 182 catalogued rows; workbook sheet names make scope differences involving features, collaborations, or compilations plausible.

- **Claim level:** Observation plus bounded interpretation
- **Source type:** Repository summary and structured files
- **Primary sources:** `README.md`, lines 250, 555, 567, 587; XLSX workbook structure; CSV
- **Independence:** Partly independent
- **Verification:** Counts and labels reproduced; complete workbook semantics not yet normalized
- **Confidence:** Strong that scopes differ; tentative about exact reason
- **Alternatives:** Stale documentation, export omission, or distinct entity definitions
- **Falsifier:** A published reconciliation showing identical scope and explaining the numerical difference another way
- **Status:** Active, unresolved

---

## ZP-CLM-0006 — The CSV is not a unique-recording table

**Statement:** The current CSV includes repeated valid ISRCs for recordings appearing on later releases, so each row represents a release appearance more closely than a unique recording.

- **Claim level:** Structural interpretation grounded in data
- **Source type:** Structured catalog
- **Primary source:** CSV rows containing repeated ISRCs across original and deluxe releases
- **Independence:** Primary
- **Verification:** Reproduced by duplicate grouping
- **Confidence:** Strong
- **Limits:** Some appearances could be materially different versions and require manual review
- **Falsifier:** Documentation establishing that every repeated ISRC row represents a distinct recording despite code reuse
- **Status:** Active

---

## ZP-CLM-0007 — The receipt console stores mutable self-reports locally

**Statement:** The current stewardship console stores user-authored receipt objects in browser `localStorage`, displays them, permits deletion, and exports editable Markdown.

- **Claim level:** Observation
- **Source type:** Software behavior inferred from source code
- **Primary source:** `stewardship_receipt.html`, inline script
- **Independence:** Primary
- **Verification:** Static source inspection; syntax smoke test passes
- **Confidence:** Strong
- **Limits:** Full browser behavior was not exercised in an automated browser during this audit
- **Falsifier:** Code change replacing localStorage and deletion with another mechanism
- **Status:** Active

---

## ZP-CLM-0008 — “Nothing transmitted” does not mean zero external requests

**Statement:** The receipt application does not intentionally transmit receipt content through `fetch` or XHR, but its stylesheet imports Google Fonts and may therefore create external network requests when opened online.

- **Claim level:** Software/security interpretation
- **Source type:** Source-code behavior
- **Primary source:** `stewardship_receipt.html`, CSS `@import`; smoke-test assertions
- **Independence:** Primary
- **Verification:** Static inspection; network request not dynamically captured here
- **Confidence:** Strong about request capability, not about any specific historical request
- **Limits:** Browser caching, offline mode, CSP, or blocking may prevent the request
- **Falsifier:** Removal or local vendoring of all external resources
- **Status:** Active

---

## ZP-CLM-0009 — The assistant memory export is not an independent behavioral record

**Statement:** The ChatGPT memory export is a record of assistant-stored summaries derived from prior interaction, not an independent observational record of behavior.

- **Claim level:** Source classification
- **Source type:** Model memory summary
- **Primary source:** `JSON file re-export ChatGPT Memory .md`
- **Independence:** Derived from user-model interaction
- **Verification:** Artifact type reproduced; underlying conversations are not available here for full reconstruction
- **Confidence:** Strong
- **Limits:** It may still reliably summarize recurring disclosures and preferences
- **Alternative:** Some entries may closely track repeated observed interaction patterns rather than explicit self-report
- **Falsifier:** Documentation showing the export was generated from independent external behavioral data
- **Status:** Active

---

## ZP-CLM-0010 — The six verdicts do not constitute six independent observers

**Statement:** The six verdict files form a sequential, mutually referential commission series and should not be counted as six independent confirmations of their shared psychological conclusions.

- **Claim level:** Process interpretation
- **Source type:** Generated interpretation sequence
- **Primary sources:** `verdict_from_A.i` through `verdict_from_A.i_6`
- **Independence:** Contaminated / sequential
- **Verification:** Reproduced from explicit cross-reference and Verdict 6’s reconstruction
- **Confidence:** Strong
- **Limits:** Later verdicts sometimes add new structural observations even though framing is inherited
- **Falsifier:** Provenance showing the documents were independently generated without access to prior verdicts, prompts, or summaries
- **Status:** Active

---

# Derived Claims Requiring Caution

The following statements should not enter the ledger as observations without narrower wording:

| Overstrong statement | Governed replacement |
|---|---|
| “No behavior changed.” | “No exported stewardship receipt was located in the tracked tree on 2026-09-23.” |
| “No other person lives here.” | “The archive contains little detailed, consented interpersonal primary evidence.” |
| “The subject wants to be caught.” | “The subject repeatedly commissioned penetrating interpretations; motive remains uncertain.” |
| “The dark material proves predator identification.” | “The archive repeatedly uses predator, manipulation, and control aesthetics.” |
| “The archive is a trauma response.” | “Some agents interpret the archive through trauma frameworks; the repository cannot verify that causal claim.” |
| “Six agents agree.” | “Six sequential documents repeat and elaborate related claims under inherited framing.” |
| “The receipt proves the change.” | “The receipt records a user’s statement that a change and evidence exist.” |
| “The catalog has 200 unique tracks.” | “The workbook reports 200 tracks under a scope not yet reconciled with the 182-row CSV.” |

---

# Contradiction Register

## C-01 — 200 versus 182

- **Apparent conflict:** 200 workbook tracks versus 182 CSV rows.
- **Leading explanation:** Different scope.
- **Status:** Unresolved, not yet a contradiction.
- **Required evidence:** Normalize workbook catalog, features, and compilation sheets against CSV recording and appearance IDs.

## C-02 — Local-only versus external resources

- **Apparent conflict:** “Nothing leaves this browser” / self-contained wording versus Google Fonts import.
- **Resolution:** Receipt content is not intentionally submitted, but zero-network privacy is not guaranteed.
- **Status:** Partly resolved through narrower wording.

## C-03 — Evidence-backed endpoint versus mutable receipt

- **Apparent conflict:** Receipt rhetoric implies proof, while implementation stores editable self-attestation.
- **Resolution:** Distinguish reflective receipt from tamper-evident or corroborated evidence.
- **Status:** Terminology and product-design issue.

## C-04 — Independent tribunal language versus sequential commissions

- **Apparent conflict:** Multiple verdicts create plural authority while later files document shared context and continuation.
- **Resolution:** Treat as one recursive analytic series with six stages.
- **Status:** Resolved for meta-analysis.

---

# Ledger Maintenance Rule

A claim must be reviewed when:

- its source file changes;
- a new independent source appears;
- a conflicting artifact is found;
- its scope or denominator changes;
- six months pass for a psychological interpretation;
- one year passes for catalog metadata;
- or the claim is reused in a public-facing document.

Repeated use is not a substitute for review.

---

*The ledger’s purpose is not to eliminate interpretation. It is to stop interpretation from forgetting its parents.*
