from __future__ import annotations

import html
import json
from pathlib import Path

from tests.helpers.command_coverage.models import CoverageReport


def _format_missing_sample(report_group, layer_summary, verbose: bool) -> str:
    if not layer_summary.missing:
        return ""
    items = layer_summary.missing if verbose else layer_summary.missing[:3]
    parts = []
    for cell in items:
        dims = ",".join(f"{k}={v}" for k, v in sorted(cell.dimensions.items()))
        leaf = cell.tree_path.rsplit(" ", 1)[-1]
        parts.append(f"{leaf}({dims})" if dims else leaf)
    suffix = ""
    if not verbose and len(layer_summary.missing) > 3:
        suffix = f", +{len(layer_summary.missing) - 3} more"
    return ", ".join(parts) + suffix


def format_text_report(report: CoverageReport, *, verbose: bool = False) -> str:
    lines: list[str] = []
    lines.append("Command test coverage matrix")
    lines.append(
        f"Manifest paths with any test: {report.paths_with_any_test}/{report.total_manifest_paths}"
    )
    below_90 = [cmd for cmd in report.commands if cmd.percent < 90]
    if below_90:
        lines.append(f"Commands below 90%: {len(below_90)}")
    lines.append("")

    for group in report.groups:
        lines.append(f"Command coverage — {group.root_group} ({len(group.tree_paths)} commands)")
        lines.append("─" * 72)
        lines.append(f"{'Layer':<18} {'Expected':>8} {'Covered':>8} {'%':>6}  Missing (sample)")
        for layer in group.layers:
            sample = _format_missing_sample(group, layer, verbose)
            lines.append(
                f"{layer.layer.value:<18} {layer.expected:>8} {layer.covered:>8} "
                f"{layer.percent:>5.0f}%  {sample}"
            )
        if group.permission_denial_expected:
            lines.append(
                f"{'permission_denial':<18} {group.permission_denial_expected:>8} "
                f"{group.permission_denial_covered:>8} {group.permission_denial_percent:>5.0f}%  "
                f"{', '.join(group.permission_denial_missing[:5])}"
            )
        lines.append("")

    if verbose:
        lines.append("Missing cells (full):")
        for group in report.groups:
            for layer in group.layers:
                for cell in layer.missing:
                    dims = ",".join(f"{k}={v}" for k, v in sorted(cell.dimensions.items()))
                    lines.append(f"  {group.root_group} {layer.layer.value} {cell.tree_path} [{dims}]")

    return "\n".join(lines)


def format_json_report(report: CoverageReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_html_report(report: CoverageReport) -> str:
    rows: list[str] = []
    for group in report.groups:
        for layer in group.layers:
            color = "#2d6a4f" if layer.percent >= 100 else "#bc6c25" if layer.percent >= 60 else "#9b2226"
            rows.append(
                "<tr>"
                f"<td>{html.escape(group.root_group)}</td>"
                f"<td>{html.escape(layer.layer.value)}</td>"
                f"<td>{layer.expected}</td>"
                f"<td>{layer.covered}</td>"
                f"<td style='color:{color}'>{layer.percent:.0f}%</td>"
                "</tr>"
            )
    body = "\n".join(rows)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Command Coverage</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
th {{ background: #f4f4f4; }}
</style></head><body>
<h1>Command test coverage matrix</h1>
<p>Paths with any test: {report.paths_with_any_test}/{report.total_manifest_paths}</p>
<table>
<thead><tr><th>Group</th><th>Layer</th><th>Expected</th><th>Covered</th><th>%</th></tr></thead>
<tbody>{body}</tbody>
</table>
</body></html>"""


def write_report(report: CoverageReport, path: Path, fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(format_json_report(report), encoding="utf-8")
    elif fmt == "html":
        path.write_text(format_html_report(report), encoding="utf-8")
    else:
        path.write_text(format_text_report(report), encoding="utf-8")
