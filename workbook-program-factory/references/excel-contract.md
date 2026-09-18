# Excel contract — curriculum workbook

## Primary sheet

The canonical pedagogical table occupies columns A:Q.

```text
A Module
B Durée (en jours)
C Objectifs
D Compétences acquises
E Phase / LearningUnit
F Lien
G Durée (heures)
H Type de contenu
I Intention
J Ressources
K Modifications suggérées
L Exercices
M Quiz
N Évaluation professeur
O Outils
P Prérequis
Q Mode d'évaluation
```

Module/Objectives/Competencies may appear only on the first row of a module and are inherited by following phase rows until the next module begins.

The workbook footer exposes the duration-control interface:
- `HEURE TOTAL`
- `HEURE VOULUE`
- `HEURE MANQUANTE`

For the reference workbook, `HEURE VOULUE = 140`.

## Sheet roles

| Sheet | Role |
|---|---|
| Scenario Dev Blockchain Full St | canonical phase-level curriculum surface |
| Presentation Module | module summary/projection |
| Copies Links | source/provenance/access mapping |
| Ressources | resource inventory |
| Exercices | exercise projection |
| Liste | derived index |
| Projet à proposer | capstone candidates |

Other copy/scratch sheets must not override canonical facts without an explicit migration.

## Formula rules

The final workbook should compute:
- populated hours from phase durations;
- target hours from a single controlled target cell;
- missing hours = target - populated.

No generated process may claim completeness unless missing hours = 0 and curriculum graph gates pass.
