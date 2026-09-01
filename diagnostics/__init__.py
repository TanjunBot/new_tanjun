"""Production-safe bot diagnostics for test_bot / benchmark_bot and CI."""

from diagnostics.benchmark_models import BenchmarkPhase, BenchmarkResult, BenchmarkSummary
from diagnostics.benchmark_runner import BenchmarkRunner
from diagnostics.models import CheckOutcome, CommandBehaviorSpec, DiagnosticsSummary, PhaseResult
from diagnostics.registry import all_specs, clear_spec_cache, run_spec
from diagnostics.runner import DiagnosticsRunner

__all__ = [
    "BenchmarkPhase",
    "BenchmarkResult",
    "BenchmarkRunner",
    "BenchmarkSummary",
    "CheckOutcome",
    "CommandBehaviorSpec",
    "DiagnosticsRunner",
    "DiagnosticsSummary",
    "PhaseResult",
    "all_specs",
    "clear_spec_cache",
    "run_spec",
]
