from __future__ import annotations

from unittest.mock import patch

from diagnostics.locale_checks import check_locale_files, check_localizer_samples


def test_check_locale_files_finds_json() -> None:
    outcomes = check_locale_files()
    assert outcomes
    assert all(o.passed for o in outcomes)


def test_check_localizer_samples() -> None:
    outcomes = check_localizer_samples("en")
    assert outcomes
    assert all(o.passed for o in outcomes)


def test_check_localizer_samples_missing_key() -> None:
    with patch("localizer.tanjunLocalizer.localize", return_value="err: no translation found."):
        outcomes = check_localizer_samples("en")
    assert any(not o.passed for o in outcomes)
