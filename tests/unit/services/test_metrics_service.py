from __future__ import annotations

from unittest.mock import patch

import pytest
from prometheus_client import REGISTRY

from services import metrics_service


class TestGetProcessStats:
    def test_reads_linux_proc(self):
        stats = metrics_service._get_process_stats()
        assert "memory_bytes" in stats
        assert stats["memory_bytes"] > 0
        assert "cpu_seconds_total" in stats
        assert stats["threads"] >= 1.0
        assert stats["open_fds"] >= 1.0

    def test_handles_missing_proc_files(self):
        with (
            patch("builtins.open", side_effect=FileNotFoundError),
            patch("os.listdir", side_effect=FileNotFoundError),
        ):
            stats = metrics_service._get_process_stats()
        assert stats == {}

    def test_handles_malformed_stat(self):
        from unittest.mock import mock_open

        with patch("builtins.open", mock_open(read_data="1")):
            stats = metrics_service._get_process_stats()
        assert isinstance(stats, dict)


class TestUpdateProcessMetrics:
    def test_sets_gauges_from_stats(self):
        fake_stats = {
            "memory_bytes": 123456.0,
            "cpu_seconds_total": 42.5,
            "open_fds": 17.0,
            "threads": 8.0,
        }
        with patch.object(metrics_service, "_get_process_stats", return_value=fake_stats):
            metrics_service.update_process_metrics()
        assert metrics_service.process_memory_bytes._value.get() == 123456.0
        assert metrics_service.process_cpu_seconds._value.get() == 42.5
        assert metrics_service.process_open_fds._value.get() == 17.0
        assert metrics_service.process_threads._value.get() == 8.0

    def test_skips_missing_keys(self):
        with patch.object(metrics_service, "_get_process_stats", return_value={}):
            metrics_service.update_process_metrics()


class TestMetricRegistration:
    def test_command_metrics_registered(self):
        assert "tanjun_commands_tanjun_command_usage" in REGISTRY._names_to_collectors
        assert "tanjun_database_tanjun_db_query_duration_seconds" in REGISTRY._names_to_collectors
        assert "tanjun_bot_tanjun_guild_count" in REGISTRY._names_to_collectors

    def test_counter_increments(self):
        before = metrics_service.command_usage.labels(command="test_cmd", guild_id="1", status="ok")._value.get()
        metrics_service.command_usage.labels(command="test_cmd", guild_id="1", status="ok").inc()
        after = metrics_service.command_usage.labels(command="test_cmd", guild_id="1", status="ok")._value.get()
        assert after == before + 1


class TestLabelCardinality:
    _LOW_CARDINALITY_METRICS = (
        metrics_service.command_duration,
        metrics_service.db_query_duration,
        metrics_service.db_query_errors,
        metrics_service.db_pool_size,
        metrics_service.shard_latency,
        metrics_service.shard_connected,
        metrics_service.guild_count,
        metrics_service.user_count,
        metrics_service.message_processing_duration,
        metrics_service.process_memory_bytes,
        metrics_service.process_cpu_seconds,
        metrics_service.process_open_fds,
        metrics_service.process_threads,
        metrics_service.bot_start_time,
        metrics_service.loop_running,
        metrics_service.loop_iteration_duration,
        metrics_service.loop_iteration_errors,
    )

    _GUILD_ID_LABEL_METRICS = (
        metrics_service.command_usage,
        metrics_service.messages_processed,
    )

    def test_default_metrics_have_no_guild_id_label(self):
        for metric in self._LOW_CARDINALITY_METRICS:
            assert "guild_id" not in metric._labelnames, metric._name

    def test_guild_scoped_counters_use_guild_id_label(self):
        for metric in self._GUILD_ID_LABEL_METRICS:
            assert "guild_id" in metric._labelnames, metric._name


_ALL_METRICS = (
    metrics_service.command_usage,
    metrics_service.command_duration,
    metrics_service.db_query_duration,
    metrics_service.db_query_errors,
    metrics_service.db_pool_size,
    metrics_service.shard_latency,
    metrics_service.shard_connected,
    metrics_service.guild_count,
    metrics_service.user_count,
    metrics_service.messages_processed,
    metrics_service.message_processing_duration,
    metrics_service.process_memory_bytes,
    metrics_service.process_cpu_seconds,
    metrics_service.process_open_fds,
    metrics_service.process_threads,
    metrics_service.bot_start_time,
    metrics_service.loop_running,
    metrics_service.loop_iteration_duration,
    metrics_service.loop_iteration_errors,
)


class TestEveryMetricReferenced:
    @pytest.mark.parametrize("metric", _ALL_METRICS, ids=lambda m: m._name)
    def test_metric_name_registered(self, metric):
        assert metric._name in REGISTRY._names_to_collectors

    def test_each_metric_can_be_observed_or_set(self):
        metrics_service.command_usage.labels(command="x", guild_id="1", status="ok").inc()
        metrics_service.command_duration.labels(command="x").observe(0.01)
        metrics_service.db_query_duration.labels(operation="read").observe(0.001)
        metrics_service.db_query_errors.labels(operation="read").inc()
        metrics_service.db_pool_size.labels(type="used").set(1)
        metrics_service.shard_latency.labels(shard_id="0").set(0.05)
        metrics_service.shard_connected.labels(shard_id="0").set(1)
        metrics_service.guild_count.set(10)
        metrics_service.user_count.set(100)
        metrics_service.messages_processed.labels(guild_id="1").inc()
        metrics_service.message_processing_duration.observe(0.002)
        metrics_service.process_memory_bytes.set(1024)
        metrics_service.process_cpu_seconds.set(1.0)
        metrics_service.process_open_fds.set(5)
        metrics_service.process_threads.set(2)
        metrics_service.bot_start_time.set(1_700_000_000)
        metrics_service.loop_running.labels(loop_name="giveaway").set(1)
        metrics_service.loop_iteration_duration.labels(loop_name="giveaway").observe(0.1)
        metrics_service.loop_iteration_errors.labels(loop_name="giveaway").inc()


class TestUpdateProcessMetricsLive:
    def test_gauges_reflect_proc_after_update(self):
        metrics_service.update_process_metrics()
        assert metrics_service.process_memory_bytes._value.get() > 0
        assert metrics_service.process_cpu_seconds._value.get() > 0
        assert metrics_service.process_open_fds._value.get() >= 1.0
        assert metrics_service.process_threads._value.get() >= 1.0
