from __future__ import annotations

from diagnostics.benchmark_models import BenchmarkPhase, BenchmarkResult, BenchmarkSummary


def test_benchmark_result_summary_with_samples() -> None:
    result = BenchmarkResult("test.sample", samples_ms=[10.0, 20.0, 30.0, 40.0, 100.0])
    text = result.summary()
    assert "test.sample" in text
    assert "median=30.0ms" in text
    assert "n=5" in text


def test_benchmark_result_summary_error() -> None:
    result = BenchmarkResult("test.fail", error="boom")
    assert result.summary() == "test.fail: ERROR — boom"


def test_benchmark_result_ok_false_on_error() -> None:
    assert not BenchmarkResult("x", error="fail").ok


def test_benchmark_result_p95_single_sample() -> None:
    result = BenchmarkResult("x", samples_ms=[42.0])
    assert result.p95_ms == 42.0


def test_benchmark_result_has_grade() -> None:
    result = BenchmarkResult("database.select_1", samples_ms=[9.0, 10.0, 11.0])
    assert result.grade in {"A+", "A", "B", "C", "D", "F"}
    assert result.plain_quality
    assert result.plain_explanation


def test_benchmark_summary_overall_grade_penalizes_errors() -> None:
    fast = BenchmarkResult("runtime.event_loop_yield", samples_ms=[0.2, 0.2, 0.3])
    failed = BenchmarkResult("database.select_1", error="db down")
    summary = BenchmarkSummary(phases=[BenchmarkPhase("A", "Test", results=[fast, failed])])
    assert summary.error_count == 1
    assert summary.overall_grade in {"A+", "A", "B", "C", "D", "F"}
    assert summary.overall_score >= 0.0
