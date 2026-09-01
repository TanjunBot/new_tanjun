"""Locale file integrity health check for Tanjun bot.

Verifies that locale files listed in LOCALES exist, are valid JSON,
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
    1. All locale files in LOCALES exist
    2. All files parse as valid JSON
    3. All required translation keys are present in all files
    4. No missing translations compared to en.json (warning only)
    """
    LOCALE_DIR = 'locales'
    LOCALES = ['en', 'de', 'ko', 'bg', 'cs', 'da', 'el', 'es-419', 'fi', 'fr', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'lt', 'nl', 'vi', 'zh-CN', 'zh-TW']

    @property
    def name(self) -> str:
        return 'Locale Files'

    @property
    def critical(self) -> bool:
        return True

    async def run(self) -> HealthCheckResult:
        missing_files: list[str] = []
        invalid_json: list[str] = []
        missing_keys: list[str] = []
        locale_data: dict[str, list[dict]] = {}
        warnings: list[str] = []
        for locale in self.LOCALES:
            filepath = Path(self.LOCALE_DIR) / f'{locale}.json'
            if not filepath.exists():
                missing_files.append(locale)
                continue
            try:
                with filepath.open(encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                invalid_json.append(f'{locale}: {e}')
                continue
            if not isinstance(data, list) or not all((isinstance(item, dict) for item in data)):
                invalid_json.append(f'{locale}: expected array of objects')
                continue
            locale_data[locale] = data
        en_dot_keys: set[str] = set()
        if 'en' in locale_data:
            en_dot_keys = {str(entry['identifier']) for entry in locale_data['en'] if isinstance(entry, dict) and isinstance(entry.get('identifier'), str) and ('.' in str(entry['identifier']))}
        for loc, data in locale_data.items():
            identifiers = {str(entry['identifier']) for entry in data if isinstance(entry, dict) and isinstance(entry.get('identifier'), str)}
            dup_count = len([entry for entry in data if isinstance(entry, dict) and isinstance(entry.get('identifier'), str)]) - len(identifiers)
            if dup_count:
                missing_keys.append(f'{loc}:duplicate_identifiers:{dup_count}')
            if loc != 'en' and en_dot_keys:
                missing_from_en = sorted(en_dot_keys - identifiers)
                if missing_from_en:
                    sample = missing_from_en[:20]
                    missing_keys.append(f"{loc}:missing_{len(missing_from_en)}_dot_keys:{','.join(sample)}")
                    if len(missing_from_en) > 20:
                        warnings.append(f'{loc}.json missing {len(missing_from_en)} dot keys vs en.json (showing first 20)')
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
                return HealthCheckResult(self.name, HealthStatus.HEALTHY, f'Locale files exist, parse correctly, and contain all required keys. Warnings: {len(warnings)} translation mismatch(es) detected.', details={'warnings': warnings})
            return HealthCheckResult(self.name, status, 'Locale files are valid and contain all required keys.')
        details = {}
        if warnings:
            details['warnings'] = warnings
        return HealthCheckResult(self.name, status, '; '.join(issues), details=details or None)