import type {
  Comparison,
  EvidenceItem,
  OverviewKey,
  Report,
  Status,
} from "./types";
import { downloadReport } from "./report";

const statuses: Status[] = ["matched", "partial", "missing", "unclear"];
const label = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);
const overview: [OverviewKey, string][] = [
  ["title", "Title"],
  ["employer", "Employer"],
  ["location", "Location"],
  ["work_arrangement", "Work arrangement"],
  ["employment_type", "Employment type"],
  ["salary", "Salary"],
  ["deadline", "Deadline"],
  ["working_hours", "Working hours"],
];

function Counts({
  items,
  category,
}: {
  items: Comparison[];
  category: string;
}) {
  const counts = statuses.map(
    (status) => items.filter((item) => item.status === status).length,
  );
  return (
    <div className="comparison-counts">
      <div
        className="count-bar"
        role="img"
        aria-label={`${category} comparison: ${counts.map((count, index) => `${count} ${statuses[index]}`).join(", ")}`}
      >
        {counts.map(
          (count, index) =>
            count > 0 && (
              <span
                key={statuses[index]}
                className={statuses[index]}
                style={{ flex: count }}
              />
            ),
        )}
      </div>
      <div className="count-labels">
        {statuses.map((status, index) => (
          <span key={status}>
            <span className={`swatch ${status}`} />
            {label(status)} <b>{counts[index]}</b>
          </span>
        ))}
      </div>
    </div>
  );
}

function EvidenceRow({
  item,
  comparison,
}: {
  item: EvidenceItem;
  comparison?: Comparison;
}) {
  return (
    <details className="evidence-row">
      <summary>
        <span className="qualification-text">{item.text}</span>
        {comparison && (
          <span className={`status ${comparison.status}`}>
            {label(comparison.status)}
          </span>
        )}
        <span className="evidence-toggle">
          Evidence{" "}
          <svg aria-hidden="true" viewBox="0 0 16 16" width="16" height="16">
            <path
              d="m4 6 4 4 4-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            />
          </svg>
        </span>
      </summary>
      <div className="evidence-body">
        <p className="small-label">Advertisement source</p>
        <blockquote>{item.quote}</blockquote>
        {comparison && (
          <>
            <p className="comparison-explanation">{comparison.explanation}</p>
            {comparison.evidence.map((evidence, index) => (
              <div key={index} className="profile-evidence">
                <p className="small-label">
                  Profile <code>{evidence.pointer}</code>
                </p>
                <blockquote>{evidence.quote}</blockquote>
              </div>
            ))}
            {!comparison.evidence.length && (
              <p className="muted">No supporting profile statement provided.</p>
            )}
          </>
        )}
      </div>
    </details>
  );
}

function Qualifications({
  report,
  kind,
  title,
}: {
  report: Report;
  kind: "required" | "preferred";
  title: string;
}) {
  const items = report.analysis[kind];
  const prefix = kind === "required" ? "r" : "p";
  const comparisons = (report.comparison ?? []).filter((item) =>
    item.requirement_id.startsWith(prefix),
  );
  return (
    <section aria-label={title} className="report-section">
      <div className="section-title">
        <h3>{title}</h3>
        <span className="small-label">
          {items.length} {items.length === 1 ? "item" : "items"}
        </span>
      </div>
      {report.comparison !== null && items.length > 0 && (
        <Counts items={comparisons} category={label(kind)} />
      )}
      {items.length ? (
        items.map((item, index) => (
          <EvidenceRow
            key={index}
            item={item}
            comparison={comparisons.find(
              (value) => value.requirement_id === `${prefix}${index + 1}`,
            )}
          />
        ))
      ) : (
        <p className="muted empty-category">
          None identified in the advertisement.
        </p>
      )}
    </section>
  );
}

export default function ReportView({
  report,
  stale,
}: {
  report: Report;
  stale: boolean;
}) {
  return (
    <article className="report-sheet" aria-label="Analysis results">
      <div className="report-toolbar">
        <span className="small-label">
          {report.simulated
            ? "Fictional demo / no API call"
            : "Job analysis / Gemini"}
        </span>
        <button
          type="button"
          className="text-button"
          onClick={() => downloadReport(report)}
        >
          Download JSON
        </button>
      </div>
      {stale && (
        <p className="stale-notice" role="status">
          Results belong to an earlier submission. Analyze again to reflect your
          changes.
        </p>
      )}
      <header className="report-heading">
        <h2>{report.analysis.overview.title?.text ?? "Untitled job"}</h2>
        <p className="small-label">
          {report.model} · {report.prompt}
        </p>
      </header>
      {report.simulated && (
        <p className="demo-notice">
          Simulated demonstration. These fixed fictional results were not
          generated by Gemini.
        </p>
      )}
      <section aria-label="Job overview" className="overview-section">
        <h3>Job overview</h3>
        <dl className="overview-grid">
          {overview.map(([key, title]) => {
            const item = report.analysis.overview[key];
            return (
              <div key={key}>
                <dt>{title}</dt>
                <dd>
                  {item ? (
                    <details className="overview-evidence">
                      <summary>{item.text}</summary>
                      <blockquote>{item.quote}</blockquote>
                    </details>
                  ) : (
                    <span className="not-provided">Not provided</span>
                  )}
                </dd>
              </div>
            );
          })}
        </dl>
      </section>
      {report.comparison !== null && (
        <p className="comparison-note">
          Profile comparison is self-reported, not independently verified. An
          omitted skill means unclear; missing requires an explicit negative
          statement.
        </p>
      )}
      <Qualifications
        report={report}
        kind="required"
        title="Required qualifications"
      />
      <Qualifications
        report={report}
        kind="preferred"
        title="Preferred qualifications"
      />
      {(
        [
          ["responsibilities", "Responsibilities"],
          ["application_materials", "Application materials"],
        ] as const
      ).map(([key, title]) => (
        <section key={key} aria-label={title} className="report-section">
          <div className="section-title">
            <h3>{title}</h3>
            <span className="small-label">
              {report.analysis[key].length}{" "}
              {report.analysis[key].length === 1 ? "item" : "items"}
            </span>
          </div>
          {report.analysis[key].length ? (
            report.analysis[key].map((item, index) => (
              <EvidenceRow key={index} item={item} />
            ))
          ) : (
            <p className="muted empty-category">
              None identified in the advertisement.
            </p>
          )}
        </section>
      ))}
      <section
        aria-label="Ambiguous or conflicting information"
        className="report-section"
      >
        <h3>Ambiguous or conflicting information</h3>
        {report.analysis.ambiguities.length ? (
          report.analysis.ambiguities.map((item, index) => (
            <details key={index} className="evidence-row">
              <summary>{item.text}</summary>
              <div className="evidence-body">
                {item.quotes.map((quote, i) => (
                  <blockquote key={i}>{quote}</blockquote>
                ))}
              </div>
            </details>
          ))
        ) : (
          <p className="muted empty-category">
            None identified. This does not guarantee the advertisement is
            complete.
          </p>
        )}
      </section>
      {report.comparison !== null && (
        <section className="portfolio-section">
          <h3>Portfolio availability</h3>
          <p>{report.portfolio_availability ?? "Not stated in the profile."}</p>
          <p className="muted">Self-reported; quality has not been assessed.</p>
        </section>
      )}
      <footer className="report-footnote">
        <p>
          Exact quotes verify text presence, not the correctness of its
          interpretation.
        </p>
        {report.usage?.total_tokens != null && (
          <p>
            {report.usage.total_tokens.toLocaleString()} total tokens reported
            by provider
          </p>
        )}
      </footer>
    </article>
  );
}
