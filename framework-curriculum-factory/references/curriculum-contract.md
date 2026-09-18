# Framework curriculum contract

Reference architecture: `curricula/desci-140h`.

A framework curriculum is a nested curriculum-workbook bounded context under a product aggregate. Its source is not necessarily an XLSX.

Minimum program fields:
- schema_version
- bounded_context = curriculum-workbook
- id
- slug
- title
- target_hours = 140
- source_populated_hours
- missing_hours_at_ingestion
- source_type
- source_references
- modules[]
- neo4j_sync_status

Default topology:
`5 modules × 4 units × 7 h = 140 h`.

Every module declares objective and competency ids that are covered by its units. Every unit declares assessment_status, provenance_status, prerequisite_unit_ids, activity, evidence_to_capture and deliverable.

The framework's existing `research/course-alignment/course-map.json` is a local provenance input, not permission to copy course content.
