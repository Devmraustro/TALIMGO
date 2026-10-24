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
import { fileURLToPath } from "node:url";

const allowGplBuildTools = process.argv.includes("--allow-gpl-build-tools");
const BLOCK = ["AGPL", "SSPL", "BUSL", "COMMONS CLAUSE", "EUPL"];
const WARN = ["GPL"];
// `URL.pathname` is a URL component, not a filesystem path: on Windows it starts with "/C:/..." and
// no filesystem call can open it, so the walk would find nothing and report an empty result.
// `fileURLToPath` gives the real path of the directory holding this script on every platform.
const root = fileURLToPath(new URL("../node_modules/", import.meta.url));

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
const unreadable = [];
let inspected = 0;

function walk(directory) {
  let entries;
  try {
    entries = readdirSync(directory);
  } catch (error) {
    // A directory that cannot be listed is a package whose licence is unknown. Record it and fail
    // below rather than skipping it, so a broken path cannot be mistaken for a clean result.
    unreadable.push(`${directory} (${error.code ?? error.message})`);
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

walk(root);

for (const warning of warnings) console.warn(`warning: ${warning}`);
if (failures.length > 0) {
  for (const failure of failures) console.error(`error: ${failure}`);
  process.exit(1);
}
if (unreadable.length > 0) {
  for (const directory of unreadable) console.error(`error: cannot inspect ${directory}`);
  process.exit(1);
}
if (inspected === 0) {
  console.error("error: no packages inspected — run npm install first");
  process.exit(1);
}
console.log(`licence check passed (${inspected} packages inspected)`);
