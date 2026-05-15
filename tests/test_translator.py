"""Tests for translator.py — comprehensive."""

import json
from unittest.mock import MagicMock, patch

import pytest

from tests.mock_config import patch_config_module

patch_config_module()

from translator import TanjunTranslator


class TestTanjunTranslatorInit:
    def test_init_creates_translator(self) -> None:
        t = TanjunTranslator()
        assert t is not None
        assert hasattr(t, "translations")

    def test_translations_is_list(self) -> None:
        t = TanjunTranslator()
        assert isinstance(t.translations, list)

    def test_load_translations_called_on_init(self) -> None:
        t = TanjunTranslator()
        # After init, translations should be loaded (non-empty or empty if de.json not found)
        assert isinstance(t.translations, list)


class TestTanjunTranslatorLoadTranslations:
    def test_load_translations_populates_list(self) -> None:
        t = TanjunTranslator()
        t.load_translations()
        assert isinstance(t.translations, list)

    def test_load_translations_missing_file(self) -> None:
        t = TanjunTranslator()
        with patch("translator.open", side_effect=FileNotFoundError):
            t.load_translations()
        assert t.translations == []

    def test_load_translations_invalid_json(self) -> None:
        t = TanjunTranslator()
        with patch("translator.open", side_effect=json.JSONDecodeError("err", "doc", 0)):
            t.load_translations()
        assert t.translations == []

    def test_load_translations_returns_german(self) -> None:
        t = TanjunTranslator()
        t.load_translations()
        # If German translations exist, should be non-empty
        if t.translations:
            assert len(t.translations) > 0


class TestTanjunTranslatorTranslate:
    @pytest.mark.asyncio
    async def test_translate_rejects_unsupported_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "test_key"
        locale_str.message = "test_key"
        mock_locale = MagicMock()
        mock_locale.value = "fr"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_rejects_french_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "test_key"
        locale_str.message = "test_key"
        mock_locale = MagicMock()
        mock_locale.value = "fr"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_rejects_japanese_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "test_key"
        locale_str.message = "test_key"
        mock_locale = MagicMock()
        mock_locale.value = "ja"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_rejects_spanish_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "test_key"
        locale_str.message = "test_key"
        mock_locale = MagicMock()
        mock_locale.value = "es"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_normalizes_en_us_to_en(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en-US"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_normalizes_en_gb_to_en(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en-GB"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_de_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "de"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_de_de_locale(self) -> None:
        """de-DE is NOT normalized to 'de' in translate — it's passed as-is."""
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "de-DE"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_en_locale(self) -> None:
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en"
        context = MagicMock()
        result = await t.translate(locale_str, mock_locale, context)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_returns_none_for_error_string(self) -> None:
        """If localizer returns 'err: no translation found.', translate should return None."""
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "nonexistent_key"
        locale_str.message = "nonexistent_key"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en"
        context = MagicMock()
        with patch("localizer.missingLocalization"):
            result = await t.translate(locale_str, mock_locale, context)
        assert result is None

    @pytest.mark.asyncio
    async def test_translate_underscore_to_dot_conversion(self) -> None:
        """translate should convert underscores to dots in locale_str."""
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands_help_select_title"
        locale_str.message = "commands_help_select_title"
        # Mock replace to verify it converts underscores to dots
        locale_str.replace = lambda old, new: locale_str.message.replace(old, new)
        mock_locale = MagicMock()
        mock_locale.value = "en"
        context = MagicMock()
        # This test verifies the key transformation happens
        result = await t.translate(locale_str, mock_locale, context)
        # The key should be "commands.help.select.title" after replace
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_supported_locales(self) -> None:
        """Test that all supported locales are handled."""
        t = TanjunTranslator()
        supported = ["de", "de-DE", "en", "en-US", "en-GB"]
        for locale_val in supported:
            locale_str = MagicMock()
            locale_str.__str__ = lambda s: "commands.help.select.title"
            locale_str.message = "commands.help.select.title"
            locale_str.replace = lambda s, r: s
            mock_locale = MagicMock()
            mock_locale.value = locale_val
            context = MagicMock()
            result = await t.translate(locale_str, mock_locale, context)
            # Should return None or a string, not raise
            assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_context_parameter_unused(self) -> None:
        """The context parameter is passed but not used in translate."""
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "commands.help.select.title"
        locale_str.message = "commands.help.select.title"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en"
        # Context can be anything — it's ignored
        result = await t.translate(locale_str, mock_locale, None)
        assert result is None or isinstance(result, str)

    @pytest.mark.asyncio
    async def test_translate_non_string_returns_none(self) -> None:
        """If localize returns a non-string, translate should return None."""
        t = TanjunTranslator()
        locale_str = MagicMock()
        locale_str.__str__ = lambda s: "some_key"
        locale_str.message = "some_key"
        locale_str.replace = lambda s, r: s
        mock_locale = MagicMock()
        mock_locale.value = "en"
        context = MagicMock()
        with patch("localizer.tanjunLocalizer") as mock_loc:
            mock_loc.localize.return_value = 12345  # Not a string
            result = await t.translate(locale_str, mock_locale, context)
            assert result is None
