from __future__ import annotations

import re

_CURRENT_DB_MARKER_RE = re.compile(
    "^\\s*--\\s*Current Database:\\s*`([^`]+)`",
    re.IGNORECASE | re.MULTILINE,
)
_QUALIFIED_SCHEMA_RE = re.compile("`([^`]+)`\\.`[^`]+`")


def dump_uses_current_db_sections(sql_content: str) -> bool:
    return _CURRENT_DB_MARKER_RE.search(sql_content) is not None


def extract_schemas_from_sql(sql_content: str) -> set[str]:
    schemas: set[str] = set()
    for line in sql_content.splitlines():
        current_db_match = _CURRENT_DB_MARKER_RE.search(line)
        use_match = re.search("^\\s*USE\\s+`?([^\\s`;]+)`?", line, re.IGNORECASE)
        create_match = re.search(
            "^\\s*CREATE DATABASE\\s+(?:/\\*.*?\\*/\\s+)?(?:IF NOT EXISTS\\s+)?`?([^\\s`;]+)`?",
            line,
            re.IGNORECASE,
        )
        qualified_match = _QUALIFIED_SCHEMA_RE.search(line)
        if current_db_match:
            schemas.add(current_db_match.group(1))
        elif create_match:
            schemas.add(create_match.group(1))
        elif use_match:
            schemas.add(use_match.group(1))
        elif qualified_match:
            schemas.add(qualified_match.group(1))
    return schemas


def transform_dump_line(line: str, selected_schema: str, target_schema: str) -> str:
    mod_line = re.sub("DEFINER\\s*=\\s*`[^`]+`@`[^`]+`\\s*", "", line, flags=re.IGNORECASE)
    mod_line = re.sub("SQL\\s+SECURITY\\s+DEFINER\\s*", "", mod_line, flags=re.IGNORECASE)
    mod_line = re.sub(
        f"(CREATE DATABASE\\s+(?:/\\*.*?\\*/\\s+)?(?:IF NOT EXISTS\\s+)?)`?{re.escape(selected_schema)}`?",
        f"\\g<1>`{target_schema}`",
        mod_line,
        flags=re.IGNORECASE,
    )
    mod_line = re.sub(
        f"(USE\\s+)`?{re.escape(selected_schema)}`?",
        f"\\g<1>`{target_schema}`",
        mod_line,
        flags=re.IGNORECASE,
    )
    mod_line = re.sub(
        f"`{re.escape(selected_schema)}`\\.",
        f"`{target_schema}`.",
        mod_line,
        flags=re.IGNORECASE,
    )
    return mod_line


def filter_sql_dump_legacy(sql_content: str, selected_schema: str, target_schema: str) -> str:
    current_schema: str | None = None
    selected_lower = selected_schema.lower()
    output_lines: list[str] = []
    for line in sql_content.splitlines(keepends=True):
        use_m = re.search("^\\s*USE\\s+`?([^\\s`;]+)`?", line, re.IGNORECASE)
        create_m = re.search(
            "^\\s*CREATE DATABASE\\s+(?:/\\*.*?\\*/\\s+)?(?:IF NOT EXISTS\\s+)?`?([^\\s`;]+)`?",
            line,
            re.IGNORECASE,
        )
        if create_m:
            current_schema = create_m.group(1)
        elif use_m:
            current_schema = use_m.group(1)
        if current_schema is not None and current_schema.lower() != selected_lower:
            continue
        output_lines.append(transform_dump_line(line, selected_schema, target_schema))
    return "".join(output_lines)


def filter_sql_dump_sections(sql_content: str, selected_schema: str, target_schema: str) -> str:
    current_schema: str | None = None
    seen_current_db_marker = False
    selected_lower = selected_schema.lower()
    header_lines: list[str] = []
    selected_lines: list[str] = []
    for line in sql_content.splitlines(keepends=True):
        current_db_marker_m = _CURRENT_DB_MARKER_RE.search(line)
        use_m = re.search("^\\s*USE\\s+`?([^\\s`;]+)`?", line, re.IGNORECASE)
        create_m = re.search(
            "^\\s*CREATE DATABASE\\s+(?:/\\*.*?\\*/\\s+)?(?:IF NOT EXISTS\\s+)?`?([^\\s`;]+)`?",
            line,
            re.IGNORECASE,
        )
        if current_db_marker_m:
            current_schema = current_db_marker_m.group(1)
            seen_current_db_marker = True
        elif create_m:
            current_schema = create_m.group(1)
        elif use_m:
            current_schema = use_m.group(1)
        if not seen_current_db_marker:
            header_lines.append(line)
            continue
        if current_schema is not None and current_schema.lower() == selected_lower:
            selected_lines.append(line)
    transformed_lines = [
        transform_dump_line(line, selected_schema, target_schema) for line in header_lines + selected_lines
    ]
    return "".join(transformed_lines)


def filter_sql_dump(sql_content: str, selected_schema: str, target_schema: str) -> str:
    if dump_uses_current_db_sections(sql_content):
        return filter_sql_dump_sections(sql_content, selected_schema, target_schema)
    return filter_sql_dump_legacy(sql_content, selected_schema, target_schema)


def has_executable_sql(sql_content: str) -> bool:
    for raw_line in sql_content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("--") or line.startswith("/*") or line.startswith("*/"):
            continue
        if line.startswith("/*!"):
            continue
        return True
    return False


def extract_table_names_from_sql(sql_content: str) -> list[str]:
    names: list[str] = []
    for line in sql_content.splitlines():
        m = re.search("^\\s*CREATE\\s+TABLE\\s+`([^`]+)`", line, re.IGNORECASE)
        if m:
            names.append(m.group(1))
    return names


def extract_use_schemas(sql_content: str) -> list[str]:
    schemas: list[str] = []
    for line in sql_content.splitlines():
        m = re.search("^\\s*USE\\s+`?([^\\s`;]+)`?", line, re.IGNORECASE)
        if m:
            schemas.append(m.group(1))
    return schemas


def validate_filtered_import_sql(sql_content: str, target_schema: str) -> tuple[bool, str, list[str]]:
    if not has_executable_sql(sql_content):
        return False, "The selected schema produced an empty import file. Please choose a schema that exists in the dump.", []
    lower = sql_content.lower()
    if f"create database `{target_schema.lower()}`" not in lower and f"use `{target_schema.lower()}`" not in lower:
        return False, "The filtered import does not include CREATE/USE statements for the target schema.", []
    use_schemas = extract_use_schemas(sql_content)
    invalid_use = [name for name in use_schemas if name.lower() != target_schema.lower()]
    if invalid_use:
        bad = ", ".join(sorted(set(invalid_use))[:5])
        return False, f"The filtered import still references other schemas in USE statements: {bad}", []
    table_names = extract_table_names_from_sql(sql_content)
    if not table_names:
        return False, "The filtered import does not contain any CREATE TABLE statements.", []
    return True, "", table_names
