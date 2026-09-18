# Workbook and manifest layout

## GitHub materialization

Use a bounded context that keeps source, working workbook, metadata, assessments, exercises, and graph artifacts separate:

~~~text
curricula/<program-slug>/
  source/curriculum.xlsx
  workbook/curriculum-working.xlsx
  metadata/program.json
  metadata/modules.json
  metadata/units.json
  metadata/coverage.json
  metadata/provenance.json
  assessments/index.json
  exercises/index.json
  graph/curriculum.cypher
  graph/curriculum.jsonld
  graph/curriculum.mmd
  graph/neo4j-sync.json
~~~

The source file is immutable evidence. The working file is the editable projection. metadata/program.json is the canonical write model; derived workbook tabs and graph files must agree with it.

## Derived workbook tabs

Append, in order, without renaming or deleting source tabs:

| Tab | Required content |
|---|---|
| Program Summary | program id, target hours, source-entered hours, planned hours, missing hours at ingestion, counts, gate status, NeoFort status |
| Modules | module id, order, title, declared days, allocated hours, source row, objectives, competencies, coverage status |
| Learning Units | unit id, module id, order, title, source row, source duration, planned duration, A:Q fields, objectives, competencies, prerequisites, provenance |
| Assessment Matrix | unit id, assessment id, assessment status, exercise/quiz/professor evaluation, evidence path, deliverable |
| Coverage & Gaps | objective and competency coverage, source gaps, assessment gaps, provenance gaps, duration reconciliation |

## Graph projection

Use globally unique string IDs. Minimum labels are Program, Module, LearningUnit, Objective, Competency, Assessment, Resource, Tool, and Deliverable.

Minimum relationships:

~~~text
Program -HAS_MODULE-> Module
Module -HAS_UNIT-> LearningUnit
LearningUnit -ADDRESSES_OBJECTIVE-> Objective
LearningUnit -BUILDS_COMPETENCY-> Competency
LearningUnit -USES_RESOURCE-> Resource
LearningUnit -USES_TOOL-> Tool
LearningUnit -ASSESSED_BY-> Assessment
LearningUnit -PRODUCES-> Deliverable
LearningUnit -REQUIRES|PRECEDES-> LearningUnit
~~~

Use parameterized MERGE on id. When live NeoFort access is unavailable, ship the deterministic Cypher and set neo4j_sync_status to pending.
