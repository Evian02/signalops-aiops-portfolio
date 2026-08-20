# SignalOps Architecture

## Goal

SignalOps is a deliberately small operational-analysis demo. Its purpose is to keep the data flow, assumptions, and failure modes easy to inspect. It is not a replacement for a production monitoring system.

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
7. **Publish** — serialize a machine-readable report consumed by the static dashboard.

## Why rule-based detection

This demo uses transparent rules because they keep the behavior easy to inspect:

- thresholds can be justified and tested;
- false positives are easier to investigate;
- each result can be traced back to its input and threshold;
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
