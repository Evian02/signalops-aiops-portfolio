import pytest

from signalops.parser import LogParseError, parse_json_lines


def test_parse_valid_record():
    records = parse_json_lines(
        ['{"timestamp":"2026-08-20T09:00:00Z","service":"api","level":"INFO","message":"ok","status_code":200,"latency_ms":42}']
    )
    assert records[0].service == "api"
    assert records[0].latency_ms == 42.0


def test_rejects_invalid_json():
    with pytest.raises(LogParseError, match="invalid JSON"):
        parse_json_lines(["not-json"])
