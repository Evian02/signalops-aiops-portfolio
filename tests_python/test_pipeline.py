from pathlib import Path

from signalops.pipeline import analyze_files


ROOT = Path(__file__).resolve().parents[1]


def test_sample_pipeline_opens_explainable_incident(tmp_path):
    report = analyze_files(
        ROOT / "data" / "sample_logs.jsonl",
        ROOT / "data" / "baseline_logs.jsonl",
        tmp_path / "report.json",
    )
    assert report["summary"]["total_logs"] == 900
    assert report["summary"]["incidents_opened"] >= 1
    incident = report["incidents"][0]
    assert incident["service"] == "checkout-api"
    assert incident["recommended_actions"]
