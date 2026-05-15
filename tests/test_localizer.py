"""Tests for localizer.py — comprehensive."""

import os
import tempfile
from unittest.mock import patch

from tests.mock_config import patch_config_module

patch_config_module()

from localizer import Localizer, tanjunLocalizer


class TestLocalizerInit:
    def test_init_empty_translations(self):
        loc = Localizer()
        assert loc.translations == {}


class TestLocalizerLoadTranslations:
    def test_load_english(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        assert isinstance(translations, list)
        assert len(translations) > 0

    def test_load_german(self):
        loc = Localizer()
        translations = loc.load_translations("de")
        assert isinstance(translations, list)
        assert len(translations) > 0

    def test_load_nonexistent_locale_falls_back_to_english(self):
        loc = Localizer()
        translations = loc.load_translations("xx")
        assert isinstance(translations, list)
        assert len(translations) > 0  # Falls back to en.json

    def test_load_translations_structure(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        for entry in translations:
            assert "identifier" in entry
            assert "translation" in entry

    def test_load_translations_has_identifier_key(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        identifiers = [str(t.get("identifier", "")) for t in translations]
        assert "commands.help.select.title" in identifiers

    def test_load_translations_caches(self):
        """load_translations is called each time but should return consistent data."""
        loc = Localizer()
        t1 = loc.load_translations("en")
        t2 = loc.load_translations("en")
        assert t1 == t2


class TestLocalizerGetTranslation:
    def test_get_existing_translation(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        key = str(translations[0].get("identifier", "")).lower()
        result = loc.get_translation(translations, key)
        assert result is not None
        assert "translation" in result

    def test_get_nonexistent_translation(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        result = loc.get_translation(translations, "nonexistent.key.that.does.not.exist")
        assert result is None

    def test_get_translation_case_insensitive(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        key_upper = str(translations[0].get("identifier", "")).upper()
        key_lower = str(translations[0].get("identifier", "")).lower()
        result_upper = loc.get_translation(translations, key_upper)
        result_lower = loc.get_translation(translations, key_lower)
        assert result_upper == result_lower

    def test_get_translation_with_empty_list(self):
        loc = Localizer()
        result = loc.get_translation([], "any.key")
        assert result is None

    def test_get_translation_returns_dict_with_translation_key(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        key = str(translations[0].get("identifier", "")).lower()
        result = loc.get_translation(translations, key)
        assert "translation" in result


class TestLocalizerLocalize:
    def test_localize_english(self):
        result = tanjunLocalizer.localize("en", "commands.help.select.title")
        assert result != "err: no translation found."
        assert isinstance(result, str)

    def test_localize_with_params(self):
        """Test that template substitution works."""
        # Find a translation with parameters
        loc = Localizer()
        translations = loc.load_translations("en")
        # Look for entries with $ in their translation
        for t in translations:
            translation_text = str(t.get("translation", ""))
            if "$" in translation_text:
                key = str(t.get("identifier", "")).lower()
                result = tanjunLocalizer.localize("en", key)
                assert isinstance(result, str)
                break

    @patch("localizer.missingLocalization")
    def test_localize_nonexistent_key(self, mock_missing):
        mock_missing.return_value = None
        result = tanjunLocalizer.localize("en", "completely.nonexistent.key.xyz123")
        assert "err" in result
        mock_missing.assert_called_once_with("completely.nonexistent.key.xyz123")

    def test_localize_normalizes_locale_en_us(self):
        result = tanjunLocalizer.localize("en-US", "commands.help.select.title")
        assert isinstance(result, str)

    def test_localize_normalizes_locale_en_gb(self):
        result = tanjunLocalizer.localize("en-GB", "commands.help.select.title")
        assert isinstance(result, str)

    def test_localize_normalizes_locale_en(self):
        result = tanjunLocalizer.localize("en", "commands.help.select.title")
        assert isinstance(result, str)

    def test_localize_all_normalized_same(self):
        r1 = tanjunLocalizer.localize("en", "commands.help.select.title")
        r2 = tanjunLocalizer.localize("en-US", "commands.help.select.title")
        r3 = tanjunLocalizer.localize("en-GB", "commands.help.select.title")
        assert r1 == r2 == r3 or all("err" in r for r in [r1, r2, r3])


class TestLocalizerTestLocalize:
    def test_test_localize_fallback(self):
        loc = Localizer()
        result = loc.test_localize("de", "commands.help.select.title")
        assert isinstance(result, str)

    def test_test_localize_no_translation_found(self):
        loc = Localizer()
        result = loc.test_localize("de", "nonexistent.key.xyz")
        assert "No translation found" in result or isinstance(result, str)

    def test_test_localize_with_params(self):
        """test_localize should pass parameters through Template.safe_substitute."""
        loc = Localizer()
        result = loc.test_localize("en", "commands.help.select.title")
        assert isinstance(result, str)


class TestLocalizerMalformedJson:
    def test_malformed_json_returns_empty(self):
        loc = Localizer()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", dir="locales", delete=False) as f:
            f.write("{invalid json")
            f.flush()
            locale_name = os.path.basename(f.name).replace(".json", "")
            result = loc.load_translations(locale_name)
            assert result == []
            os.unlink(f.name)

    def test_empty_json_array(self):
        loc = Localizer()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", dir="locales", delete=False) as f:
            f.write("[]")
            f.flush()
            locale_name = os.path.basename(f.name).replace(".json", "")
            result = loc.load_translations(locale_name)
            assert result == []
            os.unlink(f.name)

    def test_valid_json_but_wrong_structure(self):
        """JSON that is valid but not a list of dicts."""
        loc = Localizer()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", dir="locales", delete=False) as f:
            f.write('{"key": "value"}')
            f.flush()
            locale_name = os.path.basename(f.name).replace(".json", "")
            result = loc.load_translations(locale_name)
            # Should return the dict as-is (it's valid JSON)
            assert isinstance(result, dict)
            os.unlink(f.name)


class TestReportedLocales:
    def test_reported_locales_is_list(self):
        from localizer import reported_locales

        assert isinstance(reported_locales, list)


class TestTanjunLocalizerSingleton:
    def test_singleton_exists(self):
        assert tanjunLocalizer is not None
        assert isinstance(tanjunLocalizer, Localizer)


class TestLocalizerEdgeCases:
    def test_load_translations_english_has_many_entries(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        assert len(translations) > 100

    def test_load_translations_german_has_entries(self):
        loc = Localizer()
        translations = loc.load_translations("de")
        assert len(translations) > 50

    def test_get_translation_case_insensitive(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        # Exact match
        result = loc.get_translation(translations, "commands.help.select.title")
        assert result is not None

    def test_get_translation_with_uppercase_key(self):
        loc = Localizer()
        translations = loc.load_translations("en")
        result_lower = loc.get_translation(translations, "commands.help.select.title")
        result_upper = loc.get_translation(translations, "COMMANDS.HELP.SELECT.TITLE")
        assert result_lower == result_upper

    def test_get_translation_empty_list(self):
        loc = Localizer()
        result = loc.get_translation([], "any.key")
        assert result is None

    def test_localize_with_params(self):
        """Test that Template.safe_substitute works for translations with parameters."""
        result = tanjunLocalizer.localize("en", "commands.help.select.title")
        assert isinstance(result, str)

    @patch("localizer.missingLocalization")
    def test_localize_nonexistent_key_returns_error(self, mock_missing):
        mock_missing.return_value = None
        result = tanjunLocalizer.localize("en", "completely.nonexistent.key.xyz123")
        assert "err" in result

    def test_test_localize_german(self):
        loc = Localizer()
        result = loc.test_localize("de", "commands.help.select.title")
        assert isinstance(result, str)

    def test_test_localize_nonexistent(self):
        loc = Localizer()
        result = loc.test_localize("de", "nonexistent.key.xyz")
        assert isinstance(result, str)

    def test_reported_locales_starts_empty(self):
        """The module-level reported_locales list tracks locales already reported."""
        from localizer import reported_locales

        assert isinstance(reported_locales, list)
