/**
 * Types for `check-bundle.mjs` so the test file can import it under `tsc --noEmit`.
 *
 * The runtime script stays plain JavaScript (CI runs it with no build step); this file only describes
 * what it exports. Violations are plain strings, each beginning with the artifact they were found in.
 * Keep these declarations in sync when the script's signature changes — the test file is type-checked,
 * the script is not.
 */

/** Check one text artifact (the document or an asset) for local/private and insecure references. */
export function scanText(
  name: string,
  text: string,
  allowedInsecureHosts?: string[],
): string[];

/**
 * Check the served document itself: no inline script or style, no `<base>` tag, no cross-origin
 * reference, and every same-origin reference present in the build. `presentAssets` may be null when
 * only the document's own rules are being tested.
 */
export function scanHtml(
  text: string,
  presentAssets?: ((reference: string) => boolean) | null,
): string[];

/** Check a whole built directory. Returns an empty array when the bundle is acceptable. */
export function checkBundle(
  distDirectory: string,
  options?: { allowedInsecureHosts?: string[] },
): string[];

/** CLI entry point: returns the process exit code (0 pass, 1 violations). */
export function main(argv: string[]): number;
