#!/usr/bin/env python3
"""Report locale file integrity issues. Exit 1 if any check fails."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
LOCALES_DIR = ROOT / "locales"
LOCALES = [
    "en",
    "de",
    "ko",
    "bg",
    "cs",
    "da",
    "el",
    "es-419",
    "fi",
    "fr",
    "hi",
    "hr",
    "hu",
    "id",
    "it",
    "ja",
    "lt",
    "nl",
    "vi",
    "zh-CN",
    "zh-TW",
]

SKIP_DIRS = {".git", ".venv", ".venv2", "build", "__pycache__", "locale_keys", "locales", "scripts"}


def _load_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected JSON array")
    return [e for e in data if isinstance(e, dict)]


def _dot_identifiers(entries: list[dict]) -> set[str]:
    return {
        str(e["identifier"])
        for e in entries
        if isinstance(e.get("identifier"), str) and "." in str(e["identifier"])
    }


def _collect_code_string_keys() -> tuple[set[str], list[str]]:
    keys: set[str] = set()
    dynamic: list[str] = []

    for path in ROOT.rglob("*.py"):
        if any(s in path.parts for s in SKIP_DIRS):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id in ("raw", "LocalizedString"):
                if (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                    and "." in node.args[0].value
                ):
                    keys.add(node.args[0].value)
                elif node.args:
                    dynamic.append(f"{path.relative_to(ROOT)}:{node.lineno}")
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "localize"
                and isinstance(func.value, ast.Name)
                and func.value.id == "tanjunLocalizer"
            ):
                key_expr: ast.expr | None = None
                if len(node.args) >= 2:
                    key_expr = node.args[1]
                else:
                    for kw in node.keywords:
                        if kw.arg == "key":
                            key_expr = kw.value
                            break
                if key_expr is None:
                    continue
                if isinstance(key_expr, ast.Constant) and isinstance(key_expr.value, str):
                    if "." in key_expr.value:
                        keys.add(key_expr.value)
                else:
                    dynamic.append(f"{path.relative_to(ROOT)}:{node.lineno}")

    return keys, dynamic


def _check_registry(en_dot: set[str]) -> list[str]:
    from locale_keys._registry import LOCALE_KEYS

    reg = set(LOCALE_KEYS)
    issues: list[str] = []
    if reg != en_dot:
        only_en = sorted(en_dot - reg)[:10]
        only_reg = sorted(reg - en_dot)[:10]
        if only_en:
            issues.append(f"registry missing {len(en_dot - reg)} en keys (sample: {only_en})")
        if only_reg:
            issues.append(f"registry has {len(reg - en_dot)} keys not in en (sample: {only_reg})")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-missing", action="store_true", help="Copy missing dot-keys from en.json into other locales")
    args = parser.parse_args()

    en_path = LOCALES_DIR / "en.json"
    en_entries = _load_entries(en_path)
    en_dot = _dot_identifiers(en_entries)
    en_by_id = {str(e["identifier"]): e for e in en_entries if e.get("identifier")}

    issues: list[str] = []
    issues.extend(_check_registry(en_dot))

    for loc in LOCALES:
        path = LOCALES_DIR / f"{loc}.json"
        if not path.exists():
            issues.append(f"{loc}.json: file missing")
            continue
        try:
            entries = _load_entries(path)
        except (json.JSONDecodeError, ValueError) as exc:
            issues.append(f"{loc}.json: {exc}")
            continue
        ids = [str(e.get("identifier", "")) for e in entries if isinstance(e, dict)]
        if len(ids) != len(set(ids)):
            issues.append(f"{loc}.json: {len(ids) - len(set(ids))} duplicate identifiers")
        empty = [e for e in entries if not str(e.get("translation", "")).strip()]
        if empty and loc == "en":
            issues.append(f"{loc}.json: {len(empty)} entries with empty translation")

        if loc != "en":
            loc_dot = _dot_identifiers(entries)
            missing = sorted(en_dot - loc_dot)
            if missing and args.sync_missing:
                added = 0
                for key in missing:
                    if key in en_by_id:
                        entries.append(dict(en_by_id[key]))
                        added += 1
                path.write_text(
                    json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                print(f"Synced {added} keys into {loc}.json", file=sys.stderr)
                loc_dot = _dot_identifiers(entries)
                missing = sorted(en_dot - loc_dot)
            if missing:
                issues.append(f"{loc}.json: missing {len(missing)} dot-keys vs en.json")
                for key in missing[:5]:
                    issues.append(f"  - {key}")
                if len(missing) > 5:
                    issues.append(f"  ... and {len(missing) - 5} more")

    code_keys, dynamic = _collect_code_string_keys()
    missing_in_en = sorted(k for k in code_keys if k not in en_dot)
    if missing_in_en:
        issues.append(f"code references {len(missing_in_en)} dot-keys not in en.json (sample: {missing_in_en[:5]})")
    if dynamic:
        print(
            f"Note: {len(dynamic)} dynamic localize/LocalizedString calls (not statically verified)",
            file=sys.stderr,
        )

    if issues:
        print("Locale check FAILED:", file=sys.stderr)
        for line in issues:
            print(line, file=sys.stderr)
        return 1

    print("Locale check OK: all locale files match en.json dot-keys, registry aligned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
