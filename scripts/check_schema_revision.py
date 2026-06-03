#!/usr/bin/env python3
"""Fail if schema-related files changed without a new Alembic revision."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_PREFIX = "migrations/versions/"

SCHEMA_PATHS = (
    "api.py",
    "table_def_models/",
    "utils/schema_metadata.py",
    "utils/schema_ensure.py",
    "utils/migration_ddl.py",
)


def _changed_files(base_ref: str) -> list[str] | None:
    result = subprocess.run(
        ["git", "diff", "--name-status", base_ref, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-status", "--cached"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _normalize_path(path: str) -> str:
    if "\t" in path:
        return path.split("\t", 1)[1].replace("\\", "/")
    return path.replace("\\", "/")


def _schema_changed(entries: list[str]) -> bool:
    for entry in entries:
        path = _normalize_path(entry)
        if path == "api.py":
            return True
        for prefix in SCHEMA_PATHS:
            if prefix.endswith("/") and path.startswith(prefix):
                return True
            if path == prefix:
                return True
    return False


def _new_migration_added(entries: list[str]) -> bool:
    for entry in entries:
        parts = entry.split("\t", 1)
        if len(parts) != 2:
            continue
        status, path = parts[0].strip(), parts[1].replace("\\", "/")
        if status == "A" and path.startswith(VERSIONS_PREFIX):
            return True
    return False


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    changed = _changed_files(base_ref)
    if changed is None:
        changed = _changed_files("HEAD~1")
    if changed is None:
        print("Could not determine changed files for schema revision check.", file=sys.stderr)
        return 1
    if not changed:
        return 0

    if not _schema_changed(changed):
        return 0

    if _new_migration_added(changed):
        return 0

    print(
        "Schema-related files changed but no new file under migrations/versions/.\n"
        "Add an Alembic revision: alembic revision -m \"describe your change\"",
        file=sys.stderr,
    )
    for entry in changed:
        path = _normalize_path(entry)
        if any(path.startswith(p.rstrip("/")) or path == "api.py" for p in SCHEMA_PATHS):
            print(f"  - {path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
