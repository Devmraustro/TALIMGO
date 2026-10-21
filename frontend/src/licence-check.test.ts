/**
 * Tests for the licence checker (scripts/check-licences.mjs).
 *
 * The checker is a build gate: it has to read the licences of the packages that are really
 * installed, and it has to fail rather than report a clean result when it cannot. These tests
 * run the script as a child process against fixture directories, so they cover the whole
 * contract — the directory it resolves, what it inspects, and what it does when the inspection
 * fails — on every platform, including the one where a URL-derived path cannot be opened.
 */

import { spawnSync } from "node:child_process";
import { cpSync, mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";

const checker = resolve(__dirname, "..", "scripts", "check-licences.mjs");
const frontendRoot = resolve(__dirname, "..");

interface Run {
  status: number;
  stdout: string;
  stderr: string;
}

function runChecker(script: string, cwd: string, args: string[] = []): Run {
  const result = spawnSync(process.execPath, [script, ...args], { cwd, encoding: "utf8" });
  return {
    status: result.status ?? -1,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? "",
  };
}

/** A directory laid out like the frontend: the script in `scripts/`, the packages beside it. */
function fixture(): { root: string; script: string } {
  const root = mkdtempSync(join(tmpdir(), "talimgo-licence-"));
  const script = join(root, "scripts", "check-licences.mjs");
  mkdirSync(join(root, "scripts"), { recursive: true });
  cpSync(checker, script);
  return { root, script };
}

function writePackage(root: string, name: string, licence: string): void {
  const directory = join(root, "node_modules", name);
  mkdirSync(directory, { recursive: true });
  writeFileSync(join(directory, "package.json"), JSON.stringify({ name, license: licence }), "utf8");
}

describe("the licence checker", () => {
  it("inspects the packages that are installed", () => {
    const result = runChecker(checker, frontendRoot);
    expect(result.status).toBe(0);
    const inspected = Number(result.stdout.match(/passed \((\d+) packages inspected\)/)?.[1] ?? "0");
    expect(inspected).toBeGreaterThan(0);
  });

  it("resolves its own directory rather than the working directory", () => {
    const { root, script } = fixture();
    writePackage(root, "talimgo-fixture-permissive", "MIT");
    // The working directory deliberately holds the real, populated node_modules: a checker that
    // looked there instead of beside itself would report the whole install, not the fixture.
    const result = runChecker(script, frontendRoot);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain("1 packages inspected");
  });

  it("refuses a package whose licence is not allowed", () => {
    const { root, script } = fixture();
    writePackage(root, "talimgo-fixture-refused", "AGPL-3.0-only");
    const result = runChecker(script, frontendRoot);
    expect(result.status).toBe(1);
    expect(result.stderr).toContain("AGPL");
    expect(result.stdout).not.toContain("passed");
  });

  it("does not report success when it cannot inspect the packages", () => {
    const { script } = fixture();
    const result = runChecker(script, frontendRoot);
    expect(result.status).not.toBe(0);
    expect(result.stdout).not.toContain("passed");
    expect(result.stderr).toContain("cannot inspect");
  });

  it("does not report success when there is nothing to inspect", () => {
    const { root, script } = fixture();
    mkdirSync(join(root, "node_modules"), { recursive: true });
    const result = runChecker(script, frontendRoot);
    expect(result.status).not.toBe(0);
    expect(result.stdout).not.toContain("passed");
    expect(result.stderr).toContain("no packages inspected");
  });
});
