"""Tests for locale_keys.nav module."""
from __future__ import annotations

import pytest

from locale_keys.nav import at, field_name


class TestFieldName:
    def test_simple_identifier(self) -> None:
        """Standard dot-separated path segments."""
        assert field_name("hello") == "hello"
        assert field_name("helloWorld") == "helloWorld"
        assert field_name("_hello") == "_hello"

    def test_quoted_identifier(self) -> None:
        """Quoted segments that are valid identifiers."""
        assert field_name('"hello"') == "hello"

    def test_non_identifier_characters(self) -> None:
        """Segments with special characters get underscores."""
        result = field_name("hello-world")
        assert result == "hello_world"
        assert _is_valid_identifier(result)

    def test_empty_segment_defaults_to_key(self) -> None:
        """An empty segment gets 'key'."""
        result = field_name("")
        assert result == "key"

    def test_digit_prefix_gets_underscore(self) -> None:
        """A segment starting with a digit gets an underscore prefix."""
        result = field_name("123abc")
        assert result == "_123abc"

    def test_keyword_becomes_keyword_underscore(self) -> None:
        """Python keywords get an underscore suffix."""
        result = field_name("for")
        assert result == "for_"
        result = field_name("class")
        assert result == "class_"
        result = field_name("in")
        assert result == "in_"


class TestAt:
    def test_simple_path(self) -> None:
        """at resolves a dotted path to a locale node."""
        result = at("admin.name")
        # The root.admin.name should exist as a LocalizedString
        assert result is not None

    def test_nested_path(self) -> None:
        """at resolves deeper paths."""
        result = at("admin.addrole.name")
        assert result is not None


def _is_valid_identifier(s: str) -> bool:
    return s.isidentifier()


def test_invite_target_embedded_application_resolve() -> None:
    from locale_keys import locale as l10n

    res = l10n.logs.inviteCreate.targetTypeLocales.resolve("InviteTarget.embedded_application")
    assert res.key == "logs.inviteCreate.targetTypeLocales.InviteTarget.embedded_application"
    text = res("en")
    assert "embedded application" in text.lower()
