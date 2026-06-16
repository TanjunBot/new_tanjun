#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.helpers.command_coverage.gate import check_thresholds
from tests.helpers.command_coverage.models import LayerKind
from tests.helpers.command_coverage.report import build_coverage_report
from tests.helpers.command_coverage.reporter import (
    format_html_report,
    format_json_report,
    format_text_report,
    write_report,
)


def _parse_layer(value: str | None) -> LayerKind | None:
    if not value:
        return None
    return LayerKind(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report command test coverage matrix")
    parser.add_argument("--all", action="store_true", help="Report all command groups")
    parser.add_argument("--group", help="Filter to a root group (e.g. funcmd_name)")
    parser.add_argument("--path", help="Filter to a single manifest tree path")
    parser.add_argument("--layer", help="Filter to a test layer")
    parser.add_argument("--verbose", action="store_true", help="Show full missing cell list")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text")
    parser.add_argument("--output", type=Path, help="Write report to file")
    parser.add_argument(
        "--fail-under-config",
        type=Path,
        default=ROOT / "coverage" / "thresholds.yaml",
        help="YAML thresholds config; exit 1 on violation",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Report thresholds but do not exit 1 on violation",
    )
    args = parser.parse_args(argv)

    if not args.all and not args.group and not args.path:
        args.all = True

    display_report = build_coverage_report(
        filter_group=args.group,
        filter_path=args.path,
        filter_layer=_parse_layer(args.layer),
    )
    gate_report = (
        display_report
        if args.all and not args.group and not args.path and not args.layer
        else build_coverage_report()
    )

    if args.format == "json":
        output = format_json_report(display_report)
    elif args.format == "html":
        output = format_html_report(display_report)
    else:
        output = format_text_report(display_report, verbose=args.verbose)

    if args.output:
        write_report(display_report, args.output, args.format)
    print(output)

    if args.no_fail:
        return 0

    violations = check_thresholds(gate_report, args.fail_under_config)
    if violations:
        print("\nThreshold violations:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation.check_id}: {violation.message}", file=sys.stderr)
        return 1
    if not args.no_fail:
        print("All coverage thresholds met.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
