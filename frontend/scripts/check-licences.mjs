/**
 * Fail the build if any installed npm package carries an unacceptable licence.
 *
 * Same policy as backend/scripts/check_licences.py: AGPL, SSPL, BUSL and Commons Clause are refused;
 * GPL is refused unless it is clearly a build-only tool and was recorded in the reuse audit.
 *
 * Usage: node scripts/check-licences.mjs [--allow-gpl-build-tools]
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const allowGplBuildTools = process.argv.includes("--allow-gpl-build-tools");
const BLOCK = ["AGPL", "SSPL", "BUSL", "COMMONS CLAUSE", "EUPL"];
const WARN = ["GPL"];
const root = new URL("../node_modules/", import.meta.url).pathname;

function readLicence(packagePath) {
  try {
    const manifest = JSON.parse(readFileSync(join(packagePath, "package.json"), "utf8"));
    const licence = manifest.license ?? manifest.licenses ?? "";
    const text = Array.isArray(licence)
      ? licence.map((entry) => entry?.type ?? entry).join(" ")
      : typeof licence === "object"
        ? (licence.type ?? "")
        : String(licence);
    return { name: manifest.name ?? packagePath, text: text.toUpperCase() };
  } catch {
    return null;
  }
}

const failures = [];
const warnings = [];
let inspected = 0;

function walk(directory) {
  let entries;
  try {
    entries = readdirSync(directory);
  } catch {
    return;
  }
  if (entries.includes("package.json")) {
    const found = readLicence(directory);
    if (found) {
      inspected += 1;
      const blocked = BLOCK.find((token) => found.text.includes(token));
      if (blocked) {
        failures.push(`${found.name}: ${blocked} is not allowed`);
      } else {
        const warned = WARN.find((token) => found.text.includes(token));
        if (warned) {
          const message = `${found.name}: ${warned}`;
          if (allowGplBuildTools) warnings.push(message);
          else failures.push(message);
        }
      }
    }
  }
  for (const entry of entries) {
    if (entry === "node_modules" || entry.startsWith(".")) continue;
    const child = join(directory, entry);
    let stats;
    try {
      stats = statSync(child);
    } catch {
      continue;
    }
    if (stats.isDirectory()) walk(child);
  }
}

walk(root.replace(/\/$/, ""));

for (const warning of warnings) console.warn(`warning: ${warning}`);
if (failures.length > 0) {
  for (const failure of failures) console.error(`error: ${failure}`);
  process.exit(1);
}
if (inspected === 0) {
  console.error("error: no packages inspected — run npm install first");
  process.exit(1);
}
console.log(`licence check passed (${inspected} packages inspected)`);
