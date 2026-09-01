from __future__ import annotations

import statistics
from dataclasses import dataclass, field

GRADE_BANDS: tuple[tuple[str, float], ...] = (
    ("A+", 115.0),
    ("A", 100.0),
    ("B", 90.0),
    ("C", 75.0),
    ("D", 60.0),
    ("F", 0.0),
)

BENCH_TARGETS_MS: dict[str, float] = {
    "discord.gateway_latency": 120.0,
    "discord.message_roundtrip": 280.0,
    "database.pool_acquire": 6.0,
    "database.select_1": 22.0,
    "database.parallel_select_1": 150.0,
    "database.level_config_count": 40.0,
    "database.guild_level_config": 30.0,
    "localization.sample_keys": 10.0,
    "localization.locale_file_load": 30.0,
    "io.manifest_json_parse": 1.0,
    "commands.tree_enumerate": 7.0,
    "commands.manifest_compare": 12.0,
    "commands.prefix_enumerate": 8.0,
    "handlers.all_specs": 350.0,
    "runtime.event_loop_yield": 1.5,
    "runtime.async_gather": 10.0,
}

PREFIX_TARGETS_MS: tuple[tuple[str, float], ...] = (
    ("health.", 120.0),
    ("database.", 30.0),
    ("runtime.", 10.0),
    ("commands.", 12.0),
    ("localization.", 20.0),
    ("discord.", 250.0),
)


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

    @property
    def display_name(self) -> str:
        return self.bench_id.replace(".", " ").replace("_", " ").title()

    @property
    def target_ms(self) -> float:
        if self.bench_id in BENCH_TARGETS_MS:
            return BENCH_TARGETS_MS[self.bench_id]
        for prefix, target in PREFIX_TARGETS_MS:
            if self.bench_id.startswith(prefix):
                return target
        return 50.0

    @property
    def grade_score(self) -> float:
        if not self.ok:
            return 0.0
        median = self.median_ms
        if median <= 0:
            return 120.0
        score = (self.target_ms / median) * 100
        return round(max(0.0, min(130.0, score)), 1)

    @property
    def grade(self) -> str:
        for grade, threshold in GRADE_BANDS:
            if self.grade_score >= threshold:
                return grade
        return "F"

    @property
    def plain_quality(self) -> str:
        if self.error:
            return "not available"
        if self.grade in {"A+", "A"}:
            return "excellent"
        if self.grade == "B":
            return "good"
        if self.grade == "C":
            return "acceptable"
        if self.grade == "D":
            return "weak"
        return "poor"

    @property
    def plain_explanation(self) -> str:
        if self.error:
            return "This check failed and should be reviewed."
        if self.grade in {"A+", "A"}:
            return "Users should feel this as fast and responsive."
        if self.grade == "B":
            return "Performance is solid and should feel smooth."
        if self.grade == "C":
            return "This is usable but has room to improve."
        if self.grade == "D":
            return "Users may notice delays in this area."
        return "This is slow and likely needs optimization."

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
        base = f"{base} grade={self.grade} ({self.plain_quality})"
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

    @property
    def ok_results(self) -> list[BenchmarkResult]:
        return [r for p in self.phases for r in p.results if r.ok]

    @property
    def overall_score(self) -> float:
        ok = self.ok_results
        if not ok:
            return 0.0
        raw = sum((r.grade_score for r in ok)) / len(ok)
        penalized = max(0.0, raw - (self.error_count * 12.0))
        return round(penalized, 1)

    @property
    def overall_grade(self) -> str:
        for grade, threshold in GRADE_BANDS:
            if self.overall_score >= threshold:
                return grade
        return "F"
