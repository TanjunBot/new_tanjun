#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.classify_command_axes import classify_group
from tests.helpers.command_coverage.inventory import detect_permission_checks_for_paths
MANIFEST = ROOT / "diagnostics" / "manifest.json"
OUT = ROOT / "coverage" / "overrides.yaml"

PERMISSION_FULL = ["admin", "member", "restricted", "no_guild", "channel_deny_send", "channel_deny_embed"]
PERMISSION_BASIC = ["admin", "restricted"]
LOCALES = ["en-US", "de", "fr"]

ADMIN_GROUPS = {f"admin_{s}_name" for s in [
    "channels", "emoji", "jointocreate", "localegroup", "messaging", "moderation",
    "purgegroup", "report", "role", "rolemanage", "setup", "triggermessages", "warn",
]}

PERMISSION_GROUPS = ADMIN_GROUPS | {
    "ai_name", "channel_name", "giveaway_name", "level_blacklist_name",
    "level_boosts_name", "level_config_name", "logs_name", "minigame_name",
}


def paths_for(root: str, paths: list[str]) -> list[str]:
    return [p for p in paths if p.startswith(root + " ") or p == root]


E2E_MESSAGE_KINDS = ["none", "short", "unicode", "max"]
E2E_TARGETS = ["self", "bot"]


def standard_layers(*, e2e_permission: list[str] | None = None) -> dict:
    e2e_permission = e2e_permission or ["admin"]
    return {
        "unit_logic": [{"axes": ["permission"], "per_path": True}],
        "integration": [{"axes": ["permission"], "per_path": True, "overrides": {"permission": ["admin"]}}],
        "behavior_spec": [{"axes": [], "per_path": True}],
        "e2e_live": [
            {
                "axes": ["permission", "target"],
                "per_path": True,
                "overrides": {"permission": e2e_permission, "target": E2E_TARGETS},
            }
        ],
    }


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "bootstrap_command_handlers.py")], check=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths: list[str] = manifest["paths"]
    roots: list[str] = manifest["roots"]
    permission_paths = detect_permission_checks_for_paths()
    groups: dict = {}

    groups["funcmd_name"] = {
        "path_template": "funcmd_name fun_{action}_name",
        "dimensions": {
            "action": ["hug", "kiss", "boop", "wave", "slap", "laugh", "tickle", "pat", "poke"],
            "message_kind": ["none", "empty", "short", "unicode", "max", "multiline"],
            "permission": PERMISSION_FULL,
            "locale": LOCALES,
            "target": ["self", "bot"],
            "gif": ["gif", "no-gif"],
        },
        "layers": {
            "unit_logic": [
                {"axes": ["action", "message_kind", "permission"], "defaults": {"gif": "gif"}},
                {"axes": ["action", "locale"], "defaults": {"message_kind": "short", "permission": "admin", "gif": "gif"}},
                {"axes": ["action"], "defaults": {"message_kind": "none", "permission": "admin", "gif": "no-gif"}},
            ],
            "integration": [{"axes": ["action"]}],
            "behavior_spec": [{"axes": ["action"]}],
            "e2e_live": [
                {
                    "axes": ["action", "message_kind", "target"],
                    "overrides": {"message_kind": ["none", "short", "unicode", "max"]},
                }
            ],
            "unit_extension": [{"axes": ["action"]}],
        },
    }

    groups["math_name"] = {
        "path_template": "math_name math_{command}_name",
        "dimensions": {
            "command": ["calc", "calculator", "faculty", "num2word", "plotfunction", "randomnumber"],
            "permission": PERMISSION_BASIC,
            "expression": ["valid", "invalid"],
        },
        "layers": {
            "unit_logic": [{"axes": ["command", "permission", "expression"]}],
            "integration": [{"axes": ["command"]}],
            "behavior_spec": [{"axes": ["command"]}],
            "e2e_live": [
                {
                    "axes": ["command", "permission", "expression"],
                    "overrides": {"permission": ["admin", "restricted"], "expression": ["valid", "invalid"]},
                }
            ],
        },
    }

    groups["utility_help_name"] = {
        "tree_paths": paths_for("utility_help_name", paths),
        "dimensions": {"locale": LOCALES},
        "per_path": True,
        "layers": {
            "unit_logic": [{"axes": ["locale"], "per_path": True}],
            "integration": [{"axes": [], "per_path": True}],
            "behavior_spec": [{"axes": [], "per_path": True}],
            "e2e_live": [{"axes": ["locale"], "per_path": True, "overrides": {"locale": ["en-US"]}}],
        },
    }

    groups["utilitycmd_name"] = {
        "tree_paths": paths_for("utilitycmd_name", paths),
        "dimensions": {"permission": PERMISSION_BASIC, "target": ["self", "bot"]},
        "per_path": True,
        "layers": {
            "unit_logic": [{"axes": ["permission", "target"], "per_path": True}],
            "integration": [{"axes": ["permission"], "per_path": True, "overrides": {"permission": ["admin"]}}],
            "behavior_spec": [{"axes": [], "per_path": True}],
            "e2e_live": [
                {
                    "axes": ["permission", "target", "message_kind"],
                    "per_path": True,
                    "overrides": {
                        "permission": ["admin"],
                        "target": E2E_TARGETS,
                        "message_kind": E2E_MESSAGE_KINDS,
                    },
                }
            ],
        },
    }

    groups["utility_scheduledmessage_name"] = {
        "tree_paths": paths_for("utility_scheduledmessage_name", paths),
        "dimensions": {"permission": PERMISSION_BASIC},
        "per_path": True,
        "layers": standard_layers(),
    }

    groups["games_name"] = {
        "path_template": "games_name games_{command}_name",
        "dimensions": {
            "command": [
                "advanced_ttt", "akinator", "battleship", "connect4", "flagquiz",
                "hangman", "memory", "rps", "ttt", "wordle",
            ],
            "permission": PERMISSION_BASIC,
        },
        "layers": {
            "unit_logic": [{"axes": ["command", "permission"]}],
            "integration": [{"axes": ["command"]}],
            "behavior_spec": [{"axes": ["command"]}],
            "e2e_live": [
                {
                    "axes": ["command", "permission"],
                    "overrides": {"permission": ["admin", "restricted"]},
                }
            ],
        },
    }

    groups["ai_name"] = {
        "tree_paths": paths_for("ai_name", paths),
        "dimensions": {"permission": PERMISSION_BASIC, "prompt_kind": ["short", "empty"]},
        "per_path": True,
        "layers": {
            "unit_logic": [{"axes": ["permission", "prompt_kind"], "per_path": True}],
            "integration": [{"axes": ["permission"], "per_path": True, "overrides": {"permission": ["admin"]}}],
            "behavior_spec": [{"axes": [], "per_path": True}],
            "e2e_live": [
                {
                    "axes": ["permission", "prompt_kind"],
                    "per_path": True,
                    "overrides": {"permission": ["admin", "restricted"], "prompt_kind": ["short", "empty"]},
                }
            ],
        },
    }

    groups["image_name"] = {
        "path_template": "image_name image_{command}_name",
        "dimensions": {
            "command": [
                "background", "blur", "compress", "contour", "detail", "edgeenhance",
                "emboss", "findedges", "mirror", "rescale", "resize", "sharpen", "smooth",
            ],
            "permission": PERMISSION_BASIC,
            "attachment": ["present"],
        },
        "layers": {
            "unit_logic": [{"axes": ["command", "permission", "attachment"]}],
            "integration": [{"axes": ["command"]}],
            "behavior_spec": [{"axes": ["command"]}],
            "e2e_live": [
                {
                    "axes": ["command", "attachment", "permission"],
                    "overrides": {"permission": ["admin", "restricted"], "attachment": ["present"]},
                }
            ],
        },
    }

    groups["setup_name"] = {
        "path_template": "setup_name setup_{wizard}_name",
        "dimensions": {"wizard": ["booster", "giveaway", "level", "logs"], "permission": PERMISSION_BASIC},
        "layers": {
            "unit_logic": [{"axes": ["wizard", "permission"]}],
            "integration": [{"axes": ["wizard"]}],
            "behavior_spec": [{"axes": ["wizard"]}],
            "e2e_live": [{"axes": ["wizard", "permission"], "overrides": {"permission": ["admin", "restricted"]}}],
        },
    }

    for root in roots:
        if root in groups:
            continue
        group_paths = paths_for(root, paths)
        groups[root] = classify_group(root, group_paths, permission_paths)

    ai_nested = [p for p in paths if "ai_customsituations_name" in p]
    if ai_nested:
        groups["ai_name"]["tree_paths_extra"] = ai_nested

    for root in ["level_blacklist_name", "level_boosts_name", "level_config_name", "levelcommands_name"]:
        groups[root]["dimensions"]["permission"] = PERMISSION_FULL

    OUT.write_text(
        yaml.safe_dump({"groups": groups}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(groups)} groups")


if __name__ == "__main__":
    main()
