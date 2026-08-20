from __future__ import annotations

import argparse
import json

from .pipeline import analyze_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signalops", description="Analyze structured service logs and open explainable incidents."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="analyze a JSONL log window")
    analyze.add_argument("--input", required=True, help="current JSONL log file")
    analyze.add_argument("--baseline", required=True, help="baseline JSONL log file")
    analyze.add_argument("--output", required=True, help="destination report JSON file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        report = analyze_files(args.input, args.baseline, args.output)
        print(json.dumps(report["summary"], indent=2))
        return 0
    return 1
