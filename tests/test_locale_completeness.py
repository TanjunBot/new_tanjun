from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from health.checks.locales import LocaleFileHealthCheck
from locale_keys._registry import LOCALE_KEYS

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
LOCALES = LocaleFileHealthCheck.LOCALES
SKIP_DIRS = {".git", ".venv", ".venv2", "build", "__pycache__", "locale_keys", "locales", "scripts"}


def _load_identifiers(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(entry["identifier"])
        for entry in data
        if isinstance(entry, dict) and isinstance(entry.get("identifier"), str)
    }


def _load_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return [e for e in data if isinstance(e, dict)]


def test_en_dot_keys_in_registry() -> None:
    en_ids = {k for k in _load_identifiers(LOCALES_DIR / "en.json") if "." in k}
    assert en_ids == set(LOCALE_KEYS)


def test_no_duplicate_identifiers_per_locale() -> None:
    for locale in LOCALES:
        path = LOCALES_DIR / f"{locale}.json"
        if not path.exists():
            pytest.skip(f"missing {path}")
        ids = [str(e["identifier"]) for e in _load_entries(path) if e.get("identifier")]
        assert len(ids) == len(set(ids)), f"duplicate identifiers in {locale}.json"


def test_en_translations_non_empty() -> None:
    for entry in _load_entries(LOCALES_DIR / "en.json"):
        ident = entry.get("identifier")
        if not isinstance(ident, str) or "." not in ident:
            continue
        trans = str(entry.get("translation", "")).strip()
        assert trans, f"empty translation for {ident!r}"


@pytest.mark.parametrize("locale", LOCALES)
def test_all_en_dot_keys_present(locale: str) -> None:
    en_path = LOCALES_DIR / "en.json"
    loc_path = LOCALES_DIR / f"{locale}.json"
    if not loc_path.exists():
        pytest.skip(f"missing {loc_path}")
    en_dot = {k for k in _load_identifiers(en_path) if "." in k}
    loc_ids = _load_identifiers(loc_path)
    missing = sorted(en_dot - loc_ids)
    assert not missing, f"{locale}.json missing {len(missing)} keys: {missing[:10]}"


def _collect_static_code_keys() -> set[str]:
    keys: set[str] = set()
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
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "localize"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "tanjunLocalizer"
            ):
                key_expr: ast.expr | None = None
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    key_expr = node.args[1]
                else:
                    for kw in node.keywords:
                        if kw.arg == "key" and isinstance(kw.value, ast.Constant):
                            key_expr = kw.value
                            break
                if (
                    key_expr is not None
                    and isinstance(key_expr.value, str)
                    and "." in key_expr.value
                ):
                    keys.add(key_expr.value)
    return keys


def test_static_code_keys_exist_in_en_json() -> None:
    en_dot = {k for k in _load_identifiers(LOCALES_DIR / "en.json") if "." in k}
    code_keys = _collect_static_code_keys()
    missing = sorted(code_keys - en_dot)
    assert not missing, f"static code keys missing from en.json: {missing[:15]}"


def test_all_locale_keys_resolve_in_en() -> None:
    from locale_keys._registry import PLACEHOLDERS
    from locale_keys.types import LocalizedString

    for key in LOCALE_KEYS:
        placeholders = PLACEHOLDERS.get(key, ())
        kwargs = {p: str(p) for p in placeholders}
        result = LocalizedString(key)("en", **kwargs)
        assert result, f"empty result for {key!r}"
        assert "err: no translation found" not in result, f"missing en translation for {key!r}"


def test_locale_accessor_smoke() -> None:
    from locale_keys import locale

    title = locale.commands.channel.dynamicslowmode.missingPermission.title("en")
    assert title
    assert "err: no translation found" not in title


def test_check_locales_script() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_locales.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_health_locale_check_passes() -> None:
    import asyncio

    from health.checks.locales import HealthStatus, LocaleFileHealthCheck

    outcome = asyncio.run(LocaleFileHealthCheck().run())
    assert outcome.status == HealthStatus.HEALTHY, outcome.message
