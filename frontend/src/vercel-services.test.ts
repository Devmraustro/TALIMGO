import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = resolve(__dirname, "..", "..");

function readRootVercelConfig(): {
  services: {
    web: { framework: string; root: string; buildCommand?: string; outputDirectory?: string };
    api: { framework: string; root: string; entrypoint: string };
  };
  rewrites: { source: string; destination: { service: string } }[];
} {
  return JSON.parse(readFileSync(resolve(repositoryRoot, "vercel.json"), "utf8")) as {
    services: {
      web: { framework: string; root: string; buildCommand?: string; outputDirectory?: string };
      api: { framework: string; root: string; entrypoint: string };
    };
    rewrites: { source: string; destination: { service: string } }[];
  };
}

describe("root Vercel Services configuration", () => {
  it("declares the Vite frontend and FastAPI backend under one project", () => {
    const config = readRootVercelConfig();

    expect(config.services.web.framework).toBe("vite");
    expect(config.services.web.root).toBe("frontend");
    expect(config.services.web.buildCommand).toBe("npm run build");
    expect(config.services.web.outputDirectory).toBe("dist");

    expect(config.services.api.framework).toBe("fastapi");
    expect(config.services.api.root).toBe("backend");
    expect(config.services.api.entrypoint).toBe("app.main:app");
  });

  it("routes API requests before the frontend catch-all", () => {
    const config = readRootVercelConfig();

    expect(config.rewrites).toHaveLength(2);
    expect(config.rewrites[0]).toEqual({
      source: "/api/(.*)",
      destination: { service: "api" },
    });
    expect(config.rewrites[1]).toEqual({
      source: "/(.*)",
      destination: { service: "web" },
    });
  });

  it("keeps the API service entrypoint tied to the FastAPI application", () => {
    const config = readRootVercelConfig();

    expect(config.services.api.entrypoint).toBe("app.main:app");
  });
});
