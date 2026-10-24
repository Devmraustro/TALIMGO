#!/usr/bin/env bash
#
# Liveness/readiness probe for one TALIMGO API. Read-only: it never writes, never needs credentials and
# never creates an account, so it is safe to run from a supervisor, a systemd timer or a monitoring
# agent. Exit codes: 0 healthy, 1 unhealthy, 2 usage error.
#
# It checks the API's own recorded contract:
#   /api/health   -> HTTP 200 with {"status": "ok", ...}
#   /api/health/ai (--ai) -> HTTP 200 with the local-only policy reported, when tutoring is enabled
#
# Usage:
#   deploy/health-check.sh [--url http://127.0.0.1:8000] [--timeout 5] [--wait 0] [--ai]
#
# --wait SECONDS polls until the deadline instead of checking once. That is what a service unit uses
# after starting: a single immediate probe would race the process and report a false failure.

set -euo pipefail

URL="http://127.0.0.1:8000"
TIMEOUT=5
WAIT=0
CHECK_AI=0

while [ $# -gt 0 ]; do
  case "$1" in
    --url) URL="${2:-}"; shift 2 ;;
    --timeout) TIMEOUT="${2:-}"; shift 2 ;;
    --wait) WAIT="${2:-}"; shift 2 ;;
    --ai) CHECK_AI=1; shift ;;
    -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "health-check: unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v curl >/dev/null 2>&1 || { echo "health-check: curl is required" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "health-check: python3 is required" >&2; exit 2; }
case "$TIMEOUT" in ''|*[!0-9]*) echo "health-check: --timeout must be a whole number of seconds" >&2; exit 2 ;; esac
case "$WAIT" in ''|*[!0-9]*) echo "health-check: --wait must be a whole number of seconds" >&2; exit 2 ;; esac
case "$URL" in http://*|https://*) ;; *) echo "health-check: --url must start with http:// or https://" >&2; exit 2 ;; esac

probe_health() {
  local body
  body="$(curl -fsS --max-time "$TIMEOUT" "$URL/api/health" 2>/dev/null)" || return 1
  printf '%s' "$body" | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except ValueError:
    raise SystemExit("health-check: /api/health did not answer with JSON")
if payload.get("status") != "ok":
    raise SystemExit("health-check: /api/health reported status=" + repr(payload.get("status")))
' || return 1
  return 0
}

probe_ai() {
  local body
  body="$(curl -fsS --max-time "$TIMEOUT" "$URL/api/health/ai" 2>/dev/null)" || return 1
  printf '%s' "$body" | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except ValueError:
    raise SystemExit("health-check: /api/health/ai did not answer with JSON")
if payload.get("policy") != "local-only":
    raise SystemExit("health-check: AI policy is not local-only: " + repr(payload.get("policy")))
' || return 1
  return 0
}

deadline=$((SECONDS + WAIT))
attempt=0
while :; do
  attempt=$((attempt + 1))
  if probe_health; then
    if [ "$CHECK_AI" = "1" ] && ! probe_ai; then
      echo "health-check: API is up but the AI health check failed ($URL)" >&2
      exit 1
    fi
    echo "health-check: healthy ($URL/api/health, attempt $attempt)"
    exit 0
  fi
  [ "$SECONDS" -lt "$deadline" ] || break
  sleep 1
done
echo "health-check: unhealthy after $attempt attempt(s) ($URL/api/health)" >&2
exit 1
