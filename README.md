# SignalOps

SignalOps is a small learning demo for structured log analysis. It uses synthetic data to show how logs, baselines, rule-based alerts, and runbooks can fit together in a basic AIOps workflow.

The project produces a fixed, reproducible example and is intended for code reading, local testing, and experimentation. It is not a production monitoring system.

## What the demo does

1. Reads and validates JSONL service logs.
2. Calculates service-level error rates and latency statistics.
3. Compares a current window with a static baseline.
4. Applies readable rules for error rate, latency, repeated error codes, and event volume.
5. Groups signals by service and attaches a short investigation checklist.
6. Writes a JSON report used by the static dashboard.

The included sample has three services and 900 current-window events. It is intentionally deterministic so that tests and dashboard output remain consistent.

## Run the analysis

Python 3.11 or later is recommended.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/generate_sample_logs.py
python3 -m signalops analyze \
  --input data/sample_logs.jsonl \
  --baseline data/baseline_logs.jsonl \
  --output public/data/report.json
python3 -m pytest
```

## Run the dashboard

Node.js 22 or later and pnpm are recommended.

```bash
pnpm install
pnpm run dev
```

To rebuild the static GitHub Pages files:

```bash
pnpm run export:pages
```

## Project map

```text
signalops/              Python analysis code
scripts/                Sample-data generator and static-site exporter
data/                   Synthetic baseline and current JSONL samples
public/data/report.json Generated analysis report
app/                    Dashboard source
tests_python/           Parser, detector, and pipeline tests
.github/workflows/      Automated checks and Pages deployment
docs/                   Architecture notes and a Chinese learning note
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the data flow and design choices. [`docs/LEARNING_GUIDE_ZH.md`](docs/LEARNING_GUIDE_ZH.md) records the concepts I am using this demo to study.

## Limits

- All logs are synthetic; no customer or production data is included.
- Detection uses fixed thresholds and a static baseline, not machine learning.
- There is no streaming input, database, cloud-platform integration, authentication, or automatic remediation.
- The generated runbook is a checklist selected by rules; it does not diagnose or fix a real incident.
- Results from this sample should not be treated as evidence of production reliability.

## License

MIT — see [`LICENSE`](LICENSE).
