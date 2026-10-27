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

  it("keeps the SPA fallback away from API paths", () => {
    const config = readRootVercelConfig();
    const rewrites = config.rewrites ?? [];

    // Everything that is not an API path falls back to the interface; /api/* is excluded here and
    // handled by the root middleware (below), because a rewrite to a missing destination falls
    // through to this very fallback instead of answering 404 (verified live on 2026-10-25).
    expect(rewrites).toHaveLength(1);
    expect(rewrites[0]).toEqual({
      source: "/((?!api/).*)",
      destination: "/index.html",
    });
  });

  it("answers API paths with a bare 404 through the root middleware", async () => {
    // The middleware is the only Vercel construct that can answer a path with a status code:
    // the modern config schema has no `status` field, and legacy `routes` (which can carry one)
    // is mutually exclusive with the headers block this file also needs.
    const { config, default: handler } = (await import("../../middleware")) as {
      config: { matcher: string };
      default: () => Response;
    };

    expect(config.matcher).toBe("/api/:path*");
    const response = handler();
    expect(response.status).toBe(404);
    expect(response.headers.get("content-type")).toContain("text/plain");
    expect(response.headers.get("cache-control")).toBe("no-store");
    const body = await response.text();
    expect(body).toContain("no API is mounted here");
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
