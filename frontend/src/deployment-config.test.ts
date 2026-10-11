/**
 * Consistency checks for the interface's deployment configuration.
 *
 * The built interface is served from three places and each one needs the same browser-facing policy:
 * the API answers JSON with its own headers (`backend/app/http_hardening.py`), Nginx serves the SPA
 * from disk (`deploy/nginx/talimgo.conf.example`), and Vercel serves it when the frontend is hosted
 * there (`frontend/vercel.json`). These tests keep the two static-server configurations from drifting
 * apart; the API's own policy is asserted in the backend test suite.
 *
 * They parse the checked-in configuration rather than exercising a server: `nginx -t` and the edge
 * smoke test cover the Nginx file itself, and the Vercel file can only be exercised by a deployment.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const repositoryRoot = resolve(__dirname, "..", "..");

function nginxHeaders(): Map<string, string> {
  const config = readFileSync(
    resolve(repositoryRoot, "deploy", "nginx", "talimgo.conf.example"),
    "utf8",
  );
  const headers = new Map<string, string>();
  const pattern = /^\s*add_header\s+(\S+)\s+"([^"]*)"/gm;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(config)) !== null) {
    headers.set(match[1].toLowerCase(), match[2]);
  }
  return headers;
}

function vercelHeaders(): Map<string, string> {
  const config = JSON.parse(readFileSync(resolve(__dirname, "..", "vercel.json"), "utf8")) as {
    headers: { source: string; headers: { key: string; value: string }[] }[];
  };
  const headers = new Map<string, string>();
  for (const rule of config.headers) {
    for (const header of rule.headers) headers.set(header.key.toLowerCase(), header.value);
  }
  return headers;
}

describe("deployment configuration", () => {
  it("serves the interface with the same browser-facing policy on Nginx and on Vercel", () => {
    expect(vercelHeaders()).toEqual(nginxHeaders());
  });

  it("never weakens framing, sniffing, referrer or transport protections", () => {
    const headers = vercelHeaders();
    expect(headers.get("x-frame-options")).toBe("DENY");
    expect(headers.get("x-content-type-options")).toBe("nosniff");
    expect(headers.get("referrer-policy")).toBe("no-referrer");
    expect(headers.get("strict-transport-security")).toBe("max-age=31536000");
    // includeSubDomains/preload are intentionally absent: they commit every current and future
    // subdomain to HTTPS and are the owner's decision, not a default.
    expect(headers.get("strict-transport-security")).not.toMatch(/includeSubDomains|preload/i);
  });

  it("keeps the content policy tight enough to be worth having", () => {
    const policy = vercelHeaders().get("content-security-policy") ?? "";
    expect(policy).toContain("default-src 'self'");
    expect(policy).toContain("frame-ancestors 'none'");
    expect(policy).toContain("object-src 'none'");
    expect(policy).toContain("connect-src 'self'");
    // No remote script/style origin may creep in: the interface is a local bundle.
    expect(policy).not.toMatch(/script-src[^;]*https?:/);
    expect(policy).not.toMatch(/style-src[^;]*https?:/);
  });

  it("applies the headers to every path Vercel serves", () => {
    const config = JSON.parse(readFileSync(resolve(__dirname, "..", "vercel.json"), "utf8")) as {
      headers: { source: string }[];
    };
    expect(config.headers).toHaveLength(1);
    expect(config.headers[0].source).toBe("/(.*)");
  });
});
