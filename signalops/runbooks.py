RUNBOOKS: dict[str, list[str]] = {
    "error_rate_spike": [
        "Group recent error messages and trace IDs to identify the dominant failure pattern.",
        "Compare the incident window with recent releases or configuration changes.",
        "Check upstream dependency health before deciding whether to retry, isolate, or roll back.",
    ],
    "latency_spike": [
        "Compare endpoint latency and request volume with the baseline window.",
        "Inspect slow upstream dependencies, timeouts, and resource saturation indicators.",
        "Validate whether the issue is isolated to one service or propagating across dependencies.",
    ],
    "repeated_error_pattern": [
        "Filter logs by the dominant error code and inspect representative trace IDs.",
        "Reproduce the failing request with the smallest known input.",
        "Document the trigger condition and add a regression test after resolution.",
    ],
    "volume_drop": [
        "Verify log ingestion, routing, and service health before treating the drop as real traffic change.",
        "Compare request volume across adjacent services and time windows.",
        "Escalate if the drop coincides with elevated errors or missing heartbeat events.",
    ],
}


def actions_for(signal_kinds: list[str]) -> list[str]:
    actions: list[str] = []
    for kind in signal_kinds:
        for action in RUNBOOKS.get(kind, []):
            if action not in actions:
                actions.append(action)
    return actions[:4]
