---
name: framework-curriculum-factory
description: Convert every WBNK framework product into a complete 140-hour curriculum bounded context, using curricula/desci-140h as the reference architecture while preserving the framework product aggregate and its product-knowledge routing contract.
---

# Framework Curriculum Factory

Use this skill when a resource under `frameworks/<slug>/` must become a complete teachable curriculum rather than a placeholder workbook.

The DeSci curriculum is the architectural reference, not a content template. Reuse its invariants, directory semantics, graph identity, assessment model and 140-hour reconciliation. Do not clone its subject matter.

## Canonical materialization

Each framework remains a product aggregate and receives a nested curriculum bounded context:

```text
frameworks/<slug>/
  source/
  research/
  workbook/
  curriculum/
    source/
      source-profile.json
    metadata/
      program.json
      modules.json
      units.json
      coverage.json
      provenance.json
    workbook/
      program-summary.csv
      modules.csv
      learning-units.csv
      assessment-matrix.csv
      coverage-gaps.csv
    assessments/
      index.json
    exercises/
      index.json
    evidence/
      index.json
    graph/
      curriculum.mmd
      curriculum.cypher
      neo4j-sync.json
    research/
      README.md
    exports/
      README.md
```

The outer `frameworks/<slug>` remains governed by product-knowledge. The nested `curriculum/` is governed by curriculum-workbook semantics.

## 140-hour invariant

Every framework curriculum MUST satisfy:

```text
target_hours = 140.0
sum(module.allocated_hours) = 140.0
sum(unit.duration_hours) = 140.0
sum(unit.duration_hours within module) = module.allocated_hours
```

Default factory topology when the framework has no source duration model:

- 5 modules.
- 28 hours per module.
- 4 learning units per module.
- 7 hours per unit.
- 20 learning units total.
- source_populated_hours = 0 unless an authoritative source contains explicit hours.
- missing_hours_at_ingestion = 140 when no source hours exist.

This is a planning design. Never claim that a quick-reference framework originally contained 140 hours.

## Content generation

Use, in order:

1. catalog/resources.json declaration;
2. the framework's research/course-alignment/course-map.json;
3. existing framework source/research/evidence artifacts;
4. verified external sources only when a gap remains.

For each framework derive a curriculum focus from its exact product name, description and family_id. Courses in course-map.json may inform structure and concepts but must not be copied. Produce original learning material.

Every unit must contain:
- stable id;
- title;
- 7 h planned duration unless a controlled allocation says otherwise;
- one objective id;
- one competency id;
- explanatory content;
- guided practice;
- independent practice;
- an activity;
- assessment method;
- assessment rubric;
- learner evidence/output;
- prerequisite unit ids or explicit empty list;
- provenance_status;
- resource status;
- deliverable status.

## Family specialization

The seven current WBNK curriculum families are:
- agentic-production;
- ai-security-release;
- traceability-verifiability;
- gxp-regulated-evidence;
- clinical-pv;
- workforce-adoption;
- marketing-commercial.

Use family-specific module archetypes, then specialize them to the exact framework. A Diagnostic Framework and a Production Promotion Gate may share a family but MUST NOT have identical module titles or capstones.

## Assessment rule

Every unit has assessment_status=defined unless a documented exemption exists. Prefer authentic artifacts: architecture decision records, gate packs, trace matrices, validation plans, signal dossiers, workflow maps, offer systems, evaluation datasets, incident drills and capstone reviews.

## Provenance rule

If a unit is synthesized from the declared framework plus its local course-map, set provenance_status=source-linked and record those local paths. If a required concept lacks local provenance, keep research-gap until a verified source is attached. Do not relabel a research gap as verified merely because the content sounds plausible.

## Graph rule

Stable graph labels:
Program, Module, LearningUnit, Objective, Competency, Activity, Assessment, Resource, Evidence, Tool, Deliverable, Capstone.

Stable relations:
HAS_MODULE, HAS_UNIT, ADDRESSES_OBJECTIVE, BUILDS_COMPETENCY, REQUIRES, PRECEDES, USES_RESOURCE, SUPPORTED_BY, USES_TOOL, ASSESSED_BY, PRODUCES.

Neo4j live synchronization is optional. If unavailable, generate deterministic Cypher and set neo4j_sync_status=pending with the exact reason.

## Gates

Fail closed when:
- target is not exactly 140 h;
- module/unit allocation does not reconcile;
- duplicate IDs exist;
- an objective or competency is uncovered;
- a prerequisite is unresolved or cyclic;
- an assessment is missing;
- a unit lacks pedagogy/evidence/deliverable fields;
- the nested curriculum files are not routed through the curriculum RDF role;
- CI does not validate framework curriculum manifests.

## Agent behavior

For a request such as "fill frameworks as curricula":
1. enumerate all declared framework aggregates;
2. load their course maps;
3. generate or update all framework curricula;
4. update curriculum CI discovery;
5. update RDF routing if needed;
6. run deterministic preflight;
7. inspect GitHub Actions;
8. report complete/total, 140-hour invariants, provenance gaps and CI status.

Do not stop after creating folders. A framework is considered materialized only when program.json, units, assessments, exercises, workbook read models and graph projections exist.
