# XLSX curriculum contract

## Canonical phase table

The reference curriculum sheet is Scenario Dev Blockchain Full St. Its learner-facing table occupies A:Q:

| Column | Field |
|---|---|
| A | Module |
| B | Durée (en jours) |
| C | Objectifs |
| D | Compétences acquises |
| E | Phase / learning-unit title |
| F | Lien |
| G | Durée (heures) entered in the source |
| H | Type de contenu |
| I | Intention |
| J | Ressources |
| K | Modifications suggérées |
| L | Exercices |
| M | Quiz |
| N | Évaluation professeur |
| O | Outils |
| P | Prérequis |
| Q | Mode d'évaluation |

The two header rows may split labels across rows 5 and 6. Find the header by semantics, not by a fixed row number.

## Row interpretation

- A non-empty A with numeric B starts a module.
- A:D values from the module-opening row are inherited by following phase rows until the next module starts.
- A row with a non-empty E after the header is a learning-unit candidate.
- A blank E with a source pointer in F and a numeric G is a resource-only continuation candidate. Give it a stable supplementary title rather than dropping it.
- A blank E with no source pointer and no duration is not a unit.
- Rows containing HEURE TOTAL, HEURE VOULUE, or HEURE MANQUANTE are duration controls.
- Keep the source row number, sheet name, link, and raw source duration on every normalized unit.

## Supporting sheets

Preserve all source sheets. In the reference workbook the supporting set includes Presentation Module, Copy of Presentation Module, Sheet4, Ressources, Feuil4, Exercices, Sheet3, Copies Links, Sheet2, Liste, and Projet à proposer. Their roles may be projected into metadata, but they do not override canonical A:Q facts without an explicit migration.

## Duration semantics

The source workbook currently contains 6.12 entered hours, including two duration-bearing resource-only rows, and has a 140-hour design target. Store both values. The target is not evidence that the source already contains 140 hours. Planned hours may be allocated from module days using a 0.5-hour quantum and largest-remainder correction, but each planned value must carry a duration_basis.
