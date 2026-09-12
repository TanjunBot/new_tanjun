from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from utils.migration_ddl import (  # noqa: E402
    _dependency_batches,
    ordered_table_names,
    run_create_all_tables,
)

pytestmark = pytest.mark.unit


def test_dependency_batches_raises_on_unresolvable_cycle() -> None:
    deps = {"child_a": ["child_b"], "child_b": ["child_a"]}
    with (
        patch("utils.migration_ddl.CREATE_TABLE_DEPENDENCIES", deps),
        pytest.raises(RuntimeError, match="Cannot resolve table dependencies"),
    ):
        _dependency_batches({"child_a", "child_b"})


def test_ordered_table_names_orders_parents_before_children() -> None:
    names = ordered_table_names({"reports", "report_evidence", "report_mod_actions"})
    assert names.index("reports") < names.index("report_evidence")
    assert names.index("reports") < names.index("report_mod_actions")


def test_run_create_all_tables_executes_ddl_in_order() -> None:
    import migrations.snapshot_001 as snapshot

    connection = MagicMock()
    order = ["reports", "report_evidence"]
    ddl = {
        "reports": "CREATE TABLE `reports` (id INT)",
        "report_evidence": "CREATE TABLE `report_evidence` (id INT)",
    }
    with (
        patch.object(snapshot, "CREATE_ORDER", order),
        patch.object(snapshot, "TABLE_DDL", ddl),
    ):
        run_create_all_tables(connection)
    assert connection.execute.call_count == 2
    first_sql = str(connection.execute.call_args_list[0][0][0])
    assert "reports" in first_sql


def test_migration_chain_reaches_nullable_repair_head() -> None:
    import importlib

    revisions = [
        importlib.import_module(f"migrations.versions.{name}")
        for name in (
            "001_initial_schema",
            "002_legacy_schema_patches",
            "003_giveaway_legacy_column",
            "004_schema_fk_and_guild_keys",
            "005_legacy_camelcase_columns",
            "006_giveaway_id_not_null",
            "007_welcome_leave_channel_nullable",
            "008_nullable_repair",
        )
    ]

    assert revisions[0].down_revision is None
    for previous, current in zip(revisions[:-1], revisions[1:], strict=True):
        assert current.down_revision == previous.revision
    assert revisions[-1].revision == "008_nullable_repair"
