import type { StringKey } from "../lib/i18n";

interface HelpPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
}

/**
 * Static help. Deliberately honest about the pre-MVP state: it promises no support channel,
 * response time or account-recovery path that does not exist yet (those become real only with
 * the owner's launch decisions; see master reference §19).
 */
export function HelpPanel({ t }: HelpPanelProps) {
  const sections: Array<{ title: StringKey; body: StringKey }> = [
    { title: "help.learningTitle", body: "help.learningBody" },
    { title: "help.goalTitle", body: "help.goalBody" },
    { title: "help.privacyTitle", body: "help.privacyBody" },
    { title: "help.statusTitle", body: "help.statusBody" },
  ];
  return (
    <section className="card" aria-labelledby="help-heading">
      <h2 id="help-heading">{t("help.title")}</h2>
      {sections.map((section) => (
        <div key={section.title}>
          <h3>{t(section.title)}</h3>
          <p className="muted">{t(section.body)}</p>
        </div>
      ))}
    </section>
  );
}
