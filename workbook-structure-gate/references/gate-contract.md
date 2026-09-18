# Workbook structure gate contract

## Required manifest fields

The normalized program must include:

~~~text
schema_version
bounded_context = curriculum-workbook
id
title
target_hours
source_populated_hours
missing_hours_at_ingestion
canonical_sheet
primary_range = A:Q
workbook_contract.column_map
workbook_contract.derived_tabs
modules[]
neo4j_sync_status
~~~

Each module must include an id, order, title, allocated hours, objectives, competencies, and units. Each unit must include an id, title, duration_hours, objective_ids, competency_ids, assessment_status, provenance_status, prerequisite_unit_ids, and its source row or explicit research-gap reason.

## Required invariants

| Invariant | Pass condition |
|---|---|
| Identity | no duplicate IDs across the manifest |
| Module allocation | unit sum equals each module allocation within 0.01 h |
| Program allocation | all module allocations equal target hours within 0.01 h |
| Coverage | each module objective and competency appears in at least one unit |
| Assessment | each unit is defined or exempt with a reason |
| Provenance | each unit is verified, source-linked, or research-gap |
| Prerequisites | all references resolve and the graph has no cycle |
| Source/design separation | source-entered and planned hours are distinct |
| NeoFort status | unavailable connector is recorded as pending with a reason |

## Workbook checks

Derived tabs may be checked with Artifact Tool after recalculation. Existing source-tab #REF! values are preserved evidence; a new error on a derived tab is a gate failure.
