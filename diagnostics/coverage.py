from __future__ import annotations

from typing import Any

from diagnostics.models import CheckOutcome
from diagnostics.registry import all_specs
from diagnostics.tree import load_manifest


def check_manifest_spec_coverage() -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    manifest = load_manifest()
    expected_paths = set(manifest.get("paths") or [])
    if not expected_paths:
        outcomes.append(CheckOutcome("coverage.manifest", True, "No manifest paths to verify"))
        return outcomes

    specs = all_specs()
    by_path: dict[str, list[Any]] = {}
    for spec in specs:
        if spec.tree_path:
            by_path.setdefault(spec.tree_path, []).append(spec)

    missing: list[str] = []
    skip_only: list[str] = []
    for path in sorted(expected_paths):
        matched = by_path.get(path, [])
        if not matched:
            missing.append(path)
            continue
        if all(s.skip_reason for s in matched):
            skip_only.append(path)

    for path in missing:
        outcomes.append(CheckOutcome(f"coverage.missing_spec.{path}", False, "No behavior spec for manifest path"))
    for path in skip_only:
        outcomes.append(
            CheckOutcome(
                f"coverage.skipped_only.{path}",
                False,
                "Manifest path only has skipped specs (must be runnable or allowlisted)",
            )
        )

    if not missing and not skip_only:
        outcomes.append(
            CheckOutcome(
                "coverage.manifest",
                True,
                f"All {len(expected_paths)} manifest paths have runnable behavior specs",
            )
        )

    return outcomes


def check_duplicate_spec_ids() -> list[CheckOutcome]:
    specs = all_specs()
    seen: dict[str, int] = {}
    for spec in specs:
        seen[spec.id] = seen.get(spec.id, 0) + 1
    outcomes: list[CheckOutcome] = []
    for spec_id, count in sorted(seen.items()):
        if count > 1:
            outcomes.append(CheckOutcome(f"coverage.duplicate.{spec_id}", False, f"Duplicate spec id ({count}x)"))
    if not outcomes:
        outcomes.append(CheckOutcome("coverage.duplicate_ids", True, f"No duplicates among {len(specs)} specs"))
    return outcomes
