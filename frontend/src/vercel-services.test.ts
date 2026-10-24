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
  routes: { src?: string; status?: number; handle?: string; dest?: string }[];
  services?: unknown;
  rewrites?: unknown;
} {
  return JSON.parse(readFileSync(resolve(repositoryRoot, "vercel.json"), "utf8")) as {
    framework: string;
    installCommand: string;
    buildCommand: string;
    outputDirectory: string;
    headers: { source: string; headers: { key: string; value: string }[] }[];
    routes: { src?: string; status?: number; handle?: string; dest?: string }[];
    services?: unknown;
    rewrites?: unknown;
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
    expect(config.rewrites).toBeUndefined();
  });

  it("refuses API paths explicitly while the backend host is not provisioned", () => {
    const config = readRootVercelConfig();

    expect(config.routes[0]).toEqual({
      src: "^/api(?:/.*)?$",
      status: 404,
    });
    expect(config.routes[1]).toEqual({ handle: "filesystem" });
    expect(config.routes[2]).toEqual({
      src: "^/(.*)$",
      dest: "/index.html",
    });
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
