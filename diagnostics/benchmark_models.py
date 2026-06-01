from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class BenchmarkResult:
    bench_id: str
    samples_ms: list[float] = field(default_factory=list)
    detail: str = ""
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.samples_ms)

    @property
    def count(self) -> int:
        return len(self.samples_ms)

    @property
    def median_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        return round(statistics.median(self.samples_ms), 2)

    @property
    def p95_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        if len(self.samples_ms) == 1:
            return round(self.samples_ms[0], 2)
        ordered = sorted(self.samples_ms)
        idx = max(0, int(len(ordered) * 0.95) - 1)
        return round(ordered[idx], 2)

    @property
    def min_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        return round(min(self.samples_ms), 2)

    @property
    def max_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        return round(max(self.samples_ms), 2)

    @property
    def mean_ms(self) -> float:
        if not self.samples_ms:
            return 0.0
        return round(statistics.mean(self.samples_ms), 2)

    def summary(self) -> str:
        if self.error:
            return f"{self.bench_id}: ERROR — {self.error}"
        if not self.samples_ms:
            return f"{self.bench_id}: no samples"
        base = (
            f"{self.bench_id}: median={self.median_ms}ms "
            f"p95={self.p95_ms}ms mean={self.mean_ms}ms "
            f"min={self.min_ms} max={self.max_ms} (n={self.count})"
        )
        if self.detail:
            return f"{base} — {self.detail}"
        return base


@dataclass
class BenchmarkPhase:
    phase_id: str
    title: str
    results: list[BenchmarkResult] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return round(sum(r.mean_ms * max(r.count, 1) for r in self.results), 2)


@dataclass
class BenchmarkSummary:
    phases: list[BenchmarkPhase] = field(default_factory=list)
    total_wall_ms: float = 0.0

    @property
    def bench_count(self) -> int:
        return sum(len(p.results) for p in self.phases)

    @property
    def error_count(self) -> int:
        return sum(1 for p in self.phases for r in p.results if r.error)
