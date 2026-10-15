import { describe, expect, it, vi } from "vitest";
import { api, ApiError, NO_RESPONSE, onUnauthorized } from "./api";

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

  it("reports a request that produced no response as unreachable, not as a status code", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const failure = await api.get("/api/auth/me").catch((cause: unknown) => cause);

    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).status).toBe(NO_RESPONSE);
    expect((failure as ApiError).message).toMatch(/could not be reached/i);
    vi.unstubAllGlobals();
  });

  it("says so when the response is not a TALIMGO API response", async () => {
    // Exactly what a static host answers for /api/... when no API is deployed behind the interface:
    // a non-JSON error page, which previously surfaced to the learner as "Request failed (404).".
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response("<!doctype html><title>404: NOT_FOUND</title>", {
          status: 404,
          headers: { "content-type": "text/html" },
        }),
      ),
    );

    const failure = await api.get("/api/auth/me").catch((cause: unknown) => cause);

    expect(failure).toBeInstanceOf(ApiError);
    expect((failure as ApiError).status).toBe(404);
    expect((failure as ApiError).message).toMatch(/may be deployed without an API/i);
    vi.unstubAllGlobals();
  });

  it("still prefers the API's own JSON message over the generic one", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Unknown learning path." }), {
          status: 404,
          headers: { "content-type": "application/json" },
        }),
      ),
    );

    await expect(api.get("/api/curriculum/paths/nope")).rejects.toThrow("Unknown learning path.");
    vi.unstubAllGlobals();
  });

  it("reports an authenticated 401 to the registered listener, and stops when unregistered", async () => {
    const handler = vi.fn();
    const unsubscribe = onUnauthorized(handler);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Authentication required." }), {
          status: 401,
          headers: { "content-type": "application/json" },
        }),
      ),
    );

    await api.get("/api/dashboard").catch(() => undefined);
    expect(handler).toHaveBeenCalledTimes(1);

    // A 200 is not a session expiry.
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    await api.get("/api/dashboard");
    expect(handler).toHaveBeenCalledTimes(1);

    unsubscribe();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Authentication required." }), {
          status: 401,
          headers: { "content-type": "application/json" },
        }),
      ),
    );
    await api.get("/api/dashboard").catch(() => undefined);
    expect(handler).toHaveBeenCalledTimes(1);
    vi.unstubAllGlobals();
  });
});
