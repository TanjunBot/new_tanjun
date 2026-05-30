"""Tests for services.openrouter_client."""

from __future__ import annotations

from unittest.mock import patch


class TestOpenRouterClient:
    def test_reads_key_from_config(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("services.openrouter_client.OPENROUTER_API_KEY", "config-key"):
            from services.openrouter_client import get_openrouter_api_key

            assert get_openrouter_api_key() == "config-key"

    def test_falls_back_to_env(self, monkeypatch):
        with patch("services.openrouter_client.OPENROUTER_API_KEY", ""):
            monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
            from services.openrouter_client import get_openrouter_api_key

            assert get_openrouter_api_key() == "env-key"

    def test_client_none_without_key(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("services.openrouter_client.OPENROUTER_API_KEY", ""):
            from services.openrouter_client import get_openrouter_client

            assert get_openrouter_client() is None

    def test_client_created_with_key(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        with patch("services.openrouter_client.OPENROUTER_API_KEY", "test-key"):
            from services.openrouter_client import get_openrouter_client

            client = get_openrouter_client()
            assert client is not None
            assert client.api_key == "test-key"
            assert str(client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"

    def test_default_model(self, monkeypatch):
        monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
        with patch("services.openrouter_client.OPENROUTER_MODEL", "custom/model:free"):
            from services.openrouter_client import get_openrouter_model

            assert get_openrouter_model() == "custom/model:free"
