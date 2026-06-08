#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "coverage" / "command_handlers.json"
sys.path.insert(0, str(ROOT))

from diagnostics.registry import all_specs
from tests.helpers.command_matrix.resolver import (
    _awaited_call_name,
    _import_alias_map,
    _resolve_from_commands_leaf,
    _resolve_from_extension_spec,
)
from diagnostics.discovery import _instantiate_group

MANUAL_HANDLERS: dict[str, str] = {
    "ai_name ai_askcustom_name": "tests.helpers.command_matrix.manual_handlers.ask_custom_situation",
    "setup_name setup_logs_name": "tests.helpers.command_matrix.manual_handlers.setup_logs_wizard",
    "setup_name setup_level_name": "tests.helpers.command_matrix.manual_handlers.setup_level_wizard",
    "setup_name setup_giveaway_name": "tests.helpers.command_matrix.manual_handlers.setup_giveaway_wizard",
    "setup_name setup_booster_name": "tests.helpers.command_matrix.manual_handlers.setup_booster_wizard",
    "utilitycmd_name utility_boosterchannel_name utility_boosterchannelinfo_name": "tests.helpers.command_matrix.manual_handlers.booster_channel_info",
    "utilitycmd_name utility_boosterrole_name utility_boosterroleinfo_name": "tests.helpers.command_matrix.manual_handlers.booster_role_info",
    "utilitycmd_name utility_feedback_name": "tests.helpers.command_matrix.manual_handlers.feedback_command",
}


def main() -> None:
    by_spec: dict[str, str] = {}
    by_path: dict[str, str] = {}
    path_meta: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    for spec in all_specs():
        if not spec.tree_path or spec.skip_reason:
            continue
        handler = _resolve_from_extension_spec(spec)
        if handler is None:
            handler = _resolve_from_commands_leaf(spec.tree_path)
        if handler is None:
            manual = MANUAL_HANDLERS.get(spec.tree_path)
            if manual:
                from tests.helpers.command_matrix.resolver import _load_callable

                handler = _load_callable(manual)
        if handler is None:
            missing.append(spec.tree_path)
            continue
        path = f"{handler.__module__}.{handler.__qualname__.split('.')[-1]}"
        by_spec[spec.id] = path
        by_path[spec.tree_path] = path
        patch_target = path
        group = _instantiate_group(spec.group_cls)
        if group is not None:
            method = getattr(group, spec.method_name, None)
            if method is not None:
                callback = getattr(method, "callback", method)
                alias = _awaited_call_name(callback)
                if alias:
                    base = alias.split(".", 1)[0]
                    patch_target = f"{spec.extension}.{base}"
        path_meta[spec.tree_path] = {
            "extension": spec.extension,
            "group_cls": f"{spec.group_cls.__module__}.{spec.group_cls.__name__}",
            "method": spec.method_name,
            "handler": path,
            "patch_target": patch_target,
        }
    payload = {"by_spec": by_spec, "by_path": by_path, "path_meta": path_meta}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {len(by_path)} handlers to {OUT}")
    if missing:
        print(f"Missing handlers for {len(missing)} paths (first 5): {missing[:5]}")


if __name__ == "__main__":
    main()
