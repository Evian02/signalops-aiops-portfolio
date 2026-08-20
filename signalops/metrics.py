from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import ceil

from .models import LogRecord, ServiceMetrics


def percentile(values: list[float], percentile_value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, ceil(percentile_value * len(ordered)) - 1)
    return round(ordered[index], 2)


def is_error(record: LogRecord) -> bool:
    return record.level == "ERROR" or bool(
        record.status_code is not None and record.status_code >= 500
    )


def calculate_metrics(records: list[LogRecord], service: str) -> ServiceMetrics:
    relevant = [record for record in records if record.service == service]
    latencies = [record.latency_ms for record in relevant if record.latency_ms is not None]
    errors = sum(is_error(record) for record in relevant)
    warnings = sum(record.level == "WARN" for record in relevant)
    total = len(relevant)
    return ServiceMetrics(
        service=service,
        total=total,
        errors=errors,
        warnings=warnings,
        error_rate=round(errors / total, 4) if total else 0.0,
        p95_latency_ms=percentile(latencies, 0.95),
        average_latency_ms=round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
    )


def calculate_all_services(records: list[LogRecord]) -> list[ServiceMetrics]:
    services = sorted({record.service for record in records})
    return [calculate_metrics(records, service) for service in services]


def build_timeline(records: list[LogRecord], bucket_minutes: int = 5) -> list[dict[str, object]]:
    buckets: dict[tuple[str, datetime], list[LogRecord]] = defaultdict(list)
    for record in records:
        bucket = record.timestamp.replace(
            minute=(record.timestamp.minute // bucket_minutes) * bucket_minutes,
            second=0,
            microsecond=0,
        )
        buckets[(record.service, bucket)].append(record)

    timeline: list[dict[str, object]] = []
    for (service, bucket), bucket_records in sorted(
        buckets.items(), key=lambda item: (item[0][1], item[0][0])
    ):
        metrics = calculate_metrics(bucket_records, service)
        timeline.append(
            {
                "timestamp": bucket.isoformat(),
                "service": service,
                "total": metrics.total,
                "errors": metrics.errors,
                "error_rate": metrics.error_rate,
                "p95_latency_ms": metrics.p95_latency_ms,
            }
        )
    return timeline
