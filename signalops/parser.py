from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import LogRecord


class LogParseError(ValueError):
    """Raised when a structured log line cannot be validated."""


def _parse_timestamp(raw: object, line_number: int) -> datetime:
    if not isinstance(raw, str):
        raise LogParseError(f"line {line_number}: timestamp must be a string")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LogParseError(f"line {line_number}: invalid ISO-8601 timestamp") from exc


def parse_json_lines(lines: Iterable[str]) -> list[LogRecord]:
    records: list[LogRecord] = []
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LogParseError(f"line {line_number}: invalid JSON") from exc
        if not isinstance(item, dict):
            raise LogParseError(f"line {line_number}: log entry must be an object")

        service = item.get("service")
        level = item.get("level")
        message = item.get("message")
        if not isinstance(service, str) or not service.strip():
            raise LogParseError(f"line {line_number}: service is required")
        if not isinstance(level, str) or not level.strip():
            raise LogParseError(f"line {line_number}: level is required")
        if not isinstance(message, str):
            raise LogParseError(f"line {line_number}: message must be a string")

        status_code = item.get("status_code")
        latency_ms = item.get("latency_ms")
        if status_code is not None and not isinstance(status_code, int):
            raise LogParseError(f"line {line_number}: status_code must be an integer")
        if latency_ms is not None and not isinstance(latency_ms, (int, float)):
            raise LogParseError(f"line {line_number}: latency_ms must be numeric")

        records.append(
            LogRecord(
                timestamp=_parse_timestamp(item.get("timestamp"), line_number),
                service=service.strip(),
                level=level.upper().strip(),
                message=message.strip(),
                status_code=status_code,
                latency_ms=float(latency_ms) if latency_ms is not None else None,
                trace_id=str(item.get("trace_id", "")),
                error_code=str(item.get("error_code", "")),
            )
        )
    if not records:
        raise LogParseError("no log records found")
    return sorted(records, key=lambda record: record.timestamp)


def load_jsonl(path: str | Path) -> list[LogRecord]:
    log_path = Path(path)
    with log_path.open("r", encoding="utf-8") as handle:
        return parse_json_lines(handle)
