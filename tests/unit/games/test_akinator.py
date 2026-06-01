'Unit tests for akinator command locale mapping.'
from __future__ import annotations

from locale_keys import locale
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

def akinator_language(locale: str) -> str:
    if locale in ('en', 'en-US', 'en-GB'):
        return 'en'
    if locale == 'de':
        return 'de'
    if locale == 'ar':
        return 'ar'
    if locale in ('zh-CN', 'zh-TW'):
        return 'zh'
    if locale in ('es', 'es-ES', 'es-419'):
        return 'es'
    if locale == 'fr':
        return 'fr'
    if locale == 'he':
        return 'he'
    if locale == 'it':
        return 'it'
    if locale == 'ja':
        return 'jp'
    if locale == 'ko':
        return 'ko'
    if locale == 'nl':
        return 'nl'
    if locale == 'pl':
        return 'pl'
    if locale in ('pt-PT', 'pt', 'pt-BR'):
        return 'pt'
    if locale == 'ru':
        return 'ru'
    if locale == 'tr':
        return 'tr'
    if locale == 'id':
        return 'id'
    return 'en'

@pytest.mark.unit
class TestAkinatorLanguageMapping:

    @pytest.mark.parametrize(('locale', 'expected'), [('en-US', 'en'), ('de', 'de'), ('ja', 'jp'), ('zh-CN', 'zh'), ('pt-BR', 'pt'), ('unknown', 'en')])
    def test_locale_maps_to_akinator_lang(self, locale: str, expected: str):
        assert akinator_language(locale) == expected

@pytest.mark.unit
class TestAkinatorHypothesis:

    @given(locale=st.sampled_from(['en-US', 'de', 'fr', 'ja', 'ko', 'pt-BR', 'ru', 'xx']))
    @settings(max_examples=20)
    def test_mapping_always_returns_nonempty_string(self, locale: str):
        result = akinator_language(locale)
        assert isinstance(result, str)
        assert len(result) >= 2
