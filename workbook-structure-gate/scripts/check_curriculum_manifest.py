#!/usr/bin/env python3
"""Fail-closed checks for a curriculum program manifest."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ALLOWED_ASSESSMENT = {"defined", "exempt"}
ALLOWED_PROVENANCE = {"verified", "source-linked", "research-gap"}
ALLOWED_SYNC = {"synced", "pending", "not-configured"}
REQUIRED_COLUMNS = set("ABCDEFGHIJKLMNOPQ")


def close(a: float, b: float, tolerance: float = 0.01) -> bool:
    return math.isclose(float(a), float(b), abs_tol=tolerance)


def as_number(value, label, errors):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label} must be numeric")
        return None
    if not math.isfinite(float(value)):
        errors.append(f"{label} must be finite")
        return None
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--expected-hours", type=float)
    args = parser.parse_args()

    try:
        program = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "errors": [f"cannot read manifest: {exc}"]}, indent=2))
        return 1

    errors = []
    warnings = []
    if not isinstance(program, dict):
        errors.append("manifest root must be an object")
        program = {}

    if program.get("bounded_context") != "curriculum-workbook":
        errors.append("bounded_context must be curriculum-workbook")
    for field in ("schema_version", "id", "title", "canonical_sheet", "primary_range"):
        if not program.get(field):
            errors.append(f"missing {field}")
    if program.get("primary_range") != "A:Q":
        errors.append("primary_range must be A:Q")

    target = as_number(program.get("target_hours"), "target_hours", errors)
    source = as_number(program.get("source_populated_hours"), "source_populated_hours", errors)
    missing = as_number(program.get("missing_hours_at_ingestion"), "missing_hours_at_ingestion", errors)
    if target is not None and target <= 0:
        errors.append("target_hours must be positive")
    if source is not None and target is not None and missing is not None:
        if not close(target - source, missing):
            errors.append("missing_hours_at_ingestion does not equal target_hours - source_populated_hours")
    if args.expected_hours is not None and target is not None and not close(target, args.expected_hours):
        errors.append(f"target_hours must equal {args.expected_hours:g}")

    contract = program.get("workbook_contract") or {}
    columns = contract.get("column_map") or {}
    if set(columns) != REQUIRED_COLUMNS:
        errors.append("workbook_contract.column_map must contain exactly A:Q")
    derived_tabs = contract.get("derived_tabs") or []
    required_tabs = {"Program Summary", "Modules", "Learning Units", "Assessment Matrix", "Coverage & Gaps"}
    missing_tabs = sorted(required_tabs - set(derived_tabs))
    if missing_tabs:
        errors.append("missing derived tabs: " + ", ".join(missing_tabs))
    if not isinstance(program.get("source_supporting_sheets"), list):
        errors.append("source_supporting_sheets must be a list")

    sync_status = program.get("neo4j_sync_status")
    if sync_status not in ALLOWED_SYNC:
        errors.append("neo4j_sync_status is invalid")
    if sync_status == "pending" and not str(program.get("neo4j_sync_reason") or "").strip():
        errors.append("pending NeoFort status requires neo4j_sync_reason")

    modules = program.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("modules must be a non-empty list")
        modules = []

    all_ids = {}
    unit_ids = set()
    unit_by_id = {}
    total_planned = 0.0
    research_gap_count = 0
    assessment_count = 0

    def register(identifier, kind, repeated_reference=False):
        if not identifier:
            errors.append(f"missing {kind} id")
            return
        if identifier in all_ids:
            if repeated_reference and all_ids[identifier] == kind:
                return
            errors.append(f"duplicate id {identifier} ({kind}; already {all_ids[identifier]})")
        else:
            all_ids[identifier] = kind

    for module in modules:
        if not isinstance(module, dict):
            errors.append("module entry must be an object")
            continue
        module_id = module.get("id")
        register(module_id, "module")
        if not module.get("title"):
            errors.append(f"{module_id} missing title")
        allocated = as_number(module.get("allocated_hours"), f"{module_id}.allocated_hours", errors)
        units = module.get("units")
        if not isinstance(units, list) or not units:
            errors.append(f"{module_id}.units must be a non-empty list")
            units = []
        module_planned = 0.0
        covered_objectives = set()
        covered_competencies = set()
        for unit in units:
            if not isinstance(unit, dict):
                errors.append(f"{module_id} contains a non-object unit")
                continue
            unit_id = unit.get("id")
            register(unit_id, "unit")
            if not unit.get("title"):
                errors.append(f"{unit_id} missing title")
            if unit_id:
                unit_ids.add(unit_id)
                unit_by_id[unit_id] = unit
            duration = as_number(unit.get("duration_hours"), f"{unit_id}.duration_hours", errors)
            if "source_duration_hours" not in unit:
                errors.append(f"{unit_id} must retain source_duration_hours separately")
            if not unit.get("duration_basis"):
                errors.append(f"{unit_id} missing duration_basis")
            if duration is not None:
                if duration <= 0:
                    errors.append(f"{unit_id} duration_hours must be positive")
                module_planned += duration
                total_planned += duration
            for field, target_set in (("objective_ids", covered_objectives), ("competency_ids", covered_competencies)):
                values = unit.get(field)
                if not isinstance(values, list) or not values:
                    errors.append(f"{unit_id}.{field} must be non-empty")
                else:
                    target_set.update(values)
                    for value in values:
                        register(value, field[:-4], repeated_reference=True)
            assessment_status = unit.get("assessment_status")
            if assessment_status not in ALLOWED_ASSESSMENT:
                errors.append(f"{unit_id}.assessment_status is invalid")
            else:
                if assessment_status == "exempt" and not (
                    unit.get("not_applicable_reason") or unit.get("assessment_exemption_reason")
                ):
                    errors.append(f"{unit_id} assessment exemption needs a reason")
                assessment_count += int(assessment_status == "defined")
            provenance_status = unit.get("provenance_status")
            if provenance_status not in ALLOWED_PROVENANCE:
                errors.append(f"{unit_id}.provenance_status is invalid")
            if provenance_status == "research-gap":
                research_gap_count += 1
            prereqs = unit.get("prerequisite_unit_ids")
            if not isinstance(prereqs, list):
                errors.append(f"{unit_id}.prerequisite_unit_ids must be a list")
            resources = unit.get("resource_ids")
            if not isinstance(resources, list):
                errors.append(f"{unit_id}.resource_ids must be a list")
            if not unit.get("source_row") and provenance_status != "research-gap":
                errors.append(f"{unit_id} needs source_row or research-gap provenance")
        if allocated is not None and not close(module_planned, allocated):
            errors.append(f"{module_id} unit hours {module_planned:g} != allocated {allocated:g}")
        for field, values in (("objectives", module.get("objectives")), ("competencies", module.get("competencies"))):
            if not isinstance(values, list) or not values:
                errors.append(f"{module_id}.{field} must be non-empty")
                continue
            covered = covered_objectives if field == "objectives" else covered_competencies
            for value in values:
                if value not in covered:
                    errors.append(f"{module_id} uncovered {field[:-1]} {value}")

    if target is not None and not close(total_planned, target):
        errors.append(f"program planned hours {total_planned:g} != target {target:g}")

    for unit_id, unit in unit_by_id.items():
        for dependency in unit.get("prerequisite_unit_ids") or []:
            if dependency not in unit_ids:
                errors.append(f"{unit_id} references missing prerequisite {dependency}")

    state = {}

    def visit(node, stack):
        if state.get(node) == 1:
            errors.append("prerequisite cycle: " + " -> ".join(stack + [node]))
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for dependency in unit_by_id.get(node, {}).get("prerequisite_unit_ids") or []:
            if dependency in unit_by_id:
                visit(dependency, stack + [node])
        state[node] = 2

    for unit_id in unit_ids:
        visit(unit_id, [])

    if args.profile:
        try:
            profile = json.loads(args.profile.read_text(encoding="utf-8"))
            if profile.get("canonical_sheet") != program.get("canonical_sheet"):
                errors.append("profile canonical_sheet disagrees with manifest")
            if profile.get("unit_count") and profile["unit_count"] > len(unit_by_id):
                errors.append("normalized manifest drops source unit candidates")
            if source is not None and profile.get("source_populated_hours") is not None:
                if not close(source, profile["source_populated_hours"]):
                    errors.append("profile source_populated_hours disagrees with manifest")
        except Exception as exc:
            errors.append(f"cannot read profile: {exc}")

    report = {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
        "target_hours": target,
        "planned_hours": round(total_planned, 2),
        "source_populated_hours": source,
        "missing_hours_at_ingestion": missing,
        "module_count": len(modules),
        "unit_count": len(unit_by_id),
        "research_gap_unit_count": research_gap_count,
        "defined_assessment_unit_count": assessment_count,
        "neo4j_sync_status": sync_status,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
