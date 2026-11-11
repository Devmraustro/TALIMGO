/**
 * Provisional TALIMGO symbol (master reference §9.4 direction: a "T" fused with a forward path —
 * a stroke that starts at a node and advances past checkpoints toward a terminal node).
 *
 * STATUS: PROVISIONAL / NOT CLEARANCE-APPROVED. The wordmark and mark may not ship in a production
 * form until DEC-001 (brand clearance search) and the owner's logo approval are complete. This
 * in-code symbol exists so the pre-launch interface is not designer-asset-blocked; it is geometric,
 * one-colour reproducible, and legible small, which are the reference's acceptance criteria.
 * Per §9.4 the symbol is never mirrored in RTL layouts.
 */
export function LogoMark({ size = 32, className }: { size?: number; className?: string }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 36 34"
      role="img"
      aria-label="TALIMGO"
      focusable="false"
    >
      {/* T crossbar */}
      <path
        d="M4 8h28"
        fill="none"
        stroke="currentColor"
        strokeWidth={3.4}
        strokeLinecap="round"
      />
      {/* Stem curving forward into the path to the terminal node */}
      <path
        d="M18 8v10.5A6.5 6.5 0 0 0 24.5 25H27"
        fill="none"
        stroke="currentColor"
        strokeWidth={3.4}
        strokeLinecap="round"
      />
      {/* Terminal chevron of the forward path */}
      <path
        d="M23.5 18.5 30 25l-6.5 6.5"
        fill="none"
        stroke="currentColor"
        strokeWidth={3.4}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Origin node — the single brand accent; a checkpoint the path has passed */}
      <circle cx="4" cy="8" r="3" fill="#D92D20" />
    </svg>
  );
}
