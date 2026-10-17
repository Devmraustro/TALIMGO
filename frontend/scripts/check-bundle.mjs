/**
 * Release gate for the built interface.
 *
 * The checks here are the ones a *build artifact* can fail even when the source is correct, and they
 * are the ones that matter for a deployment behind one origin:
 *
 *   1. no insecure (`http://`) or local/private host is baked into the bundle — the interface must
 *      reach the API on its own origin, never a hard-coded `localhost`, LAN address or unknown
 *      back end (docs/DEPLOYMENT.md, "Where the built interface is hosted");
 *   2. `index.html` carries no inline `<script>`/`<style>` and no cross-origin or `<base>` reference,
 *      because the deployment serves it under `script-src 'self'` / `style-src 'self' 'unsafe-inline'`
 *      (deploy/nginx/talimgo.conf.example, frontend/vercel.json);
 *   3. every asset `index.html` references is actually present in the build.
 *
 * Usage: node scripts/check-bundle.mjs [--dist dist] [--allow-insecure-host HOST]
 *
 * Namespace identifiers (`http://www.w3.org/...`) are exempt from (1): they are XML/SVG namespace
 * names the DOM compares as strings, never addresses a browser fetches. `--allow-insecure-host` exists
 * for an operator who genuinely must bundle another insecure origin, and requires naming it.
 */

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const NAMESPACE_HOSTS = new Set(["www.w3.org"]);
// Sources, not shared regex objects: a module-level global regex carries `lastIndex` between calls,
// which makes scanning order matter. Each scan builds a fresh regex from these.
const LOOPBACK_SOURCE = String.raw`(?:^|[^0-9a-z.-])(localhost|127\.\d+\.\d+\.\d+|0\.0\.0\.0|\[::1\]|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b`;
// Any number of labels before .internal/.local, so `api.talimgo.internal` is caught too.
const PRIVATE_NAME_SOURCE = String.raw`(?:^|[^0-9a-z.-])((?:[a-z0-9-]+\.)+(?:internal|local|localdomain))\b`;
const INSECURE_SOURCE = String.raw`http:\/\/([a-z0-9.-]+)`;
const REFERENCED_ASSET_SOURCE = String.raw`(?:src|href)="([^"]+)"`;
const INLINE_SCRIPT = /<script(?![^>]*\bsrc=)[^>]*>[\s\S]*?<\/script>/i;
const INLINE_STYLE = /<style[\s>]/i;
const BASE_TAG = /<base\b[^>]*>/i;

/** Collect violations in one text artifact. Pure, so it can be unit-tested without a build. */
export function scanText(name, text, allowedInsecureHosts = []) {
  const violations = [];
  for (const source of [LOOPBACK_SOURCE, PRIVATE_NAME_SOURCE]) {
    for (const match of text.matchAll(new RegExp(source, "gi"))) {
      violations.push(`${name}: refers to the local/private host ${match[1]}`);
    }
  }
  for (const match of text.matchAll(new RegExp(INSECURE_SOURCE, "gi"))) {
    const candidate = match[1].toLowerCase();
    if (NAMESPACE_HOSTS.has(candidate) || allowedInsecureHosts.includes(candidate)) continue;
    violations.push(`${name}: uses the insecure origin http://${candidate}`);
  }
  return violations;
}

/** Check the served document: no inline code, no cross-origin reference, assets present. */
export function scanHtml(text, presentAssets = null) {
  const violations = [];
  if (INLINE_SCRIPT.test(text)) {
    violations.push("index.html: contains an inline <script>, which the deployment CSP blocks");
  }
  if (INLINE_STYLE.test(text)) {
    violations.push("index.html: contains an inline <style>, which the deployment CSP blocks");
  }
  if (BASE_TAG.test(text)) {
    violations.push("index.html: contains a <base> tag, which would change every relative URL");
  }
  for (const match of text.matchAll(new RegExp(REFERENCED_ASSET_SOURCE, "gi"))) {
    const reference = match[1];
    if (reference.startsWith("#") || reference.startsWith("data:")) continue;
    if (/^[a-z][a-z0-9+.-]*:/i.test(reference) || reference.startsWith("//")) {
      violations.push(`index.html: references the external location ${reference}`);
      continue;
    }
    if (presentAssets && !presentAssets(reference)) {
      violations.push(`index.html: references ${reference}, which is not in the build`);
    }
  }
  return violations;
}

function collectPresentAssets(distDirectory) {
  const assets = new Set();
  const walk = (directory, prefix) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const relative = `${prefix}${entry.name}`;
      if (entry.isDirectory()) walk(join(directory, entry.name), `${relative}/`);
      else assets.add(`/${relative}`);
    }
  };
  const assetsDirectory = join(distDirectory, "assets");
  if (existsSync(assetsDirectory)) walk(assetsDirectory, "assets/");
  return assets;
}

export function checkBundle(distDirectory, { allowedInsecureHosts = [] } = {}) {
  const violations = [];
  const indexPath = join(distDirectory, "index.html");
  if (!existsSync(indexPath)) {
    return [`${indexPath} does not exist — run the build first`];
  }

  const assets = collectPresentAssets(distDirectory);
  const indexText = readFileSync(indexPath, "utf8");
  violations.push(
    ...scanText("index.html", indexText, allowedInsecureHosts),
    ...scanHtml(indexText, (reference) => {
      const path = reference.startsWith(".") ? reference.replace(/^\./, "") : reference;
      return assets.has(path);
    }),
  );

  const assetsDirectory = join(distDirectory, "assets");
  const files = existsSync(assetsDirectory) ? readdirSync(assetsDirectory) : [];
  for (const file of files) {
    const text = readFileSync(join(assetsDirectory, file), "utf8");
    violations.push(...scanText(`assets/${file}`, text, allowedInsecureHosts));
  }
  if (files.length === 0) violations.push("assets/: the build produced no assets");
  return violations;
}

export function main(argv) {
  const distIndex = argv.indexOf("--dist");
  const distDirectory = distIndex === -1 ? "dist" : argv[distIndex + 1];
  const allowedInsecureHosts = argv
    .map((argument, position) => (argument === "--allow-insecure-host" ? argv[position + 1] : null))
    .filter(Boolean)
    .map((value) => value.toLowerCase());

  const violations = checkBundle(distDirectory, { allowedInsecureHosts });
  if (violations.length > 0) {
    for (const violation of violations) console.error(`error: ${violation}`);
    console.error(`bundle check failed (${violations.length} problem(s)) in ${distDirectory}`);
    return 1;
  }
  console.log(`bundle check passed (${distDirectory}: same-origin assets, no local or insecure host)`);
  return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exit(main(process.argv.slice(2)));
}
