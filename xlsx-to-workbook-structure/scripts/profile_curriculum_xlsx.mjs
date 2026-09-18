#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const args = process.argv.slice(2);
const inputPath = args[0];
const outputPath = args[1] || (inputPath ? inputPath.replace(/\.[^.]+$/, "") + ".profile.json" : "curriculum.profile.json");
const requestedSheet = args[2] || "Scenario Dev Blockchain Full St";

if (!inputPath) {
  console.error("Usage: profile_curriculum_xlsx.mjs <input.xlsx> [output.json] [canonical-sheet]");
  process.exit(2);
}

const clean = (value) => value == null ? "" : String(value).trim();
const numberOrNull = (value) => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const normalized = clean(value).replace(",", ".");
  if (!normalized || !/^-?\d+(?:\.\d+)?$/.test(normalized)) return null;
  const result = Number(normalized);
  return Number.isFinite(result) ? result : null;
};
const round = (value) => Math.round(value * 100) / 100;
const slugify = (value) => clean(value)
  .normalize("NFKD")
  .replace(/[\u0300-\u036f]/g, "")
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/^-+|-+$/g, "")
  .slice(0, 80);
const hash = (value) => crypto.createHash("sha256").update(value).digest("hex");
const isDurationControl = (row) => row.some((value) =>
  /heure\s+(?:total|voulue|manquante)/i.test(clean(value))
);

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheetInspection = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 30000 });
const sheetNames = [];
for (const line of String(sheetInspection.ndjson || "").split("\n").filter(Boolean)) {
  try {
    const record = JSON.parse(line);
    const name = record.name || record.sheetName;
    if (name && !sheetNames.includes(name)) sheetNames.push(name);
  } catch {
    // Ignore non-record inspection lines.
  }
}

if (!sheetNames.length) throw new Error("The workbook has no readable worksheets.");

const readRows = (name) => {
  const sheet = workbook.worksheets.getItem(name);
  const used = sheet.getUsedRange();
  return {
    name,
    address: used ? used.address : null,
    values: used && used.values ? used.values : []
  };
};

const candidates = sheetNames.map(readRows);
const canonical = candidates.find((item) => item.name === requestedSheet) ||
  candidates.find((item) => item.values.some((row) =>
    clean(row && row[0]).toLowerCase() === "module" &&
    (row || []).slice(4, 7).some((value) => /phase|durée|duration/i.test(clean(value)))
  ));

if (!canonical) throw new Error("Could not identify a canonical A:Q curriculum sheet. Requested: " + requestedSheet);

const rows = canonical.values;
const headerIndex = rows.findIndex((row) => clean(row && row[0]).toLowerCase() === "module");
if (headerIndex < 0) throw new Error("Canonical sheet " + canonical.name + " has no Module header.");

const columnMap = {
  A: "Module",
  B: "Module duration (days)",
  C: "Objectives",
  D: "Competencies",
  E: "Phase / LearningUnit",
  F: "Link",
  G: "Source duration (hours)",
  H: "Content type",
  I: "Intention",
  J: "Resources",
  K: "Suggested changes",
  L: "Exercises",
  M: "Quiz",
  N: "Professor evaluation",
  O: "Tools",
  P: "Prerequisites",
  Q: "Evaluation mode"
};

const programSlug = slugify(path.basename(inputPath, path.extname(inputPath)));
const modules = [];
const durationControls = {};
let current = null;
for (let index = headerIndex + 1; index < rows.length; index += 1) {
  const row = rows[index] || [];
  const rowText = row.map(clean).join(" ");
  const controlMatch = rowText.match(/HEURE\s+(TOTAL|VOULUE|MANQUANTE)/i);
  if (controlMatch) {
    durationControls[controlMatch[1].toLowerCase()] = numberOrNull(row[6]);
  }
  const moduleTitle = clean(row[0]);
  const declaredDays = numberOrNull(row[1]);
  if (moduleTitle && declaredDays !== null) {
    current = {
      id: "module:" + programSlug + ":M" + String(modules.length + 1).padStart(2, "0"),
      order: modules.length + 1,
      title: moduleTitle,
      declared_days: declaredDays,
      source_row: index + 1,
      source_objectives: clean(row[2]) || null,
      source_competencies: clean(row[3]) || null,
      units: []
    };
    modules.push(current);
  }
  if (!current || isDurationControl(row)) continue;
  const phaseTitle = clean(row[4]);
  const sourceLink = clean(row[5]);
  const sourceDuration = numberOrNull(row[6]);
  const resourceOnlyCandidate = !phaseTitle && sourceLink && sourceDuration !== null;
  const unitTitle = phaseTitle || (
    resourceOnlyCandidate
      ? (/^https?:\/\//i.test(sourceLink) ? "Supplementary resource from source row " + (index + 1) : sourceLink)
      : ""
  );
  if (!unitTitle) continue;
  const unitOrder = current.units.length + 1;
  current.units.push({
    id: current.id + ":U" + String(unitOrder).padStart(3, "0"),
    order: unitOrder,
    title: unitTitle,
    source_sheet: canonical.name,
    source_row: index + 1,
    source_link_or_resource: sourceLink || null,
    source_duration_hours: sourceDuration,
    content_type: clean(row[7]) || null,
    intention: clean(row[8]) || null,
    resources: clean(row[9]) || null,
    suggested_changes: clean(row[10]) || null,
    exercises: clean(row[11]) || null,
    quiz: row[12] == null ? null : row[12],
    professor_evaluation: clean(row[13]) || null,
    tools: clean(row[14]) || null,
    prerequisites: clean(row[15]) || null,
    evaluation_mode: clean(row[16]) || null
  });
}

for (const module of modules) {
  module.unit_count = module.units.length;
  module.source_populated_hours = round(module.units.reduce(
    (sum, unit) => sum + (unit.source_duration_hours == null ? 0 : unit.source_duration_hours), 0
  ));
}

const sourcePopulatedHours = round(modules.reduce(
  (sum, module) => sum + module.source_populated_hours, 0
));
const sourceBytes = await fs.readFile(inputPath);
const profile = {
  schema_version: "1.0",
  kind: "xlsx-curriculum-profile",
  source_file: inputPath,
  source_sha256: hash(sourceBytes),
  canonical_sheet: canonical.name,
  canonical_range: canonical.address,
  header_row: headerIndex + 1,
  primary_range: "A:Q",
  column_map: columnMap,
  supporting_sheets: sheetNames.filter((name) => name !== canonical.name),
  module_count: modules.length,
  unit_count: modules.reduce((sum, module) => sum + module.unit_count, 0),
  source_populated_hours: sourcePopulatedHours,
  source_duration_controls: durationControls,
  modules,
  notes: [
    "Blank Module cells inherit the current module for normalization only.",
    "Source duration is preserved separately from planned duration.",
    "Duration-control rows are not learning-unit candidates."
  ]
};

await fs.mkdir(path.dirname(path.resolve(outputPath)), { recursive: true });
await fs.writeFile(outputPath, JSON.stringify(profile, null, 2) + "\n");
console.log(JSON.stringify({
  status: "PASS",
  canonical_sheet: profile.canonical_sheet,
  module_count: profile.module_count,
  unit_count: profile.unit_count,
  source_populated_hours: profile.source_populated_hours,
  output: outputPath
}, null, 2));
