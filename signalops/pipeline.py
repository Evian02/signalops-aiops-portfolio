from __future__ import annotations

import json
from pathlib import Path

from .detector import detect_signals
from .incidents import build_incidents
from .metrics import build_timeline, is_error
from .models import AnalysisReport
from .parser import load_jsonl


def analyze_files(
    input_path: str | Path,
    baseline_path: str | Path,
    output_path: str | Path | None = None,
) -> dict[str, object]:
    current = load_jsonl(input_path)
    baseline = load_jsonl(baseline_path)
    services, signals = detect_signals(current, baseline)
    incidents = build_incidents(signals)
    total_errors = sum(is_error(record) for record in current)
    report = AnalysisReport(
        generated_at=max(record.timestamp for record in current).isoformat(),
        source=Path(input_path).name,
        baseline_source=Path(baseline_path).name,
        total_logs=len(current),
        total_errors=total_errors,
        overall_error_rate=round(total_errors / len(current), 4),
        services=services,
        signals=signals,
        incidents=incidents,
        timeline=build_timeline(current),
    ).to_dict()
    if output_path is not None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return report
