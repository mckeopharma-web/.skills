---
name: xlsx-to-workbook-structure
description: Convert an existing curriculum XLSX into a stable workbook and program contract while preserving the Excel phase-level topology, source tabs, provenance, and hour semantics. Use when a workbook must be organized from an XLSX, especially a multi-sheet curriculum with a canonical A:Q sheet.
---

# XLSX to Workbook Structure

Use this skill when the workbook is the source of truth and the task is to turn its structure into reusable curriculum content, metadata, workbook views, and graph-ready records. It is designed for the DeSci curriculum pattern, but the extraction rules are reusable for any curriculum that has module headers, inherited cells, phase rows, and supporting resource or exercise sheets.

The workbook is the editable pedagogical surface. JSON metadata and graph files are projections. Do not replace the source workbook with a new generic table.

## Required workflow

1. Import the XLSX with the spreadsheet skill and inspect sheet names, used ranges, formulas, and a rendered view of the canonical sheet before changing it.
2. Run scripts/profile_curriculum_xlsx.mjs against the source file. Treat its profile as the extraction record, not as a replacement for the workbook.
3. Detect the canonical curriculum sheet by its A:Q headers. Prefer 'Scenario Dev Blockchain Full St' for the reference workbook, but do not select a sheet solely by position.
4. Normalize module and phase rows using the rules in references/xlsx-contract.md.
5. Allocate planned learning time separately from source-entered time. Preserve source duration values in source_duration_hours; never overwrite them to make the total look complete.
6. Generate stable IDs for the program, modules, units, objectives, competencies, resources, tools, assessments, and deliverables. IDs must not depend on display titles.
7. Create a working workbook by copying the source workbook, preserving every source sheet and its existing formulas or source errors. Append derived views rather than rewriting the canonical source surface.
8. Run the companion workbook-structure-gate skill before publication.
9. For a GitHub materialization, put the working workbook at curricula/<program-slug>/workbook/curriculum-working.xlsx and the unchanged input at curricula/<program-slug>/source/curriculum.xlsx. Keep JSON manifests under metadata/.

## Canonical Excel contract

The primary sheet is a phase-level table with columns A:Q:

| Column | Meaning |
|---|---|
| A | Module |
| B | Module duration in days |
| C | Objectives |
| D | Competencies acquired |
| E | Phase / learning-unit title |
| F | Link or source pointer |
| G | Source-entered duration in hours |
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

A non-empty A cell with a numeric B cell opens a module. Blank A:D cells on following phase rows inherit the current module context. A row is a learning-unit candidate when E is non-empty, or when E is blank but F contains a source pointer and G contains a numeric duration. The latter rows must become explicit supplementary/resource-only units so source totals remain auditable. Footer rows such as HEURE TOTAL, HEURE VOULUE, and HEURE MANQUANTE are duration controls, not learning units. Do not turn a header, subtotal, or footer into content.

The reference workbook has five modules, 58 titled phase rows plus two duration-bearing resource rows, 60 normalized learning units, module days 3/4/5/4/5, and 6.12 source-entered hours. Its design target is exactly 140 hours. The distinction is mandatory:

source-entered hours is evidence from the XLSX; planned hours is the design allocation.

## Workbook organization

Preserve all source tabs and append these derived tabs in this order when the workbook needs structured projections:

1. Program Summary — target, source-entered, planned, missing, counts, and sync status.
2. Modules — one row per module with source row, declared days, allocated hours, objective and competency coverage.
3. Learning Units — one row per stable unit with source row, source duration, planned duration, source fields, IDs, prerequisites, and provenance.
4. Assessment Matrix — unit-to-assessment mapping, quiz, professor evaluation, evidence path, deliverable, and assessment status.
5. Coverage & Gaps — uncovered objectives or competencies, research gaps, source-duration gap, and unresolved provenance or assessment work.

These are read models. The canonical A:Q sheet remains the learner-facing and editor-facing phase table. Do not move its columns, merge module rows, or delete supporting sheets to make the derived tabs easier to build.

## Duration and content rules

- Use the workbook target, or a single controlled target in metadata, as the only target-hours source.
- For the reference DeSci program, reconcile exactly 140 planned hours using the module-day envelope 20.0 / 26.5 / 33.5 / 26.5 / 33.5 and a 0.5-hour planning quantum.
- Keep source_duration_hours, planned_duration_hours, source_populated_hours, target_hours, and missing_hours_at_ingestion as separate fields.
- If the source does not provide enough duration or content, record a design gap. Do not fabricate a link, resource, assessment, or source duration.
- Every planned unit needs a title, positive planned duration, one or more objectives, one or more competencies, a content type, an assessment status or explicit exemption, provenance status, and prerequisite status.
- Preserve inherited blank module fields in the source workbook. Store normalized inherited values in metadata without backfilling the original source cells unless the user explicitly asks for a workbook edit.

## NeoFort and graph projection

Before any live graph write, call the NeoFort schema tool and use read-only Cypher to confirm labels, relationship types, and property keys. Use stable id values, parameterized MERGE, and the graph contract in references/workbook-layout.md.

If NeoFort returns an access error or is unavailable:

- do not claim that a live graph was synchronized;
- emit deterministic Cypher and a synchronization manifest;
- set neo4j_sync_status to pending with the observed reason;
- keep the workbook and JSON manifests usable without a graph connection.

The graph validates the workbook; it does not replace the workbook's Excel organization.

## Completion report

Report target hours, source-entered hours, planned hours, missing hours at ingestion, module and unit counts, uncovered objectives, unassessed competencies, provenance gaps, workbook path, gate status, and NeoFort synchronization status. A PASS requires exact planned-hour reconciliation and no unresolved structural gate errors.

See references/xlsx-contract.md, references/workbook-layout.md, and scripts/profile_curriculum_xlsx.mjs.
