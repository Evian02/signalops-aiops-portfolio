from datetime import datetime, timedelta, timezone

from signalops.detector import detect_signals
from signalops.models import LogRecord


def record(index: int, *, error: bool, latency: float) -> LogRecord:
    return LogRecord(
        timestamp=datetime(2026, 8, 20, tzinfo=timezone.utc) + timedelta(seconds=index),
        service="checkout-api",
        level="ERROR" if error else "INFO",
        message="request",
        status_code=503 if error else 200,
        latency_ms=latency,
        error_code="UPSTREAM_TIMEOUT" if error else "",
    )


def test_detects_error_latency_and_repeated_pattern():
    baseline = [record(i, error=i == 0, latency=180) for i in range(100)]
    current = [record(i, error=i < 20, latency=1800 if i < 30 else 250) for i in range(100)]
    _, signals = detect_signals(current, baseline)
    kinds = {signal.kind for signal in signals}
    assert "error_rate_spike" in kinds
    assert "latency_spike" in kinds
    assert "repeated_error_pattern" in kinds
