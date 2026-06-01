from __future__ import annotations

from diagnostics.benchmark_models import BenchmarkResult


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
