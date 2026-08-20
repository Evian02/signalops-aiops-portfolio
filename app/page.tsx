import type { CSSProperties } from "react";
import reportJson from "../public/data/report.json";

type ServiceMetrics = {
  service: string;
  total: number;
  errors: number;
  warnings: number;
  error_rate: number;
  p95_latency_ms: number;
  average_latency_ms: number;
};

type Signal = {
  service: string;
  kind: string;
  severity: string;
  title: string;
  observed: number;
  baseline: number;
  anomaly_score: number;
  evidence: string;
  runbook_id: string;
};

type Incident = {
  incident_id: string;
  service: string;
  severity: string;
  title: string;
  summary: string;
  signal_kinds: string[];
  recommended_actions: string[];
};

type TimelinePoint = {
  timestamp: string;
  service: string;
  total: number;
  errors: number;
  error_rate: number;
  p95_latency_ms: number;
};

type Report = {
  meta: { generated_at: string; detection_mode: string; engine_version: string };
  summary: {
    total_logs: number;
    total_errors: number;
    overall_error_rate: number;
    services_monitored: number;
    signals_detected: number;
    incidents_opened: number;
    critical_incidents: number;
  };
  services: ServiceMetrics[];
  signals: Signal[];
  incidents: Incident[];
  timeline: TimelinePoint[];
};

const report = reportJson as Report;

const pipeline = [
  { index: "01", name: "Ingest", detail: "Read structured JSONL events from multiple services." },
  { index: "02", name: "Normalize", detail: "Validate timestamps, severity, latency, status, and trace context." },
  { index: "03", name: "Baseline", detail: "Calculate service-level error rates and P95 latency ranges." },
  { index: "04", name: "Detect", detail: "Apply explainable rules to surface abnormal operational behavior." },
  { index: "05", name: "Respond", detail: "Group related signals and attach a practical investigation runbook." },
];

function percent(value: number) {
  return `${(value * 100).toFixed(value >= 0.1 ? 1 : 2)}%`;
}

function serviceStatus(service: ServiceMetrics) {
  if (service.error_rate >= 0.1) return "critical";
  if (service.error_rate >= 0.05) return "warning";
  return "healthy";
}

export default function Home() {
  const primarySignal = report.signals[0];
  const incident = report.incidents[0];
  const checkoutTimeline = report.timeline.filter((point) => point.service === "checkout-api");
  const generatedTime = new Date(report.meta.generated_at).toLocaleString("en-GB", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "UTC",
  });
  const consoleOutput = JSON.stringify(
    {
      service: primarySignal.service,
      severity: primarySignal.severity,
      signal: primarySignal.kind,
      observed: primarySignal.observed,
      baseline: primarySignal.baseline,
      anomaly_score: primarySignal.anomaly_score,
      runbook: primarySignal.runbook_id,
    },
    null,
    2,
  );

  return (
    <main>
      <nav className="site-nav" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="SignalOps home">
          <span className="brand-mark">S</span>
          <span>SignalOps</span>
        </a>
        <div className="nav-links">
          <a href="#dashboard">Dashboard</a>
          <a href="#pipeline">Pipeline</a>
          <a href="#repository">Evidence</a>
          <a className="nav-cta" href="https://github.com/Evian02/signalops-aiops-portfolio">GitHub ↗</a>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Structured log analysis · learning demo</p>
          <h1>Turn noisy logs into<br /><em>actionable signals.</em></h1>
          <p className="hero-text">
            A small rule-based demo that reads synthetic service logs, compares
            them with a baseline, groups related signals, and produces a static
            investigation checklist.
          </p>
          <div className="hero-actions">
            <a className="button primary" href="#dashboard">Explore the report</a>
            <a className="button secondary" href="#pipeline">Read the architecture</a>
          </div>
          <div className="tech-line" aria-label="Technology stack">
            <span>Python</span><span>Rule engine</span><span>GitHub Actions</span><span>Pytest</span>
          </div>
        </div>

        <div className="console-card" aria-label="Sample anomaly detection output">
          <div className="console-head">
            <div className="window-dots" aria-hidden="true"><i /><i /><i /></div>
            <span>latest-analysis.json</span>
            <b>SAMPLE REPORT</b>
          </div>
          <pre>{consoleOutput}</pre>
          <div className="pulse-line"><span /><small>Sample report generated {generatedTime} UTC</small></div>
        </div>
      </section>

      <section className="dashboard" id="dashboard">
        <div className="content-shell">
          <div className="section-heading">
            <div>
              <p className="eyebrow"><span /> Operational overview</p>
              <h2>One report. Clear priorities.</h2>
            </div>
            <div className="status"><span /> Analysis complete</div>
          </div>

          <div className="metric-grid">
            <article className="metric-card">
              <p>Logs analyzed</p><strong>{report.summary.total_logs.toLocaleString()}</strong>
              <small>Across {report.summary.services_monitored} services</small>
            </article>
            <article className="metric-card">
              <p>Signals detected</p><strong>{report.summary.signals_detected}</strong>
              <small>{report.summary.incidents_opened} correlated incident</small>
            </article>
            <article className="metric-card">
              <p>Overall error rate</p><strong>{percent(report.summary.overall_error_rate)}</strong>
              <small>{report.summary.total_errors} error events</small>
            </article>
            <article className="metric-card emphasis">
              <p>Highest anomaly score</p><strong>{Math.round(primarySignal.anomaly_score * 100)}</strong>
              <small>Explainable rule score / 100</small>
            </article>
          </div>

          <div className="analysis-grid">
            <article className="chart-card">
              <div className="card-heading">
                <div><span className="mini-label">checkout-api</span><h3>Error-rate timeline</h3></div>
                <span className="chart-legend"><i /> Errors / 5 min</span>
              </div>
              <div className="bar-chart" aria-label="Checkout API error-rate timeline">
                {checkoutTimeline.map((point) => {
                  const height = Math.max(5, Math.min(100, point.error_rate * 220));
                  return (
                    <div className="bar-column" key={point.timestamp}>
                      <span className="bar-value">{Math.round(point.error_rate * 100)}%</span>
                      <div className="bar-track"><i style={{ "--bar-height": `${height}%` } as CSSProperties} /></div>
                      <small>{new Date(point.timestamp).toISOString().slice(11, 16)}</small>
                    </div>
                  );
                })}
              </div>
            </article>

            <article className="incident-panel">
              <div className="incident-meta">
                <span className={`severity ${incident.severity}`}>{incident.severity}</span>
                <small>{incident.incident_id} · {incident.service}</small>
              </div>
              <h3>{incident.title}</h3>
              <p>{incident.summary}</p>
              <div className="signal-tags">
                {incident.signal_kinds.map((kind) => <span key={kind}>{kind.replaceAll("_", " ")}</span>)}
              </div>
            </article>
          </div>

          <article className="service-table-card">
            <div className="card-heading"><div><span className="mini-label">Service health</span><h3>Metrics by component</h3></div></div>
            <div className="service-table" role="table" aria-label="Service health metrics">
              <div className="service-row table-head" role="row">
                <span>Service</span><span>Status</span><span>Events</span><span>Error rate</span><span>P95 latency</span>
              </div>
              {report.services.map((service) => {
                const status = serviceStatus(service);
                return (
                  <div className="service-row" role="row" key={service.service}>
                    <strong>{service.service}</strong>
                    <span className={`health ${status}`}><i />{status}</span>
                    <span>{service.total}</span><span>{percent(service.error_rate)}</span><span>{Math.round(service.p95_latency_ms)} ms</span>
                  </div>
                );
              })}
            </div>
          </article>
        </div>
      </section>

      <section className="pipeline-section" id="pipeline">
        <div className="content-shell">
          <div className="section-intro">
            <p className="eyebrow"><span /> Analysis pipeline</p>
            <h2>Explainable by design.</h2>
            <p>No black box and no invented certainty. Every incident links back to measured evidence, a documented threshold, and a practical response.</p>
          </div>
          <div className="pipeline-grid">
            {pipeline.map((step) => (
              <article key={step.index}>
                <span>{step.index}</span><h3>{step.name}</h3><p>{step.detail}</p>
              </article>
            ))}
          </div>

          <div className="runbook-layout">
            <div className="runbook-copy">
              <span className="mini-label">Automated runbook · {primarySignal.runbook_id}</span>
              <h3>Detection is only useful when it leads to action.</h3>
              <p>SignalOps converts correlated evidence into a short, reviewable investigation path. The recommendations are deterministic and can be tested alongside the detection rules.</p>
            </div>
            <ol className="runbook-list">
              {incident.recommended_actions.map((action, index) => (
                <li key={action}><span>{String(index + 1).padStart(2, "0")}</span><p>{action}</p></li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <section className="engineering-section" id="repository">
        <div className="content-shell engineering-grid">
          <div className="section-intro compact">
            <p className="eyebrow"><span /> Repository notes</p>
            <h2>Small enough to inspect and run locally.</h2>
            <p>The demo uses deterministic synthetic data, modular Python code, automated checks, and a reproducible report. It is intended for code reading and experimentation, not production monitoring.</p>
          </div>
          <div className="evidence-grid">
            <article><strong>1,800</strong><span>Deterministic sample and baseline log events</span></article>
            <article><strong>4</strong><span>Automated tests for parsing, detection, and integration</span></article>
            <article><strong>0</strong><span>Runtime Python dependencies</span></article>
            <article><strong>CI</strong><span>Tests and report generation on every push</span></article>
          </div>
        </div>
      </section>

      <footer>
        <div className="content-shell footer-inner">
          <a className="brand" href="#top"><span className="brand-mark">S</span><span>SignalOps</span></a>
          <a className="footer-profile" href="https://github.com/Evian02">De Huo · GitHub ↗</a>
          <a className="back-to-top" href="#top">Back to top ↑</a>
        </div>
      </footer>
    </main>
  );
}
