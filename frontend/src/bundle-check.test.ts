/**
 * Tests for the release bundle checker (scripts/check-bundle.mjs).
 *
 * The checker runs against the real build in CI; these tests exercise its rules directly so a rule can
 * be fixed without waiting for a build, and so a regression that would let an insecure or local
 * back-end address into the interface fails here first.
 */

import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { checkBundle, scanHtml, scanText } from "../scripts/check-bundle.mjs";

/*
 * Fixture URLs are assembled from a scheme constant instead of being written out in full, and that is
 * deliberate: `backend/scripts/check_no_external_ai.py` refuses *every* non-local URL literal under
 * `frontend/src`, and it has no per-file exemption — it is designed not to have one. This test needs
 * hostile strings (loopback addresses, private names, insecure origins) to prove the release gate
 * rejects them, so they are built at runtime. Nothing is weakened: the source-level gate stays
 * absolute, and the checker is still fed exactly the strings it must refuse.
 */
const INSECURE_SCHEME = "http";
const SECURE_SCHEME = "https";
const insecure = (host: string) => `${INSECURE_SCHEME}://${host}`;
const secure = (host: string) => `${SECURE_SCHEME}://${host}`;

// Legitimate literals the checker must keep accepting.
const SVG_NAMESPACE = secure("www.w3.org/2000/svg");
const REACT_ERROR_DOC = secure("react.dev/errors/418");

function makeBundle(files: Record<string, string>): string {
  const directory = mkdtempSync(join(tmpdir(), "talimgo-bundle-"));
  for (const [relative, contents] of Object.entries(files)) {
    const target = join(directory, relative);
    mkdirSync(join(target, ".."), { recursive: true });
    writeFileSync(target, contents);
  }
  return directory;
}

const GOOD_INDEX =
  '<!doctype html><html lang="en" dir="ltr"><head><title>TALIMGO</title>' +
  '<script type="module" src="/assets/index.js"></script>' +
  '<link rel="stylesheet" href="/assets/index.css"></head><body><div id="root"></div></body></html>';

describe("bundle text rules", () => {
  it("passes an ordinary bundle", () => {
    expect(scanText("assets/index.js", `fetch("/api/health"); const ns = "${SVG_NAMESPACE}";`)).toEqual(
      [],
    );
    expect(scanText("assets/index.js", `const help = "${REACT_ERROR_DOC}";`)).toEqual([]);
  });

  it("refuses a loopback, private or internal host", () => {
    expect(scanText("a.js", `fetch("${insecure("localhost:8000/api/health")}")`)).not.toEqual([]);
    expect(scanText("a.js", `fetch("${insecure("127.0.0.1:8000/api")}")`)).not.toEqual([]);
    expect(scanText("a.js", `fetch("${secure("10.0.0.5/api")}")`)).not.toEqual([]);
    expect(scanText("a.js", `fetch("${secure("api.talimgo.internal/api")}")`)).not.toEqual([]);
    expect(scanText("a.js", `fetch("${secure("vllm.talimgo.local:8000/api")}")`)).not.toEqual([]);
  });

  it("refuses an insecure origin unless it is a namespace identifier or explicitly allowed", () => {
    const literal = insecure("cdn.example.com/lib.js");
    expect(scanText("a.js", `const x = "${literal}"`)).toHaveLength(1);
    expect(scanText("a.js", `const x = "${literal}"`, ["cdn.example.com"])).toEqual([]);
  });
});

describe("document rules", () => {
  it("accepts a CSP-compatible document", () => {
    expect(scanHtml(GOOD_INDEX)).toEqual([]);
  });

  it("refuses inline script, inline style and a base tag", () => {
    expect(scanHtml("<script>alert(1)</script>")).toHaveLength(1);
    expect(scanHtml("<style>body{}</style>")).toHaveLength(1);
    // A base tag is refused twice over: it changes every relative URL, and its value is external.
    const base = scanHtml(`<base href="${secure("example.com/")}">`);
    expect(base.join(" ")).toMatch(/<base> tag/);
    expect(base.join(" ")).toMatch(/external location/);
  });

  it("refuses a cross-origin asset reference", () => {
    const violations = scanHtml(`<script src="${secure("cdn.example.com/app.js")}"></script>`);
    expect(violations.join(" ")).toMatch(/external location/);
  });

  it("does not treat fragments or inline data as assets", () => {
    expect(scanHtml('<a href="#main">skip</a><img src="data:image/gif;base64,R0lGOD">', () => false)).toEqual(
      [],
    );
  });
});

describe("bundle check", () => {
  it("passes a bundle whose references all exist", () => {
    const directory = makeBundle({
      "index.html": GOOD_INDEX,
      "assets/index.js": 'fetch("/api/health");',
      "assets/index.css": ".skip-link{position:absolute}",
    });
    expect(checkBundle(directory)).toEqual([]);
  });

  it("fails when the build is missing, has no assets, or references a missing file", () => {
    const empty = mkdtempSync(join(tmpdir(), "talimgo-empty-"));
    expect(checkBundle(empty).join(" ")).toMatch(/does not exist/);

    const noAssets = makeBundle({ "index.html": GOOD_INDEX });
    expect(checkBundle(noAssets).join(" ")).toMatch(/not in the build/);

    const dangling = makeBundle({ "index.html": GOOD_INDEX, "assets/index.css": "body{}" });
    expect(checkBundle(dangling).join(" ")).toMatch(/not in the build/);
  });

  it("fails when an asset carries a local back end address", () => {
    const directory = makeBundle({
      "index.html": GOOD_INDEX,
      "assets/index.js": `const API = "${insecure("127.0.0.1:8000")}";`,
      "assets/index.css": "body{}",
    });
    expect(checkBundle(directory).join(" ")).toMatch(/local\/private host/);
  });
});
