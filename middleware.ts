/**
 * The interface deployed on Vercel hosts no API (docs/DEPLOYMENT.md, "Where the built interface is
 * hosted"): the backend needs a long-lived process and lives on its own host once provisioned.
 *
 * This middleware keeps the documented contract that `/api/*` answers a bare 404 on this static
 * deployment. Configuration alone cannot express that on Vercel's current schema: the modern
 * `rewrites` form has no `status` field, and a rewrite to a destination that does not exist falls
 * through to the framework's SPA fallback (verified live on 2026-10-25). The interface's own API
 * client treats a non-JSON answer on an `/api/...` path as "no API behind this deployment", so the
 * learner-facing behaviour is honest either way; the middleware keeps the machine-readable contract
 * (health checks, monitors) exact.
 *
 * When a real API host exists, remove this file and add the rewrite that proxies `/api/*` to it —
 * the browser keeps a single origin, so cookies and CORS behaviour do not change.
 */
export const config = { matcher: "/api/:path*" };

export default function middleware(): Response {
  return new Response("This deployment hosts the interface only; no API is mounted here.\n", {
    status: 404,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
