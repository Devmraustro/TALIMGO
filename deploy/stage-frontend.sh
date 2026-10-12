#!/usr/bin/env bash
#
# Stage the built interface for a release, repeatably.
#
# What it does, in order:
#   1. builds the interface (`npm ci` + `npm run build`) unless --skip-build is given;
#   2. runs the release gate on the artifact (frontend/scripts/check-bundle.mjs) and stops if it fails,
#      so an insecure or local back-end address can never reach the served directory;
#   3. copies the build into a staging directory beside the target, then swaps it into place with
#      renames on the same filesystem — a reader either sees the old release or the new one, never a
#      half-copied directory;
#   4. keeps the previous release as `<target>.previous` for an immediate rollback (see --keep).
#
# It refuses to write anywhere that is not an explicit, non-system absolute path, refuses to run when
# the target's parent does not exist, and never touches anything outside `<target>` and its siblings.
#
# Usage:
#   deploy/stage-frontend.sh --target /srv/talimgo/frontend [--dist frontend/dist] [--skip-build] [--dry-run]
#
# Roll back (the previous release is a directory next to the target):
#   mv /srv/talimgo/frontend        /srv/talimgo/frontend.failed
#   mv /srv/talimgo/frontend.previous /srv/talimgo/frontend
# Nginx serves static files from disk, so no reload is needed; only clear the browser cache if the
# asset filenames did not change.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET=""
DIST="$REPO_ROOT/frontend/dist"
SKIP_BUILD=0
DRY_RUN=0
KEEP_PREVIOUS=1

# Anything at or above these is refused outright: a staging run must never reorganise a system path.
FORBIDDEN_TARGETS="/ /bin /boot /dev /etc /home /lib /lib64 /opt /proc /root /run /sbin /srv /sys /tmp /usr /var"

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --dist) DIST="${2:-}"; shift 2 ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --no-keep-previous) KEEP_PREVIOUS=0; shift ;;
    -h|--help) sed -n '2,26p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

say() { echo "stage-frontend: $*"; }
fail() { echo "stage-frontend: refusing to run: $*" >&2; exit 1; }

[ -n "$TARGET" ] || fail "--target is required (for example --target /srv/talimgo/frontend)"
case "$TARGET" in
  /*) ;;
  *) fail "--target must be an absolute path, got '$TARGET'" ;;
esac
case "$TARGET" in
  *..*) fail "--target must not contain '..'" ;;
esac
# Validate the raw value *before* normalising: stripping the trailing slash from "/" would leave an
# empty string, which would then sail past every remaining check.
[ "$TARGET" != "/" ] || fail "'/' is a system directory, not a release directory"
TARGET="${TARGET%/}"
[ -n "$TARGET" ] || fail "--target normalised to an empty path"
[ "$TARGET" != "/" ] || fail "'/' is a system directory, not a release directory"
for forbidden in $FORBIDDEN_TARGETS; do
  [ "$TARGET" != "$forbidden" ] || fail "'$TARGET' is a system directory, not a release directory"
done
case "$TARGET" in
  /*) ;;
  *) fail "--target normalised to a relative path: '$TARGET'" ;;
esac
TARGET_PARENT="$(dirname "$TARGET")"
[ -d "$TARGET_PARENT" ] || fail "the parent directory '$TARGET_PARENT' does not exist"
command -v node >/dev/null 2>&1 || fail "node is required to check the built bundle"

if [ "$DRY_RUN" = "1" ]; then
  say "dry run: would build=$([ "$SKIP_BUILD" = 1 ] && echo no || echo yes) from $DIST"
  say "dry run: would check the bundle, stage it beside $TARGET, then swap it into place"
  say "dry run: would keep the previous release as $TARGET.previous (keep=$KEEP_PREVIOUS)"
  exit 0
fi

if [ "$SKIP_BUILD" = "0" ]; then
  say "building the interface (npm ci, npm run build)"
  ( cd "$REPO_ROOT/frontend" && npm ci --no-audit --no-fund && npm run build )
fi

[ -f "$DIST/index.html" ] || fail "no build at $DIST — run the build (or drop --skip-build) first"
say "checking the build against the release gate"
node "$REPO_ROOT/frontend/scripts/check-bundle.mjs" --dist "$DIST"

STAGING="$TARGET.new.$$"
say "copying $DIST to $STAGING"
rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -R "$DIST"/. "$STAGING"/

# A served release must be world-readable regardless of the build user's umask.
chmod -R a+rX "$STAGING"

if [ -d "$TARGET" ] && [ "$KEEP_PREVIOUS" = "1" ]; then
  say "keeping the current release as $TARGET.previous"
  rm -rf "$TARGET.previous"
  mv "$TARGET" "$TARGET.previous"
fi
mv "$STAGING" "$TARGET"
say "staged $(find "$TARGET" -type f | wc -l | tr -d ' ') file(s) into $TARGET"
if [ "$KEEP_PREVIOUS" = "1" ] && [ -d "$TARGET.previous" ]; then
  say "rollback: mv '$TARGET' '$TARGET.failed' && mv '$TARGET.previous' '$TARGET'"
fi
say "done — serve '$TARGET' (the deployment guide's Nginx example uses /srv/talimgo/frontend/dist)"
