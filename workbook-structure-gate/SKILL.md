---
name: workbook-structure-gate
description: Validate curriculum workbook manifests and projections for Excel topology, exact duration reconciliation, unit coverage, provenance, assessments, prerequisites, and graph-readiness before GitHub publication.
---

# Workbook Structure Gate

Use this skill after an XLSX has been profiled and normalized, and before a working workbook or workbook directory is published. The gate is fail-closed: a clean-looking spreadsheet is not complete if its manifest, source mapping, duration model, or dependency graph is incomplete.

## Inputs

Accept:

- the normalized metadata/program.json;
- the XLSX profile produced by xlsx-to-workbook-structure;
- the working workbook when formula or projection checks are required.

Run scripts/check_curriculum_manifest.py for deterministic JSON checks. Use the spreadsheet skill to inspect the working workbook's derived tabs and scan new tabs for formula errors. Existing source-tab errors must be recorded as pre-existing, not silently repaired.

## Structural gates

The gate must fail if any of these are false:

- the bounded context is curriculum-workbook;
- the canonical sheet is identified and its A:Q map is intact;
- source tabs are preserved and derived tabs are explicitly listed;
- module and unit IDs are stable and unique;
- each unit belongs to one module and has a positive planned duration;
- each module's unit hours equal its allocated hours;
- total planned hours equal the program target within 0.01 hours;
- every module objective and competency is covered by at least one unit;
- every unit has an assessment status, provenance status, and prerequisite list or explicit exemption;
- every prerequisite points to an existing unit and the prerequisite graph is acyclic;
- source-entered duration and planned duration remain separate;
- if NeoFort is unavailable, the sync manifest says pending and includes the actual failure reason.

The reference DeSci curriculum must close to exactly 140 planned hours. Do not make a source workbook appear complete by replacing its 6.12 entered hours with 140. The source/design distinction belongs in the summary and metadata.

## Workbook projection gates

When a working XLSX is supplied, verify that:

1. the canonical sheet remains Scenario Dev Blockchain Full St or another sheet explicitly identified by the profile;
2. its A:Q phase-level table is unchanged except for requested, traceable edits;
3. Program Summary, Modules, Learning Units, Assessment Matrix, and Coverage & Gaps are present when requested;
4. derived rows carry stable IDs and source-row provenance;
5. formula-driven duration controls are not replaced by hardcoded totals;
6. newly generated tabs have no formula errors such as #REF!, #DIV/0!, #VALUE!, #NAME?, #N/A, #NUM!, #NULL!, #SPILL!, or #CALC!.

## NeoFort gate

Inspect the NeoFort schema before writing. If the connector returns 403 Forbidden, stop graph writes, keep deterministic Cypher as an artifact, and mark the synchronization pending. Never convert a failed connector call into a false synced status.

## Output

Return a compact JSON report containing status, errors, warnings, target_hours, planned_hours, source_populated_hours, module_count, unit_count, research_gap_unit_count, and neo4j_sync_status. A non-empty error list must result in a non-zero process exit code.

See references/gate-contract.md and scripts/check_curriculum_manifest.py.
