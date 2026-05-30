"""Dependency injection container: Replace globals with a centralized DI system.

Usage:
    from di import services
    await services.giveaway_service.get(...)
"""

from __future__ import annotations

import asyncmy
from discord.ext import commands

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from api import DatabaseManager
from services.afk_service import AfkService
from services.ai_service import AiService
from services.counting_repository import CountingRepository
from services.dynamicslowmode import DynamicSlowmodeService
from services.giveaway_service import GiveawayService
from services.report_service import ReportService
from services.scheduled_message_service import ScheduledMessageService
from services.ticket_service import TicketService
from services.trigger_message_service import TriggerMessageService
from services.xp_calculator import XpCalculator


class BotServices(BaseModel):
    """Central DI container for all bot services.

    This container is populated in main.py and then passed to extensions
    that need typed access to services. Each field is optional (None by default)
    so the container can be built incrementally — add a service when it has been
    refactored away from module-level globals.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, defer_build=True)

    # ── Core infrastructure ──────────────────────────────────────────────
    bot: commands.AutoShardedBot | None = None
    pool: asyncmy.Pool | None = None
    db_manager: DatabaseManager | None = None

    # ── Services ─────────────────────────────────────────────────────────
    afk_service: AfkService | None = None
    ai_service: AiService | None = None
    counting_repository: CountingRepository | None = None
    dynamic_slowmode_service: DynamicSlowmodeService | None = None
    giveaway_service: GiveawayService | None = None
    report_service: ReportService | None = None
    scheduled_message_service: ScheduledMessageService | None = None
    ticket_service: TicketService | None = None
    trigger_message_service: TriggerMessageService | None = None
    xp_calculator: XpCalculator | None = None


BotServices.model_rebuild()

# Module-level singleton — populated by main.py once all services are initialized.
services: BotServices = BotServices()
