from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LogRecord:
    timestamp: datetime
    service: str
    level: str
    message: str
    status_code: int | None = None
    latency_ms: float | None = None
    trace_id: str = ""
    error_code: str = ""


@dataclass(frozen=True)
class ServiceMetrics:
    service: str
    total: int
    errors: int
    warnings: int
    error_rate: float
    p95_latency_ms: float
    average_latency_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Signal:
    service: str
    kind: str
    severity: str
    title: str
    observed: float
    baseline: float
    threshold: float
    anomaly_score: float
    evidence: str
    runbook_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Incident:
    incident_id: str
    service: str
    severity: str
    title: str
    summary: str
    signal_kinds: list[str]
    recommended_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisReport:
    generated_at: str
    source: str
    baseline_source: str
    total_logs: int
    total_errors: int
    overall_error_rate: float
    services: list[ServiceMetrics] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    incidents: list[Incident] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "meta": {
                "project": "SignalOps",
                "engine_version": "1.0.0",
                "generated_at": self.generated_at,
                "detection_mode": "rule-based statistical baseline",
                "source": self.source,
                "baseline_source": self.baseline_source,
            },
            "summary": {
                "total_logs": self.total_logs,
                "total_errors": self.total_errors,
                "overall_error_rate": self.overall_error_rate,
                "services_monitored": len(self.services),
                "signals_detected": len(self.signals),
                "incidents_opened": len(self.incidents),
                "critical_incidents": sum(
                    incident.severity == "critical" for incident in self.incidents
                ),
            },
            "services": [service.to_dict() for service in self.services],
            "signals": [signal.to_dict() for signal in self.signals],
            "incidents": [incident.to_dict() for incident in self.incidents],
            "timeline": self.timeline,
        }
