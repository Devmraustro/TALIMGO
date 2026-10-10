import { describe, expect, it, vi } from "vitest";
import { api, ApiError } from "./api";

describe("api client", () => {
  it("always sends same-origin credentials and never an absolute host", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await api.get("/api/health");

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url.startsWith("/api/")).toBe(true);
    expect(url).not.toMatch(/^https?:\/\//);
    expect(init.credentials).toBe("same-origin");
    vi.unstubAllGlobals();
  });

  it("raises ApiError with the server's message", async () => {
    // A fresh Response per call: a Response body can only be consumed once.
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() =>
        Promise.resolve(
          new Response(JSON.stringify({ detail: "Tutoring is unavailable." }), {
            status: 503,
            headers: { "content-type": "application/json" },
          }),
        ),
      ),
    );

    await expect(api.post("/api/tutor/ask", {})).rejects.toBeInstanceOf(ApiError);
    await expect(api.post("/api/tutor/ask", {})).rejects.toThrow("Tutoring is unavailable.");
    vi.unstubAllGlobals();
  });

  it("surfaces validation problem lists as readable text", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(() =>
        Promise.resolve(
          new Response(JSON.stringify({ detail: { problems: ["Password is too common."] } }), {
            status: 422,
            headers: { "content-type": "application/json" },
          }),
        ),
      ),
    );

    await expect(api.post("/api/auth/register", {})).rejects.toThrow("Password is too common.");
    vi.unstubAllGlobals();
  });

  it("never talks to a known hosted AI provider", () => {
    const forbidden = ["openai.com", "anthropic.com", "generativelanguage", "api.groq.com"];
    const modules = import.meta.glob("./*.ts", { query: "?raw", import: "default", eager: true });
    for (const [path, contents] of Object.entries(modules)) {
      const text = String(contents).toLowerCase();
      for (const host of forbidden) {
        expect(text.includes(host), `${path} mentions ${host}`).toBe(false);
      }
    }
  });
});
