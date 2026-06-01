"""Production-safe bot diagnostics for test_bot and CI."""

from diagnostics.models import CheckOutcome, CommandBehaviorSpec, DiagnosticsSummary, PhaseResult
from diagnostics.registry import all_specs, run_spec
from diagnostics.runner import DiagnosticsRunner

__all__ = [
    "CheckOutcome",
    "CommandBehaviorSpec",
    "DiagnosticsRunner",
    "DiagnosticsSummary",
    "PhaseResult",
    "all_specs",
    "run_spec",
]
