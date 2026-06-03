#!/usr/bin/env python3
"""Regenerate migrations/snapshot_001.py from current TableDef (run when 001 must stay frozen)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import get_table_definitions  # noqa: E402
from utils.migration_ddl import ordered_table_names  # noqa: E402

OUTPUT = ROOT / "migrations" / "snapshot_001.py"


def main() -> int:
    tables = get_table_definitions()
    order = ordered_table_names(set(tables))
    lines = [
        '"""Frozen DDL for revision 001_initial_schema (do not edit; regenerate via scripts/generate_initial_schema_snapshot.py)."""',
        "",
        "from __future__ import annotations",
        "",
        "CREATE_ORDER: list[str] = [",
    ]
    for name in order:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")
    lines.append("TABLE_DDL: dict[str, str] = {")
    for name in order:
        ddl = tables[name].replace('"""', '\\"\\"\\"')
        lines.append(f'    "{name}": """{ddl}""",')
    lines.append("}")
    lines.append("")
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(order)} tables)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
