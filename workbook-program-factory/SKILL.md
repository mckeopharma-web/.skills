---
name: workbook-program-factory
description: Produce complete curriculum workbooks from the Mickael UMT multi-sheet Excel curriculum contract, manage an exact 140-hour learning budget, project pedagogy into a Neo4j-compatible graph, and materialize validated workbook programs in WBNK.
---

# Workbook Program Factory

Use this skill for the specific exercise of creating and completing pedagogical workbooks whose source format follows the multi-sheet curriculum workbook pattern exemplified by `Decentralized Science Curriculum CLASSEUR_CURRICULUM_.xlsx`.

This is not a generic course-writing skill. The workbook is the product model.

## Primary contract

The source workbook contains a primary curriculum sheet plus supporting projections. The primary sheet uses columns A:Q:

| Col | Semantic field |
|---|---|
| A | Module |
| B | Module duration in days |
| C | Objectives |
| D | Competencies acquired |
| E | Phase / lesson title |
| F | Link / source pointer |
| G | Duration in hours |
| H | Content type |
| I | Intention |
| J | Resources |
| K | Suggested changes |
| L | Exercises |
| M | Quiz |
| N | Professor evaluation |
| O | Tools |
| P | Prerequisites |
| Q | Evaluation mode |

A non-empty Module cell opens a module. Blank Module cells inherit the current module.

Reference workbook facts:
- 5 source modules.
- Declared module-day pattern: 3, 4, 5, 4, 5 days.
- Current populated duration: 6.12 h.
- Target duration: 140 h.
- Missing duration is therefore 133.88 h until additional units are designed.
- Supporting sheets include Presentation Module, Ressources, Exercices, Copies Links, Liste, and Projet à proposer.

Never confuse the current 6.12 h of entered phase durations with the target 140 h program.

## Workbook-first domain model

Normalize rows into:

```text
Program
 ├─ Module
 │   ├─ LearningUnit
 │   │   ├─ Objective
 │   │   ├─ Competency
 │   │   ├─ Activity
 │   │   ├─ Assessment
 │   │   ├─ Resource
 │   │   ├─ Tool
 │   │   └─ Deliverable
 │   └─ ModuleEvaluation
 └─ Capstone
```

The workbook remains the editable pedagogical surface. The graph is a validation and dependency model, not a replacement UI.

## 140-hour budget

The total program duration is a hard invariant.

```text
sum(LearningUnit.duration_hours) == Program.target_hours
Program.target_hours == 140.0
```

If only module days are available, allocate the 140 h planning envelope proportionally using a 0.5 h quantum and largest-remainder correction.

For the 3/4/5/4/5-day baseline:

| Module days | Planning allocation |
|---:|---:|
| 3 | 20.0 h |
| 4 | 26.5 h |
| 5 | 33.5 h |
| 4 | 26.5 h |
| 5 | 33.5 h |
| **Total** | **140.0 h** |

This is a design budget. It does not claim the source workbook already contains this quantity.

## Supporting-sheet semantics

Treat:
- `Presentation Module` as module-level summary/projection.
- `Copies Links` as provenance, alternate-copy, access and download status.
- `Ressources` as the resource inventory/taxonomy.
- `Exercices` as the exercise projection.
- `Liste` as a derived lookup/index.
- `Projet à proposer` as capstone/project candidates.

Derived sheets are read models. Prefer the primary curriculum sheet when facts conflict.

## Production algorithm

For each module:

1. Preserve the source module title, objectives, competencies, tools, prerequisites and evaluation mode.
2. Convert every existing Phase row into a stable LearningUnit candidate.
3. Split compound phases when a row contains multiple independently teachable outcomes.
4. Determine the module planning-hour budget.
5. Expand the module until its unit durations exactly consume that budget.
6. For every unit define:
   - one primary objective;
   - one or more competencies;
   - explanatory content;
   - guided practice;
   - independent practice when appropriate;
   - one assessment or explicit assessment exemption;
   - resources and provenance;
   - tools/prerequisites;
   - a learner output/deliverable where appropriate.
7. Populate or project exercises, quizzes and professor evaluation fields.
8. Link prerequisite units through a DAG.
9. Create or reuse graph entities for shared resources and competencies.
10. Run all gates before publication.

## Quality gates

A unit fails closed if any required field is missing without an explicit `not_applicable_reason`:
- stable id;
- title;
- duration_hours > 0;
- module;
- objective;
- competency;
- content type;
- activity;
- assessment;
- provenance status;
- prerequisite status;
- resource status;
- deliverable status.

A module fails if:
- allocated hours are not fully distributed;
- any source objective is uncovered;
- any source competency is uncovered;
- any competency lacks an assessment path;
- prerequisites contain a cycle;
- any unit is orphaned.

A program fails if:
- total duration is not exactly 140 h;
- graph ids are duplicated;
- graph has orphan modules/units;
- critical provenance gaps remain;
- workbook projections disagree with the canonical normalized manifest.

## Neo4j contract

When Neo4j/@neofort is available, inspect its schema before writes.

Stable node labels:
- Program
- Module
- LearningUnit
- Objective
- Competency
- Activity
- Assessment
- Resource
- Evidence
- Tool
- Deliverable
- Capstone

Stable relationships:
- HAS_MODULE
- HAS_UNIT
- ADDRESSES_OBJECTIVE
- BUILDS_COMPETENCY
- REQUIRES
- PRECEDES
- USES_RESOURCE
- SUPPORTED_BY
- USES_TOOL
- ASSESSED_BY
- PRODUCES
- DERIVES_FROM

Identity is always `id`, never title.

Use parameterized `MERGE` operations. Never delete unrelated graph content. Before inserting a Resource, Competency, Tool, Objective, or Evidence node, try to match an existing canonical entity.

Required graph validation queries must prove:
- duplicate ids = 0;
- orphan modules = 0;
- orphan learning units = 0;
- uncovered objectives = 0;
- unassessed competencies = 0;
- prerequisite cycles = 0;
- program duration mismatch = 0.

If Neo4j is unavailable, write deterministic Cypher migration files and a synchronization manifest. Mark `neo4j_sync_status: pending`. Do not pretend a live write happened.

## WBNK bounded context

Use a separate `curriculum-workbook` bounded context. Do not overload the existing `product-knowledge` catalog.

Canonical structure:

```text
curricula/
  <program-slug>/
    source/
      curriculum.xlsx
    workbook/
      curriculum-working.xlsx
    metadata/
      program.json
      modules.json
      units.json
      coverage.json
      provenance.json
    research/
      ...
    evidence/
      ...
    graph/
      curriculum.cypher
      curriculum.mmd
      curriculum.jsonld
      neo4j-sync.json
    assessments/
      ...
    exercises/
      ...
    exports/
      ...
```

Canonical write models live in `metadata/`. Graph artifacts and workbook summary sheets are projections.

## Excel mutation rules

When actually creating or editing the workbook:
- use the spreadsheet artifact skill/tooling;
- preserve the existing sheet topology and formulas unless migration explicitly requires a new version;
- never hardcode derived total/missing-hour values when a formula can express them;
- keep `HEURE TOTAL`, `HEURE VOULUE`, `HEURE MANQUANTE` formula-driven;
- preserve A:Q semantics on the main curriculum sheet;
- generate stable IDs in metadata/hidden technical columns or external manifests, not by corrupting learner-facing titles;
- create validation dropdowns for controlled fields such as content type, provenance status and evaluation mode where appropriate;
- verify formulas and render key sheets before export.

## Generation sequence

```text
Excel source
  -> workbook contract extraction
  -> normalized manifest
  -> 140 h allocation
  -> graph identity + prerequisite DAG
  -> evidence/resource completion
  -> learning-unit expansion
  -> exercises + assessments
  -> workbook projections
  -> Neo4j/RDF/Cypher projections
  -> fail-closed gates
  -> exports
```

## Originality and provenance

Reference courses and existing slides may inform structure and pedagogy, but the produced workbook must be original. Preserve URLs and source provenance. Do not copy substantial copyrighted course material into the generated program.

## Completion report

Every run must state:
- target hours;
- populated hours;
- missing hours;
- modules complete / total;
- units complete / total;
- uncovered objectives;
- unassessed competencies;
- unresolved resource/provenance gaps;
- Neo4j synchronization status;
- gate status.
