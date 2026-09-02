# Zaziopath — diagrams & charts

Rendered charts for the vault, committed as PNG so they display anywhere
(GitHub, local editors, offline). Every number is drawn from the README and
the files actually committed at the repo root.

| File | What it shows |
|---|---|
| [`vault-map.png`](vault-map.png) | Everything committed at the root, grouped by category — 10 PDFs, 336 pages, plus the spreadsheet, memory export, templates, and profile layer. |
| [`archetype-cosmology.png`](archetype-cosmology.png) | The ≈250 named archetypes / personas, broken out by compendium chapter. |
| [`subject-typology.png`](subject-typology.png) | Big Five radar + the load-bearing shadow-profile traits. |
| [`case-study-floor.png`](case-study-floor.png) | The evidence floor: 82.5% ISRC coverage, media-master priority tiers, Instagram-audit coverage. |
| [`shadow-light-crosswalk.png`](shadow-light-crosswalk.png) | The ch. 22 crosswalk — nine shadow archetypes beside their light counterparts. |
| [`pattern-register.png`](pattern-register.png) | The fourteen recurring patterns (§07) arranged around the unifying inference. |

## Regenerate

```bash
python3 diagrams/generate_diagrams.py   # requires: pip install matplotlib
```

The counts are extracted from the files at the repo root — re-run the script
after the vault changes so the charts and the README stay in step.
