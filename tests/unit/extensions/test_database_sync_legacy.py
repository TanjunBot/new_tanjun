from __future__ import annotations

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils.database_dump_sql import (  # noqa: E402
    dump_uses_current_db_sections,
    extract_schemas_from_sql,
    filter_sql_dump,
    has_executable_sql,
    validate_filtered_import_sql,
)


def test_extract_schemas_from_schema_qualified_legacy_dump() -> None:
    sql = """
    -- legacy dump without USE/CREATE DATABASE
    CREATE TABLE `old_prod`.`users` (
      `id` bigint NOT NULL
    );
    INSERT INTO `old_prod`.`users` VALUES (1);
    """.strip()

    schemas = extract_schemas_from_sql(sql)

    assert "old_prod" in schemas


def test_extract_schemas_includes_current_database_marker() -> None:
    sql = """
    -- Current Database: `marker_db`
    USE `marker_db`;
    """.strip()

    schemas = extract_schemas_from_sql(sql)

    assert schemas == {"marker_db"}


def test_filter_sql_dump_rewrites_legacy_schema_qualified_statements() -> None:
    sql = """
    /*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
    CREATE TABLE `old_prod`.`users` (
      `id` bigint NOT NULL
    );
    INSERT INTO `old_prod`.`users` VALUES (1);
    """.strip()

    filtered = filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "DEFINER=`root`@`localhost`" not in filtered
    assert "`new_prod`.`users`" in filtered
    assert "`old_prod`.`users`" not in filtered


def test_filter_sql_dump_excludes_other_schema_when_use_statements_exist() -> None:
    sql = """
    USE `old_prod`;
    CREATE TABLE `old_prod`.`users` (`id` bigint NOT NULL);
    USE `other_prod`;
    CREATE TABLE `other_prod`.`audit` (`id` bigint NOT NULL);
    """.strip()

    filtered = filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "USE `new_prod`;" in filtered
    assert "`new_prod`.`users`" in filtered
    assert "`other_prod`.`audit`" not in filtered
    assert "USE `other_prod`;" not in filtered


def test_filter_sql_dump_legacy_skips_lines_after_create_database_for_other_schema() -> None:
    sql = """
    CREATE DATABASE `old_prod`;
    CREATE TABLE `old_prod`.`users` (`id` bigint NOT NULL);
    CREATE DATABASE `other_prod`;
    CREATE TABLE `other_prod`.`audit` (`id` bigint NOT NULL);
    """.strip()

    filtered = filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "`new_prod`.`users`" in filtered
    assert "`other_prod`.`audit`" not in filtered


def test_extract_schemas_includes_use_create_and_qualified_schema_names() -> None:
    sql = """
    CREATE DATABASE IF NOT EXISTS `db_from_create`;
    USE `db_from_use`;
    CREATE TABLE `db_from_qualified`.`users` (`id` bigint NOT NULL);
    """.strip()

    schemas = extract_schemas_from_sql(sql)

    assert schemas == {"db_from_create", "db_from_use", "db_from_qualified"}


def test_filter_sql_dump_removes_definer_case_insensitively() -> None:
    sql = """
    /*!50013 definer = `legacy`@`%` SQL SECURITY DEFINER */
    CREATE VIEW `old_prod`.`v_users` AS SELECT 1;
    """.strip()

    filtered = filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "definer" not in filtered.lower()
    assert "`new_prod`.`v_users`" in filtered


def test_dump_uses_current_db_sections_detects_marker() -> None:
    assert not dump_uses_current_db_sections("USE `db`;")
    assert dump_uses_current_db_sections("-- Current Database: `db`\nUSE `db`;")


def test_filter_sql_dump_sections_keeps_only_selected_schema() -> None:
    sql = """
    -- header comment
    -- Current Database: `prod`
    USE `prod`;
    CREATE TABLE `prod`.`users` (`id` bigint NOT NULL);
    -- Current Database: `other`
    USE `other`;
    CREATE TABLE `other`.`audit` (`id` bigint NOT NULL);
    """.strip()

    filtered = filter_sql_dump(sql, selected_schema="prod", target_schema="target")

    assert "-- header comment" in filtered
    assert "USE `target`;" in filtered
    assert "`target`.`users`" in filtered
    assert "`other`.`audit`" not in filtered
    assert "USE `other`;" not in filtered


def test_has_executable_sql() -> None:
    assert not has_executable_sql("-- only a comment\n")
    assert not has_executable_sql("/*!40101 SET NAMES utf8 */;\n")
    assert has_executable_sql("SELECT 1;\n")


def test_validate_filtered_import_sql_success() -> None:
    sql = "CREATE DATABASE `target`;\nUSE `target`;\nCREATE TABLE `users` (`id` int);\n"

    ok, error, tables = validate_filtered_import_sql(sql, "target")

    assert ok
    assert error == ""
    assert tables == ["users"]


def test_validate_filtered_import_sql_rejects_empty_executable_content() -> None:
    ok, error, tables = validate_filtered_import_sql("-- comment only\n", "target")

    assert not ok
    assert "empty import file" in error
    assert tables == []


def test_validate_filtered_import_sql_requires_target_schema_statements() -> None:
    sql = "USE `other`;\nCREATE TABLE `users` (`id` int);\n"

    ok, error, tables = validate_filtered_import_sql(sql, "target")

    assert not ok
    assert "CREATE/USE statements" in error
    assert tables == []


def test_validate_filtered_import_sql_rejects_foreign_use_statements() -> None:
    sql = "USE `target`;\nUSE `other`;\nCREATE TABLE `users` (`id` int);\n"

    ok, error, tables = validate_filtered_import_sql(sql, "target")

    assert not ok
    assert "other schemas" in error
    assert tables == []


def test_validate_filtered_import_sql_requires_create_table() -> None:
    sql = "USE `target`;\nSELECT 1;\n"

    ok, error, tables = validate_filtered_import_sql(sql, "target")

    assert not ok
    assert "CREATE TABLE" in error
    assert tables == []
