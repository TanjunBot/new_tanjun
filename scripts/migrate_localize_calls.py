#!/usr/bin/env python3

from __future__ import annotations

from locale_keys import locale

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent



def _parse_path(key: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    for char in key:
        if char == '"':
            in_quote = not in_quote
            current.append(char)
        elif char == "." and not in_quote:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return parts


def _path_to_expr(parts: list[str]) -> ast.expr:
    expr: ast.expr = ast.Name(id="locale", ctx=ast.Load())
    for part in parts:
        if part.isidentifier():
            expr = ast.Attribute(value=expr, attr=part, ctx=ast.Load())
        else:
            expr = ast.Subscript(
                value=expr,
                slice=ast.Constant(value=part),
                ctx=ast.Load(),
            )
    return expr


def _underscore_to_parts(key: str) -> list[str]:
    return key.replace("_", ".").split(".")


def _extract_localize_dynamic(node: ast.Call) -> tuple[ast.expr, ast.expr, list[ast.keyword]] | None:
    locale_expr: ast.expr | None = None
    key_expr: ast.expr | None = None
    extra_keywords: list[ast.keyword] = []

    if not (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "localize"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "tanjunLocalizer"
    ):
        return None

    if len(node.args) >= 2:
        locale_expr = node.args[0]
        key_expr = node.args[1]
        extra_keywords = list(node.keywords)
    else:
        for kw in node.keywords:
            if kw.arg == "locale":
                locale_expr = kw.value
            elif kw.arg == "key":
                key_expr = kw.value
            elif kw.arg:
                extra_keywords.append(kw)
        if locale_expr is None and node.args:
            locale_expr = node.args[0]

    if locale_expr is None or key_expr is None:
        return None
    if isinstance(key_expr, ast.Constant) and isinstance(key_expr.value, str):
        return None
    return locale_expr, key_expr, extra_keywords


def _extract_localize_key(node: ast.Call) -> tuple[ast.expr, str] | None:
    locale_expr: ast.expr | None = None
    key: str | None = None
    extra_keywords: list[ast.keyword] = []

    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "localize"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "tanjunLocalizer"
    ):
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
            locale_expr = node.args[0]
            key = node.args[1].value
            extra_keywords = list(node.keywords)
        else:
            for kw in node.keywords:
                if kw.arg == "locale":
                    locale_expr = kw.value
                elif kw.arg == "key" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    key = kw.value.value
                elif kw.arg:
                    extra_keywords.append(kw)
            if locale_expr is None and len(node.args) >= 1:
                locale_expr = node.args[0]

    if locale_expr is None or key is None or "." not in key:
        return None
    return locale_expr, key


class MigrateTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        dynamic = _extract_localize_dynamic(node)
        if dynamic is not None:
            locale_expr, key_expr, extra = dynamic
            return ast.Call(
                func=ast.Name(id="raw", ctx=ast.Load()),
                args=[self.visit(key_expr), self.visit(locale_expr)],
                keywords=[self.visit(kw) for kw in extra],
            )

        extracted = _extract_localize_key(node)
        if extracted is not None:
            locale_expr, key = extracted
            extra = [kw for kw in node.keywords if kw.arg not in ("locale", "key")]
            if len(node.args) >= 2:
                extra = [self.visit(kw) for kw in node.keywords]
            else:
                extra = [self.visit(kw) for kw in extra]
            return ast.Call(
                func=_path_to_expr(_parse_path(key)),
                args=[self.visit(locale_expr)],
                keywords=extra,
            )

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "locale_str"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            key = node.args[0].value
            path_expr = _path_to_expr(_underscore_to_parts(key))
            return ast.Attribute(value=path_expr, attr="discord_key", ctx=ast.Load())

        return ast.Call(
            func=self.visit(node.func),
            args=[self.visit(a) for a in node.args],
            keywords=[self.visit(kw) for kw in node.keywords],
        )


class ImportAdder(ast.NodeTransformer):
    def __init__(self, needs_locale: bool) -> None:
        self.needs_locale = needs_locale
        self.has_locale_import = False
        self.has_tanjun = False

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module == "locale_keys" and any(a.name == "locale" for a in node.names):
            self.has_locale_import = True
        if node.module == "localizer" and any(a.name == "tanjunLocalizer" for a in node.names):
            self.has_tanjun = True
        return node

    def visit_Import(self, node: ast.Import) -> ast.AST:
        return node


def _migrate_file(path: Path, dry_run: bool) -> bool:
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    new_tree = MigrateTransformer().visit(tree)
    if new_tree is None:
        return False

    uses_locale = any(
        isinstance(n, ast.Name) and n.id in ("locale", "raw") for n in ast.walk(new_tree)
    )
    if not uses_locale:
        return False

    new_source = ast.unparse(new_tree)

    needs_raw = "raw(" in new_source
    import_line = "from locale_keys import locale" + (", raw" if needs_raw else "")
    if import_line not in new_source:
        lines = new_source.splitlines()
        future_line = next((i for i, l in enumerate(lines) if l.startswith("from __future__")), None)
        if future_line is not None:
            lines.insert(future_line + 1, import_line)
        elif lines and lines[0].startswith('"""'):
            insert_at = 0
            for i, line in enumerate(lines[1:], 1):
                if line.endswith('"""'):
                    insert_at = i + 1
                    break
            lines.insert(insert_at, import_line)
        elif lines and "from __future__" in lines[0]:
            lines.insert(1, import_line)
        else:
            lines.insert(0, import_line)
        new_source = "\n".join(lines) + "\n"
    elif needs_raw and ", raw" not in new_source:
        new_source = new_source.replace(
            "from locale_keys import locale\n",
            "from locale_keys import locale, raw\n",
        )

    if "tanjunLocalizer.localize" not in new_source and "from localizer import tanjunLocalizer" in new_source:
        new_source = new_source.replace("from localizer import tanjunLocalizer\n", "")
        new_source = new_source.replace(", tanjunLocalizer", "")
        new_source = new_source.replace("tanjunLocalizer, ", "")

    if new_source == source:
        return False

    if not dry_run:
        path.write_text(new_source, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    changed = 0
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if _migrate_file(path, args.dry_run):
            changed += 1
            print(path)

    print(f"{'Would change' if args.dry_run else 'Changed'} {changed} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
