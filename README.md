# mckeopharma-web/.skills

Reusable production skills for curriculum workbooks and WBNK materialization.

## Skills

- workbook-program-factory/ — orchestrates complete curriculum programs, exact-hour allocation, graph projections, assessments, and WBNK package layout.
- xlsx-to-workbook-structure/ — extracts a curriculum XLSX into stable modules, learning units, provenance, derived workbook tabs, and graph-ready metadata while preserving the source Excel topology.
- workbook-structure-gate/ — fail-closed validation for A:Q structure, source/design duration separation, coverage, assessments, prerequisites, and NeoFort sync status.

## Execution order

1. Run xlsx-to-workbook-structure against the source XLSX.
2. Materialize the source copy under source/ and the edited projection under workbook/.
3. Run workbook-structure-gate against the normalized manifest and working workbook.
4. Run the graph projection only after NeoFort schema inspection. Keep synchronization pending with a reason when the connector is unavailable.
