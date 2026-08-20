# SignalOps Architecture

## Goal

SignalOps demonstrates a complete but deliberately small operational-analysis workflow. It is not positioned as a production monitoring replacement. Its purpose is to make data flow, assumptions, failure modes, and verification easy to inspect.

## Data contract

Each JSONL record contains:

- ISO-8601 timestamp;
- service name and severity level;
- human-readable message;
- HTTP status and latency when available;
- trace and structured error identifiers.

The parser rejects malformed input with line-level error messages. This prevents silent data corruption from contaminating downstream metrics.

## Processing stages

1. **Parse and normalize** — validate required fields and sort records by time.
2. **Aggregate** — calculate total events, errors, warnings, error rate, average latency, and P95 latency per service.
3. **Compare** — evaluate the current window against a known baseline window.
4. **Detect** — run transparent rules for error rates, latency, volume, and repeated error codes.
5. **Correlate** — combine multiple signals for one service into a prioritized incident.
6. **Respond** — attach deterministic investigation steps selected by signal type.
7. **Publish** — serialize a machine-readable report consumed by the portfolio dashboard.

## Why rule-based detection

The SAP role explicitly includes both AI/ML and rule-based intelligence. For a first AIOps project, transparent rules provide several advantages:

- thresholds can be justified and tested;
- false positives are easier to investigate;
- the candidate can explain every decision in an interview;
- the design can later be extended with statistical or ML detectors without changing the rest of the pipeline.

The `anomaly_score` is an explainable prioritization score derived from threshold exceedance. It is not presented as a calibrated probability.

## Reliability choices

- deterministic synthetic data keeps builds reproducible;
- runtime analysis uses only the Python standard library;
- parser and pipeline failures are explicit;
- rules are modular and independently testable;
- the dashboard is generated from the same report tested in CI;
- GitHub Pages hosting does not require a long-running backend.

## Extension points

Good next iterations include rolling baselines, configurable YAML rules, SQL persistence, OpenTelemetry input, REST ingestion, Docker packaging, and an optional ML detector evaluated against the existing rule engine.
