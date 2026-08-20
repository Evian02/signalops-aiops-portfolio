from __future__ import annotations

from collections import defaultdict

from .detector import SEVERITY_RANK
from .models import Incident, Signal
from .runbooks import actions_for


def build_incidents(signals: list[Signal]) -> list[Incident]:
    by_service: dict[str, list[Signal]] = defaultdict(list)
    for signal in signals:
        by_service[signal.service].append(signal)

    ordered_services = sorted(
        by_service,
        key=lambda service: (
            -max(SEVERITY_RANK[signal.severity] for signal in by_service[service]),
            service,
        ),
    )
    incidents: list[Incident] = []
    for index, service in enumerate(ordered_services, start=1):
        service_signals = by_service[service]
        primary = max(service_signals, key=lambda signal: SEVERITY_RANK[signal.severity])
        kinds = [signal.kind for signal in service_signals]
        incidents.append(
            Incident(
                incident_id=f"INC-{index:03d}",
                service=service,
                severity=primary.severity,
                title=primary.title,
                summary="; ".join(signal.evidence for signal in service_signals),
                signal_kinds=kinds,
                recommended_actions=actions_for(kinds),
            )
        )
    return incidents
