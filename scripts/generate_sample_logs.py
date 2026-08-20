from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RANDOM = random.Random(610041)
SERVICES = ("auth-service", "catalog-api", "checkout-api")


def make_record(timestamp: datetime, service: str, index: int, mode: str) -> dict[str, object]:
    normal_latency = {"auth-service": 120, "catalog-api": 180, "checkout-api": 240}[service]
    status_code = 200
    level = "INFO"
    error_code = ""
    message = "request completed"
    latency = max(20, RANDOM.gauss(normal_latency, normal_latency * 0.22))

    if mode == "current" and service == "checkout-api" and index >= 190:
        if index % 4 == 0:
            status_code = 503
            level = "ERROR"
            error_code = "UPSTREAM_TIMEOUT"
            message = "payment dependency timed out"
            latency = RANDOM.uniform(1700, 2600)
        elif index % 7 == 0:
            status_code = 500
            level = "ERROR"
            error_code = "PAYMENT_REJECTED"
            message = "checkout request failed"
            latency = RANDOM.uniform(900, 1600)
        else:
            latency = RANDOM.uniform(850, 1500)
    elif RANDOM.random() < 0.012:
        status_code = 500
        level = "ERROR"
        error_code = "TRANSIENT_ERROR"
        message = "transient request failure"
    elif RANDOM.random() < 0.025:
        level = "WARN"
        message = "request completed after retry"

    return {
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "service": service,
        "level": level,
        "message": message,
        "status_code": status_code,
        "latency_ms": round(latency, 2),
        "trace_id": f"{service[:4]}-{mode[:1]}-{index:04d}",
        "error_code": error_code,
    }


def generate(path: Path, mode: str, events_per_service: int, start: datetime) -> None:
    rows: list[dict[str, object]] = []
    for service in SERVICES:
        for index in range(events_per_service):
            timestamp = start + timedelta(seconds=index * 6)
            rows.append(make_record(timestamp, service, index, mode))
    rows.sort(key=lambda row: (str(row["timestamp"]), str(row["service"])))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> None:
    baseline_start = datetime(2026, 8, 19, 9, 0, tzinfo=timezone.utc)
    current_start = datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc)
    generate(DATA / "baseline_logs.jsonl", "baseline", 300, baseline_start)
    generate(DATA / "sample_logs.jsonl", "current", 300, current_start)
    print("generated 1,800 deterministic log records")


if __name__ == "__main__":
    main()
