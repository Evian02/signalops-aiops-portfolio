from __future__ import annotations

from collections import Counter

from .metrics import calculate_all_services, calculate_metrics, is_error
from .models import LogRecord, ServiceMetrics, Signal


SEVERITY_RANK = {"info": 0, "warning": 1, "high": 2, "critical": 3}


def _score(ratio: float, cap: float = 0.99) -> float:
    return round(min(cap, max(0.0, 0.45 + (ratio - 1.0) * 0.25)), 2)


def _error_rate_signal(current: ServiceMetrics, baseline: ServiceMetrics) -> Signal | None:
    threshold = max(0.05, baseline.error_rate * 2.0)
    if current.error_rate < threshold:
        return None
    ratio = current.error_rate / max(baseline.error_rate, 0.01)
    severity = "critical" if current.error_rate >= 0.12 or ratio >= 5 else "high"
    return Signal(
        service=current.service,
        kind="error_rate_spike",
        severity=severity,
        title="Error rate exceeded the rolling baseline",
        observed=current.error_rate,
        baseline=baseline.error_rate,
        threshold=round(threshold, 4),
        anomaly_score=_score(ratio),
        evidence=f"{current.errors} errors across {current.total} events",
        runbook_id="RB-ERROR-RATE",
    )


def _latency_signal(current: ServiceMetrics, baseline: ServiceMetrics) -> Signal | None:
    threshold = max(800.0, baseline.p95_latency_ms * 1.6)
    if current.p95_latency_ms < threshold:
        return None
    ratio = current.p95_latency_ms / max(baseline.p95_latency_ms, 1.0)
    severity = "high" if current.p95_latency_ms >= 1500 else "warning"
    return Signal(
        service=current.service,
        kind="latency_spike",
        severity=severity,
        title="P95 latency increased beyond the expected range",
        observed=current.p95_latency_ms,
        baseline=baseline.p95_latency_ms,
        threshold=round(threshold, 2),
        anomaly_score=_score(ratio),
        evidence=f"P95 latency reached {current.p95_latency_ms:.0f} ms",
        runbook_id="RB-LATENCY",
    )


def _volume_signal(current: ServiceMetrics, baseline: ServiceMetrics) -> Signal | None:
    threshold = baseline.total * 0.45
    if baseline.total < 20 or current.total >= threshold:
        return None
    drop_ratio = 1.0 - current.total / baseline.total
    return Signal(
        service=current.service,
        kind="volume_drop",
        severity="warning",
        title="Event volume dropped below the expected range",
        observed=float(current.total),
        baseline=float(baseline.total),
        threshold=round(threshold, 2),
        anomaly_score=round(min(0.95, 0.5 + drop_ratio * 0.5), 2),
        evidence=f"Only {current.total} events were observed versus {baseline.total} in baseline",
        runbook_id="RB-VOLUME",
    )


def _repeated_error_signal(records: list[LogRecord], service: str) -> Signal | None:
    error_codes = [record.error_code for record in records if record.service == service and is_error(record) and record.error_code]
    if not error_codes:
        return None
    error_code, count = Counter(error_codes).most_common(1)[0]
    if count < 8:
        return None
    return Signal(
        service=service,
        kind="repeated_error_pattern",
        severity="high" if count >= 20 else "warning",
        title=f"Repeated error pattern: {error_code}",
        observed=float(count),
        baseline=0.0,
        threshold=8.0,
        anomaly_score=round(min(0.98, 0.6 + count / 100), 2),
        evidence=f"{error_code} appeared {count} times in the analysis window",
        runbook_id="RB-ERROR-PATTERN",
    )


def detect_signals(
    current_records: list[LogRecord], baseline_records: list[LogRecord]
) -> tuple[list[ServiceMetrics], list[Signal]]:
    current_metrics = calculate_all_services(current_records)
    baseline_by_service = {
        metric.service: metric for metric in calculate_all_services(baseline_records)
    }
    signals: list[Signal] = []
    for current in current_metrics:
        baseline = baseline_by_service.get(current.service)
        if baseline is None:
            baseline = calculate_metrics([], current.service)
        for detector in (_error_rate_signal, _latency_signal, _volume_signal):
            signal = detector(current, baseline)
            if signal:
                signals.append(signal)
        repeated = _repeated_error_signal(current_records, current.service)
        if repeated:
            signals.append(repeated)

    signals.sort(
        key=lambda signal: (-SEVERITY_RANK[signal.severity], signal.service, signal.kind)
    )
    return current_metrics, signals
