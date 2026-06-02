from __future__ import annotations

import tests.mock_config as mock_config

mock_config.patch_config_module()

from extensions.administration import _extract_schemas_from_sql, _filter_sql_dump  # noqa: E402


def test_extract_schemas_from_schema_qualified_legacy_dump() -> None:
    sql = """
    -- legacy dump without USE/CREATE DATABASE
    CREATE TABLE `old_prod`.`users` (
      `id` bigint NOT NULL
    );
    INSERT INTO `old_prod`.`users` VALUES (1);
    """.strip()

    schemas = _extract_schemas_from_sql(sql)

    assert "old_prod" in schemas


def test_filter_sql_dump_rewrites_legacy_schema_qualified_statements() -> None:
    sql = """
    /*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
    CREATE TABLE `old_prod`.`users` (
      `id` bigint NOT NULL
    );
    INSERT INTO `old_prod`.`users` VALUES (1);
    """.strip()

    filtered = _filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

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

    filtered = _filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "USE `new_prod`;" in filtered
    assert "`new_prod`.`users`" in filtered
    assert "`other_prod`.`audit`" not in filtered
    assert "USE `other_prod`;" not in filtered


def test_extract_schemas_includes_use_create_and_qualified_schema_names() -> None:
    sql = """
    CREATE DATABASE IF NOT EXISTS `db_from_create`;
    USE `db_from_use`;
    CREATE TABLE `db_from_qualified`.`users` (`id` bigint NOT NULL);
    """.strip()

    schemas = _extract_schemas_from_sql(sql)

    assert schemas == {"db_from_create", "db_from_use", "db_from_qualified"}


def test_filter_sql_dump_removes_definer_case_insensitively() -> None:
    sql = """
    /*!50013 definer = `legacy`@`%` SQL SECURITY DEFINER */
    CREATE VIEW `old_prod`.`v_users` AS SELECT 1;
    """.strip()

    filtered = _filter_sql_dump(sql, selected_schema="old_prod", target_schema="new_prod")

    assert "definer" not in filtered.lower()
    assert "`new_prod`.`v_users`" in filtered
