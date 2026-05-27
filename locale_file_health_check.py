"""Locale file integrity health check for Tanjun bot.

Verifies that locale files (en.json, de.json) exist, are valid JSON,
contain all required translation keys, and are not missing any keys
compared to the primary language (en.json).
"""

from __future__ import annotations

import json
from pathlib import Path

from health.checks import HealthCheck, HealthCheckResult, HealthStatus


class LocaleFileHealthCheck(HealthCheck):
    """Health check for locale file integrity.

    Checks:
    1. Both en.json and de.json files exist
    2. Both files parse as valid JSON
    3. All required translation keys are present in both files
    4. No missing translations compared to en.json (warning only)
    """

    REQUIRED_KEYS = [
        "commands.help.select.placeholder",
        "commands.help.select.title",
        "commands.help.timeout.title",
        "commands.admin.addrole.missingPermission.title",
    ]

    LOCALE_DIR = "locales"
    LOCALES = ["en", "de"]

    @property
    def name(self) -> str:
        return "Locale Files"

    @property
    def critical(self) -> bool:
        return True  # Bot cannot communicate without translations

    async def run(self) -> HealthCheckResult:
        missing_files: list[str] = []
        invalid_json: list[str] = []
        missing_keys: list[str] = []
        locale_data: dict[str, list[dict]] = {}
        warnings: list[str] = []

        for locale in self.LOCALES:
            filepath = Path(self.LOCALE_DIR) / f"{locale}.json"

            # Check file exists
            if not filepath.exists():
                missing_files.append(locale)
                continue

            # Check valid JSON
            try:
                with filepath.open(encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                invalid_json.append(f"{locale}: {e}")
                continue

            # Validate it's a list of dicts
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                invalid_json.append(f"{locale}: expected array of objects")
                continue

            locale_data[locale] = data

            # Check required keys
            identifiers = {entry.get("identifier") for entry in data if isinstance(entry, dict)}
            for key in self.REQUIRED_KEYS:
                if key not in identifiers:
                    missing_keys.append(f"{locale}:{key}")

        # Cross-locale comparison: warn about keys in en.json missing from de.json
        if "en" in locale_data and "de" in locale_data:
            en_ids = {entry.get("identifier") for entry in locale_data["en"] if isinstance(entry, dict)}
            de_ids = {entry.get("identifier") for entry in locale_data["de"] if isinstance(entry, dict)}
            missing_from_de = en_ids - de_ids
            if missing_from_de:
                # Limit to first 20 to avoid absurdly long messages
                sample = sorted(missing_from_de)[:20]
                if len(missing_from_de) > 20:
                    warnings.append(
                        f"en.json has {len(missing_from_de)} entries not in de.json (showing first 20): {', '.join(sample)}"
                    )
                else:
                    warnings.append(f"en.json has {len(missing_from_de)} entries not in de.json: {', '.join(sample)}")

        issues: list[str] = []
        status = HealthStatus.HEALTHY

        if missing_files:
            issues.append(f"Missing files: {', '.join(missing_files)}")
            status = HealthStatus.CRITICAL
        if invalid_json:
            issues.append(f"Invalid JSON: {'; '.join(invalid_json)}")
            status = HealthStatus.CRITICAL
        if missing_keys:
            issues.append(f"Missing required keys: {', '.join(missing_keys)}")
            if status != HealthStatus.CRITICAL:
                status = HealthStatus.DEGRADED

        if status == HealthStatus.HEALTHY:
            if warnings:
                return HealthCheckResult(
                    self.name,
                    HealthStatus.HEALTHY,
                    "Locale files exist, parse correctly, and contain all required keys.",
                    details={"warnings": warnings},
                )
            return HealthCheckResult(
                self.name,
                status,
                "Locale files are valid and contain all required keys.",
            )

        details = {}
        if warnings:
            details["warnings"] = warnings

        return HealthCheckResult(self.name, status, "; ".join(issues), details=details or None)
