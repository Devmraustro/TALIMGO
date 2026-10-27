import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = resolve(__dirname, "..", "..");

function readRootVercelConfig(): {
  framework: string;
  installCommand: string;
  buildCommand: string;
  outputDirectory: string;
  headers: { source: string; headers: { key: string; value: string }[] }[];
  routes?: unknown;
  services?: unknown;
  rewrites?: { source: string; destination: string }[];
} {
  return JSON.parse(readFileSync(resolve(repositoryRoot, "vercel.json"), "utf8")) as {
    framework: string;
    installCommand: string;
    buildCommand: string;
    outputDirectory: string;
    headers: { source: string; headers: { key: string; value: string }[] }[];
    routes?: unknown;
    services?: unknown;
    rewrites?: { source: string; destination: string }[];
  };
}

describe("root Vercel frontend-only configuration", () => {
  it("builds the Vite frontend from the repository root", () => {
    const config = readRootVercelConfig();

    expect(config.framework).toBe("vite");
    expect(config.installCommand).toBe("npm ci --prefix frontend");
    expect(config.buildCommand).toBe("npm run build --prefix frontend");
    expect(config.outputDirectory).toBe("frontend/dist");
    expect(config.services).toBeUndefined();
  });

  it("never combines legacy routes with modern routing properties", () => {
    // Vercel silently ignores `headers` (and rewrites/redirects) when the legacy `routes` key is
    // present. This bit for real: the deployment of 2026-10-25 served the interface with no CSP,
    // nosniff or X-Frame-Options because the headers block sat next to legacy routes. The modern
    // schema (rewrites + headers) is therefore the only acceptable shape here.
    const config = readRootVercelConfig();

    expect(config.routes).toBeUndefined();
    expect(config.rewrites).toBeDefined();
  });

  it("refuses API paths explicitly while the backend host is not provisioned", () => {
    const config = readRootVercelConfig();
    const rewrites = config.rewrites ?? [];

    // The API block must win before the SPA fallback, and its destination must not exist in the
    // build output, so Vercel answers 404 instead of serving the interface for /api paths.
    expect(rewrites[0]).toEqual({
      source: "/api/:path*",
      destination: "/api-not-hosted-here",
    });
    expect(rewrites[rewrites.length - 1]).toEqual({
      source: "/((?!api/).*)",
      destination: "/index.html",
    });
  });

  it("gives the backend project its own Python-only config", () => {
    // talimgo-api's root directory is backend/; without this file it inherited the root
    // frontend commands and failed every production build inside npm.
    const backend = JSON.parse(
      readFileSync(resolve(repositoryRoot, "backend", "vercel.json"), "utf8"),
    ) as Record<string, unknown>;
    expect(backend.framework).toBe("fastapi");
    expect(JSON.stringify(backend)).not.toContain("npm");
  });

  it("keeps security headers on all served paths", () => {
    const config = readRootVercelConfig();

    expect(config.headers).toHaveLength(1);
    expect(config.headers[0].source).toBe("/(.*)");
    const headers = new Map(config.headers[0].headers.map((header) => [
      header.key.toLowerCase(),
      header.value,
    ]));
    expect(headers.get("x-frame-options")).toBe("DENY");
    expect(headers.get("x-content-type-options")).toBe("nosniff");
    expect(headers.get("referrer-policy")).toBe("no-referrer");
    expect(headers.get("strict-transport-security")).toBe("max-age=31536000");
  });
});
