"""Tests for di.py dependency injection container."""

from __future__ import annotations

from unittest.mock import MagicMock

from di import BotServices, services
from services.xp_calculator import XpCalculator


class TestBotServices:
    def test_default_all_none(self):
        container = BotServices()
        assert container.bot is None
        assert container.pool is None
        assert container.giveaway_service is None
        assert container.xp_calculator is None

    def test_can_set_services(self):
        calc = MagicMock(spec=XpCalculator)
        container = BotServices(xp_calculator=calc)
        assert container.xp_calculator is calc

    def test_arbitrary_types_allowed(self):
        bot = MagicMock()
        container = BotServices(bot=bot)
        assert container.bot is bot

    def test_all_service_fields_exist(self):
        container = BotServices()
        for field in (
            "afk_service",
            "ai_service",
            "counting_repository",
            "dynamic_slowmode_service",
            "giveaway_service",
            "report_service",
            "scheduled_message_service",
            "ticket_service",
            "trigger_message_service",
            "xp_calculator",
            "db_manager",
        ):
            assert hasattr(container, field)

    def test_module_singleton_is_bot_services(self):
        assert isinstance(services, BotServices)

    def test_module_singleton_mutable(self):
        mock_calc = MagicMock()
        original = services.xp_calculator
        try:
            services.xp_calculator = mock_calc
            assert services.xp_calculator is mock_calc
        finally:
            services.xp_calculator = original
