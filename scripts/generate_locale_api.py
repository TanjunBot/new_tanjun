#!/usr/bin/env python3
"""Generate grouped dataclass locale API from locales/en.json."""

from __future__ import annotations

import argparse
import json
import keyword
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import TextIO

ROOT = Path(__file__).resolve().parent.parent
LOCALE_DIR = ROOT / "locales"
OUT_DIR = ROOT / "locale_keys"
TREE_DIR = OUT_DIR / "_tree"

_IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

STANDARD_FIELDS = frozenset({
    "title",
    "description",
    "name",
    "label",
    "placeholder",
    "true",
    "false",
    "footer",
    "content",
    "author",
})

DYNAMIC_PREFIXES: tuple[str, ...] = (
    "logs.automodRuleCreate.",
    "logs.automodRuleCreate.timeout_duration.",
    "logs.guild_channelDelete.types.",
    "logs.guild_channelCreate.types.",
    "logs.guild_channelUpdate.types.",
    "logs.guildChannelDelete.types.",
    "logs.guildChannelCreate.types.",
    "logs.guildChannelUpdate.types.",
    "logs.permissions.",
    "logs.guildUpdate.featuresLocales.",
    "logs.guildUpdate.preferredLocaleLocales.",
    "logs.inviteCreate.targetTypeLocales.",
)

TOP_LEVEL_BUCKETS = ("commands", "logs", "admin", "other")


def _py_escape(s: str) -> str:
    return repr(s)


def _placeholders(translation: str) -> tuple[str, ...]:
    try:
        return tuple(sorted(set(Template(translation).get_identifiers())))
    except ValueError:
        return ()


def _load_entries() -> dict[str, tuple[str, ...]]:
    data = json.loads((LOCALE_DIR / "en.json").read_text(encoding="utf-8"))
    result: dict[str, tuple[str, ...]] = {}
    for entry in data:
        if not isinstance(entry, dict):
            continue
        ident = entry.get("identifier")
        if not isinstance(ident, str) or "." not in ident:
            continue
        result[ident] = _placeholders(str(entry.get("translation", "")))
    return result


def _dynamic_suffixes(keys: dict[str, tuple[str, ...]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for prefix in DYNAMIC_PREFIXES:
        suffix_map: dict[str, str] = {}
        for key in keys:
            if key.startswith(prefix):
                suffix = key[len(prefix) :]
                if suffix:
                    suffix_map[suffix] = key
        if suffix_map:
            out[prefix] = suffix_map
    return out


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


def _sanitize_field(seg: str) -> str:
    if _IDENT_RE.match(seg.strip('"')):
        name = seg.strip('"')
    else:
        name = re.sub(r"[^a-zA-Z0-9_]", "_", seg.strip('"'))
        if not name:
            name = "key"
        if name[0].isdigit():
            name = f"_{name}"
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name


def _path_var(path: tuple[str, ...]) -> str:
    if not path:
        return "_n_root"
    return "_n_" + "_".join(_sanitize_field(p) for p in path)


def _segment_pascal(seg: str) -> str:
    chunks = re.split(r"[_\s]+", seg.strip('"'))
    out = ""
    for chunk in chunks:
        safe = re.sub(r"[^a-zA-Z0-9]", "", chunk)
        if not safe:
            continue
        if safe[0].isdigit():
            safe = f"_{safe}"
        out += safe[0].upper() + safe[1:]
    return out or "Key"


def _class_name(path_parts: tuple[str, ...]) -> str:
    if not path_parts:
        return "LocaleRoot"
    parts: list[str] = []
    for p in path_parts:
        name = _sanitize_field(p)
        parts.append(name[0].upper() + name[1:])
    return "".join(parts)


@dataclass
class TreeNode:
    path: tuple[str, ...]
    groups: dict[str, dict[str, str]] = field(default_factory=dict)
    leaves: dict[str, str] = field(default_factory=dict)
    children: dict[str, TreeNode] = field(default_factory=dict)
    bracket_children: dict[str, TreeNode] = field(default_factory=dict)
    resolve_prefix: str | None = None
    resolve_suffixes: dict[str, str] = field(default_factory=dict)

    @property
    def class_name(self) -> str:
        return _class_name(self.path)

    def bucket(self) -> str:
        if not self.path:
            return "other"
        top = self.path[0]
        return top if top in ("commands", "logs", "admin") else "other"


def _get_node(root: TreeNode, path: tuple[str, ...]) -> TreeNode:
    node = root
    for seg in path:
        if _IDENT_RE.match(seg.strip('"')):
            if seg not in node.children:
                node.children[seg] = TreeNode(path=node.path + (seg,))
            node = node.children[seg]
        else:
            if seg not in node.bracket_children:
                node.bracket_children[seg] = TreeNode(path=node.path + (seg,))
            node = node.bracket_children[seg]
    return node


def _build_tree(keys: dict[str, tuple[str, ...]], dynamic: dict[str, dict[str, str]]) -> TreeNode:
    root = TreeNode(path=())
    group_paths: set[tuple[str, ...]] = set()

    for key in keys:
        parts = _parse_path(key)
        if len(parts) < 2:
            continue
        if parts[-1] in STANDARD_FIELDS:
            group_paths.add(tuple(parts[:-1]))

    for key in keys:
        parts = _parse_path(key)
        if len(parts) < 2:
            continue
        last = parts[-1]
        if last in STANDARD_FIELDS:
            group_seg = parts[-2]
            node = _get_node(root, tuple(parts[:-2]))
            if group_seg not in node.groups:
                node.groups[group_seg] = {}
            node.groups[group_seg][last] = key
            continue

        parent_path = tuple(parts[:-1])
        field_name = parts[-1]
        if parent_path in group_paths:
            group_seg = parts[-2]
            node = _get_node(root, tuple(parts[:-2]))
            if group_seg not in node.groups:
                node.groups[group_seg] = {}
            node.groups[group_seg][field_name] = key
            continue

        node = _get_node(root, parent_path)
        node.leaves[field_name] = key

    def _is_empty_node(node: TreeNode) -> bool:
        return not node.groups and not node.leaves and not node.children and not node.bracket_children

    def _prune(node: TreeNode) -> None:
        for group_seg in list(node.groups):
            child = node.children.get(group_seg)
            if child is not None and _is_empty_node(child):
                node.children.pop(group_seg)
            bracket = node.bracket_children.get(group_seg)
            if bracket is not None and _is_empty_node(bracket):
                node.bracket_children.pop(group_seg)
            if group_seg in node.leaves:
                node.groups[group_seg]["_text"] = node.leaves.pop(group_seg)
        for seg in list(node.children):
            if seg in node.leaves:
                node.children[seg].leaves["_text"] = node.leaves.pop(seg)
        for seg in list(node.bracket_children):
            if seg in node.leaves:
                node.bracket_children[seg].leaves["_text"] = node.leaves.pop(seg)
        for child in node.children.values():
            _prune(child)
        for child in node.bracket_children.values():
            _prune(child)

    def _merge_groups_into_children(node: TreeNode) -> None:
        for group_seg, fields in list(node.groups.items()):
            child = node.children.get(group_seg)
            if child is not None:
                for fname, fkey in fields.items():
                    child.leaves[fname] = fkey
                del node.groups[group_seg]
        for child in node.children.values():
            _merge_groups_into_children(child)
        for child in node.bracket_children.values():
            _merge_groups_into_children(child)

    def _finalize_conflicts(node: TreeNode) -> None:
        for group_seg, fields in list(node.groups.items()):
            if group_seg in node.leaves:
                fields["_text"] = node.leaves.pop(group_seg)
        for child in node.children.values():
            _finalize_conflicts(child)
        for child in node.bracket_children.values():
            _finalize_conflicts(child)

    _prune(root)
    _merge_groups_into_children(root)
    _finalize_conflicts(root)

    for prefix, suffix_map in dynamic.items():
        base_path = tuple(prefix.rstrip(".").split("."))
        node = _get_node(root, base_path)
        node.resolve_prefix = prefix
        node.resolve_suffixes = suffix_map

    return root


def _collect_nodes(node: TreeNode, out: list[TreeNode]) -> None:
    for child in node.children.values():
        _collect_nodes(child, out)
    for child in node.bracket_children.values():
        _collect_nodes(child, out)
    if node.path or node.groups or node.leaves or node.resolve_prefix:
        out.append(node)


def _emit_registry(keys: dict[str, tuple[str, ...]], dynamic: dict[str, dict[str, str]]) -> str:
    lines = [
        '"""Auto-generated by scripts/generate_locale_api.py. Do not edit."""',
        "from __future__ import annotations",
        "",
        "PLACEHOLDERS: dict[str, tuple[str, ...]] = {",
    ]
    for key, ph in sorted(keys.items()):
        lines.append(f"    {_py_escape(key)}: {_py_escape(ph)},")
    lines.append("}")
    lines.append("")
    lines.append("DYNAMIC_SUFFIXES: dict[str, dict[str, str]] = {")
    for prefix, suffix_map in sorted(dynamic.items()):
        lines.append(f"    {_py_escape(prefix)}: {{")
        for suffix, full in sorted(suffix_map.items()):
            lines.append(f"        {_py_escape(suffix)}: {_py_escape(full)},")
        lines.append("    },")
    lines.append("}")
    lines.append("")
    lines.append("LOCALE_KEYS: tuple[str, ...] = (")
    for key in sorted(keys):
        lines.append(f"    {_py_escape(key)},")
    lines.append(")")
    lines.append("")
    return "\n".join(lines)


def _emit_literal_keys(keys: dict[str, tuple[str, ...]]) -> str:
    lines = [
        '"""Auto-generated by scripts/generate_locale_api.py. Do not edit."""',
        "from __future__ import annotations",
        "",
        "from typing import Literal",
        "",
        "LocaleKey = Literal[",
    ]
    for key in sorted(keys):
        lines.append(f"    {_py_escape(key)},")
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def _field_type_for_node(node: TreeNode, child: TreeNode | None, group_class: str | None) -> str:
    if group_class:
        return group_class
    if child is not None:
        return child.class_name
    return "LocalizedString"


def _emit_node_builder(node: TreeNode, lines: list[str], indent: int) -> str:
    pad = "    " * indent
    inner_pad = "    " * (indent + 1)
    var = _path_var(node.path)

    for seg, child in sorted(node.children.items()):
        _emit_node_builder(child, lines, indent)

    for seg, child in sorted(node.bracket_children.items()):
        _emit_node_builder(child, lines, indent)

    args: list[str] = []

    for group_seg, fields in sorted(node.groups.items()):
        group_class = _class_name(node.path + (group_seg,))
        group_var = f"{var}_{_sanitize_field(group_seg)}"
        lines.append(f"{pad}{group_var} = {group_class}(")
        for fname, fkey in sorted(fields.items()):
            lines.append(f"{inner_pad}{_sanitize_field(fname)}=LocalizedString({_py_escape(fkey)}),")
        lines.append(f"{pad})")
        args.append(f"{_sanitize_field(group_seg)}={group_var}")

    for leaf_name, leaf_key in sorted(node.leaves.items()):
        args.append(f"{_sanitize_field(leaf_name)}=LocalizedString({_py_escape(leaf_key)})")

    for seg in sorted(node.children):
        args.append(f"{_sanitize_field(seg)}={_path_var(node.children[seg].path)}")

    for seg in sorted(node.bracket_children):
        args.append(f"{_sanitize_field(seg)}={_path_var(node.bracket_children[seg].path)}")

    if node.resolve_prefix and node.resolve_suffixes:
        resolve_var = f"{var}_resolve"
        lines.append(f"{pad}{resolve_var} = ResolveMap(")
        lines.append(f"{inner_pad}{_py_escape(node.resolve_prefix)},")
        lines.append(f"{inner_pad}{{")
        for suffix, full in sorted(node.resolve_suffixes.items()):
            lines.append(f"{inner_pad}    {_py_escape(suffix)}: LocalizedString({_py_escape(full)}),")
        lines.append(f"{inner_pad}}},")
        lines.append(f"{pad})")
        args.append(f"resolve={resolve_var}")

    seen_args: dict[str, str] = {}
    for arg in args:
        name = arg.split("=", 1)[0]
        seen_args[name] = arg
    lines.append(f"{pad}{var} = {node.class_name}(")
    for arg in sorted(seen_args.values(), key=lambda a: a.split("=", 1)[0]):
        lines.append(f"{inner_pad}{arg},")
    lines.append(f"{pad})")
    return var


def _emit_group_class(node: TreeNode, group_seg: str, fields: dict[str, str], lines: list[str]) -> None:
    group_class = _class_name(node.path + (group_seg,))
    lines.append("")
    lines.append("@dataclass(frozen=True, slots=True)")
    lines.append(f"class {group_class}:")
    for fname in sorted(fields):
        lines.append(f"    {_sanitize_field(fname)}: LocalizedString")


def _emit_class_def(node: TreeNode, lines: list[str]) -> None:
    for group_seg, fields in sorted(node.groups.items()):
        _emit_group_class(node, group_seg, fields, lines)

    lines.append("")
    lines.append("@dataclass(frozen=True, slots=True)")
    lines.append(f"class {node.class_name}:")

    if not node.groups and not node.leaves and not node.children and not node.bracket_children and not node.resolve_prefix:
        lines.append("    pass")
        return

    for group_seg in sorted(node.groups):
        group_class = _class_name(node.path + (group_seg,))
        lines.append(f"    {_sanitize_field(group_seg)}: {group_class}")

    for leaf_name in sorted(node.leaves):
        if leaf_name in node.groups:
            continue
        lines.append(f"    {_sanitize_field(leaf_name)}: LocalizedString")

    for seg in sorted(node.children):
        child = node.children[seg]
        lines.append(f"    {_sanitize_field(seg)}: {child.class_name}")

    for seg in sorted(node.bracket_children):
        child = node.bracket_children[seg]
        fname = _sanitize_field(seg)
        if fname in {f for f in node.leaves} or fname in node.children:
            fname = f"{fname}_map"
        lines.append(f"    {fname}: {child.class_name}")

    if node.resolve_prefix:
        lines.append("    resolve: ResolveMap")


def _emit_tree_module(bucket: str, nodes: list[TreeNode], root: TreeNode) -> str:
    lines: list[str] = [
        f'"""Auto-generated locale tree: {bucket}. Do not edit."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
        "from locale_keys.types import LocalizedString, ResolveMap",
        "",
    ]

    sorted_nodes = sorted(nodes, key=lambda n: n.path)
    for node in sorted_nodes:
        if node.path and node.bucket() == bucket:
            _emit_class_def(node, lines)
        elif not node.path and bucket == "other":
            _emit_class_def(node, lines)

    if bucket == "other":
        target_root = root
    else:
        if bucket not in root.children:
            return "\n".join(lines) + "\n"
        target_root = root.children[bucket]

    lines.append("")
    lines.append(f"def build_{bucket}() -> {target_root.class_name}:")
    build_lines: list[str] = ["    resolve: ResolveMap"]
    _emit_node_builder(target_root, build_lines, indent=1)
    lines.extend(build_lines)
    lines.append("")

    return "\n".join(lines) + "\n"


def _emit_tree_init(root: TreeNode) -> str:
    lines = [
        '"""Auto-generated locale root. Do not edit."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
        "from locale_keys._tree.commands import build_commands",
        "from locale_keys._tree.logs import build_logs",
        "from locale_keys._tree.admin import build_admin",
        "from locale_keys._tree.other import build_other",
        "",
        "@dataclass(frozen=True, slots=True)",
        "class LocaleRoot:",
    ]

    for seg in sorted(root.children):
        child = root.children[seg]
        lines.append(f"    {_sanitize_field(seg)}: {child.class_name}")

    for seg in sorted(root.bracket_children):
        child = root.bracket_children[seg]
        lines.append(f"    {_sanitize_field(seg)}: {child.class_name}")

    if not root.children and not root.bracket_children:
        lines.append("    pass")

    lines.extend([
        "",
        "def build_locale() -> LocaleRoot:",
        "    return LocaleRoot(",
    ])
    for seg in sorted(root.children):
        if seg == "commands":
            lines.append("        commands=build_commands(),")
        elif seg == "logs":
            lines.append("        logs=build_logs(),")
        elif seg == "admin":
            lines.append("        admin=build_admin(),")
        else:
            lines.append(f"        {_sanitize_field(seg)}=build_other().{_sanitize_field(seg)},")
    if "commands" not in root.children:
        pass
    lines.append("    )")
    lines.append("")
    lines.append("locale = build_locale()")
    lines.append("")
    return "\n".join(lines)


def _write(path: Path, content: str, check: bool) -> bool:
    if check:
        if path.exists() and path.read_text(encoding="utf-8") == content:
            return True
        print(f"Would change {path}", file=sys.stderr)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _emit_bucket_file(bucket: str, root: TreeNode, all_nodes: list[TreeNode]) -> str:
    lines: list[str] = [
        f'"""Auto-generated locale tree: {bucket}. Do not edit."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
        "from locale_keys.types import LocalizedString, ResolveMap",
        "",
    ]

    bucket_nodes = [n for n in all_nodes if n.path and n.path[0] == bucket]
    if bucket == "other":
        bucket_nodes = [
            n
            for n in all_nodes
            if n.path and n.path[0] not in ("commands", "logs", "admin")
        ]
        bucket_nodes.append(root)

    bucket_nodes = sorted({n.path: n for n in bucket_nodes}.values(), key=lambda n: len(n.path))

    for node in bucket_nodes:
        if node.path == ():
            continue
        _emit_class_def(node, lines)

    if bucket not in root.children and bucket != "other":
        lines.append("")
        lines.append(f"def build_{bucket}() -> None:")
        lines.append("    raise RuntimeError('empty bucket')")
        lines.append("")
        return "\n".join(lines)

    if bucket == "other":
        lines.extend(_emit_other_module(root, all_nodes))
        return "\n".join(lines) + "\n"

    target = root.children[bucket]
    lines.append("")
    lines.append(f"def build_{bucket}() -> {target.class_name}:")
    builder: list[str] = []
    result_var = _emit_node_builder(target, builder, 1)
    lines.extend(builder)
    lines.append(f"    return {result_var}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _emit_other_module(root: TreeNode, all_nodes: list[TreeNode]) -> list[str]:
    lines: list[str] = []
    other_tops = [seg for seg in root.children if seg not in ("commands", "logs", "admin")]

    if not other_tops:
        lines.append("@dataclass(frozen=True, slots=True)")
        lines.append("class OtherLocales:")
        lines.append("    pass")
        lines.append("")
        lines.append("def build_other() -> OtherLocales:")
        lines.append("    return OtherLocales()")
        return lines

    lines.append("@dataclass(frozen=True, slots=True)")
    lines.append("class OtherLocales:")
    for seg in sorted(other_tops):
        child = root.children[seg]
        lines.append(f"    {_sanitize_field(seg)}: {child.class_name}")
    lines.append("")
    lines.append("def build_other() -> OtherLocales:")
    builder: list[str] = []
    root_args: list[str] = []
    for seg in sorted(other_tops):
        child = root.children[seg]
        var = _emit_node_builder(child, builder, 1)
        root_args.append(f"    {_sanitize_field(seg)}={var},")
    lines.extend(builder)
    lines.append("    return OtherLocales(")
    lines.extend(root_args)
    lines.append("    )")
    return lines


def _emit_root_init(root: TreeNode) -> str:
    primary = ("commands", "logs", "admin")
    other_segs = [s for s in root.children if s not in primary]

    lines = [
        '"""Auto-generated locale root. Do not edit."""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
    ]

    for bucket in primary:
        if bucket in root.children:
            child = root.children[bucket]
            lines.append(f"from locale_keys._tree.{bucket} import {child.class_name}, build_{bucket}")
    if other_segs:
        lines.append("from locale_keys._tree.other import build_other")

    lines.extend(["", "@dataclass(frozen=True, slots=True)", "class LocaleRoot:"])
    for bucket in primary:
        if bucket in root.children:
            lines.append(f"    {_sanitize_field(bucket)}: {root.children[bucket].class_name}")
    for seg in sorted(other_segs):
        lines.append(f"    {_sanitize_field(seg)}: {root.children[seg].class_name}")

    lines.extend(["", "def build_locale() -> LocaleRoot:"])
    if other_segs:
        lines.append("    other = build_other()")
    lines.append("    return LocaleRoot(")
    for bucket in primary:
        if bucket in root.children:
            lines.append(f"        {_sanitize_field(bucket)}=build_{bucket}(),")
    for seg in sorted(other_segs):
        lines.append(f"        {_sanitize_field(seg)}=other.{_sanitize_field(seg)},")
    lines.extend(["    )", "", "locale = build_locale()", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    keys = _load_entries()
    dynamic = _dynamic_suffixes(keys)
    root = _build_tree(keys, dynamic)

    all_nodes: list[TreeNode] = []
    _collect_nodes(root, all_nodes)
    if root.path == () and (root.children or root.groups):
        all_nodes.insert(0, root)

    ok = True
    ok &= _write(OUT_DIR / "_registry.py", _emit_registry(keys, dynamic), args.check)
    ok &= _write(OUT_DIR / "_literal_keys.py", _emit_literal_keys(keys), args.check)

    for bucket in ("commands", "logs", "admin", "other"):
        content = _emit_bucket_file(bucket, root, all_nodes)
        ok &= _write(TREE_DIR / f"{bucket}.py", content, args.check)

    ok &= _write(TREE_DIR / "__init__.py", _emit_root_init(root), args.check)

    if not args.check:
        print(f"Generated {len(keys)} keys -> {OUT_DIR} ({len(all_nodes)} dataclasses)")

    if args.check and not ok:
        print("Generated locale API is out of date. Run: python scripts/generate_locale_api.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
