from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

import asyncio
import os
import sys
import tempfile
from pathlib import Path

import asyncmy  # type: ignore[import-not-found]
import discord
from discord.ext import commands

import config
from config import (
    database_ip,
    database_password,
    database_port,
    database_schema,
    database_user,
    prefix,
)
from DatabaseHealthCheck import DatabaseHealthCheck
from di import services
from external_api_health_checks import (
    BrawlStarsHealthCheck,
    BytebinHealthCheck,
    GIPHYHealthCheck,
    GitHubAPIHealthCheck,
    ImgBBHealthCheck,
)
from health.manager import HealthCheckManager
from locale_file_health_check import LocaleFileHealthCheck
from OpenAIHealthCheck import OpenAIHealthCheck
from translator import TanjunTranslator
from TwitchAPIHealthCheck import TwitchAPIHealthCheck

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


async def loadextension(bot: commands.AutoShardedBot, extensionname: str) -> None:
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        print(f"Failed to load extension {extensionname}")
        raise e


async def loadTranslator(bot: commands.AutoShardedBot) -> None:
    print("loading translator...")
    translator = TanjunTranslator()
    if bot.tree:  # type: ignore[truthy-bool]
        await bot.tree.set_translator(translator)
    print("translator loaded!")


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis_and_stickers = True
intents.voice_states = True
intents.messages = True
intents.typing = True
intents.message_content = True
intents.auto_moderation_configuration = True
intents.auto_moderation_execution = True
intents.invites = True
intents.presences = False

bot = commands.AutoShardedBot(prefix, intents=intents, application_id=config.applicationId)  # type: ignore[arg-type]


@bot.event
async def on_ready():
    Path(tempfile.gettempdir(), "bot_ready").touch()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))


async def _load_all_extensions(bot: commands.AutoShardedBot) -> None:
    """Load all extensions from the extensions directory."""
    for filename in os.listdir("extensions"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = filename.replace(".py", "")
            await loadextension(bot, extension)


async def _init_database_pool() -> asyncmy.Pool | None:
    """Initialize and return the database connection pool."""
    try:
        pool = await asyncmy.create_pool(
            host=database_ip,
            port=database_port,
            user=database_user,
            password=database_password,
            db=database_schema,
            maxsize=10,
            minsize=1,
        )
        print("Database pool initialized successfully!")
        return pool
    except Exception as e:
        print(f"Failed to initialize database pool: {e}")
        raise


async def main():
    print("starting bot...")
    print("discord.py version: ", discord.__version__)

    # Create pool-ready event before any tasks start
    # so LoopCog.on_ready can wait on it asyncio.Event-style instead of polling
    bot._pool_ready = asyncio.Event()

    # Step 1: Load extensions and initialize database pool in parallel.
    # Extensions don't need the DB at load time, so these are independent.
    ext_task = asyncio.create_task(_load_all_extensions(bot))
    pool_task = asyncio.create_task(_init_database_pool())

    # Wait for the pool first so we can start table creation while extensions finish.
    # Use fail-fast: if pool_task or ext_task raises, cancel the other.
    done, pending = await asyncio.wait(
        {ext_task, pool_task},
        return_when=asyncio.FIRST_EXCEPTION
    )

    # Check if any task raised an exception
    exception_to_raise = None
    for task in done:
        if task.exception() is not None:
            exception_to_raise = task.exception()
            # Cancel all pending tasks
            for ptask in pending:
                ptask.cancel()
            # Await pending tasks to propagate cancellations
            await asyncio.gather(*pending, return_exceptions=True)
            raise exception_to_raise

    # Both tasks completed successfully, extract pool result
    pool = pool_task.result()
    bot._pool = pool
    bot._pool_ready.set()  # Signal waiting tasks that pool is ready

    from api import set_bot

    set_bot(bot)

    # Populate DI container with core infrastructure.
    services.bot = bot
    services.pool = pool

    # Step 2: Create tables concurrently with remaining extension loading.
    from api import create_tables

    table_task = asyncio.create_task(create_tables(bot))

    # Wait for both ext_task and table_task with fail-fast behavior
    done, pending = await asyncio.wait(
        {ext_task, table_task},
        return_when=asyncio.FIRST_EXCEPTION
    )

    # Check if any task raised an exception
    for task in done:
        if task.exception() is not None:
            exception_to_raise = task.exception()
            # Cancel all pending tasks
            for ptask in pending:
                ptask.cancel()
            # Await pending tasks to propagate cancellations
            await asyncio.gather(*pending, return_exceptions=True)
            raise exception_to_raise

    # Step 3: Preload guild configs into cache to avoid cold-start latency.
    from api import preload_guild_configs

    await preload_guild_configs(bot)

    # Populate DI container with existing service singletons.
    from services.afk_service import afk_service
    from services.giveaway_service import giveaway_service
    from services.report_service import report_service
    from services.ticket_service import ticket_service
    from services.trigger_message_service import trigger_message_service
    from services.xp_calculator import xp_calculator

    services.afk_service = afk_service
    services.giveaway_service = giveaway_service
    services.report_service = report_service
    services.ticket_service = ticket_service
    services.trigger_message_service = trigger_message_service
    services.xp_calculator = xp_calculator

    # Step 3.5: Initialize Twitch service.
    from services.twitch_service import init_twitch_service

    await init_twitch_service()

    # Step 4: Load translator (depends on extensions being loaded for tree).
    await loadTranslator(bot)

    # Step 5: Run startup health checks.
    health_manager = HealthCheckManager(bot)
    health_manager.register(OpenAIHealthCheck())  # Uses default 5-minute interval
    health_manager.register(LocaleFileHealthCheck())  # Uses default 5-minute interval
    health_manager.register(DatabaseHealthCheck())  # Uses default 5-minute interval
    health_manager.register(TwitchAPIHealthCheck())  # Uses default 5-minute interval
    health_manager.register(OpenAIHealthCheck())  # Uses default 5-minute interval
    health_manager.register(GIPHYHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(BrawlStarsHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(ImgBBHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(BytebinHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(GitHubAPIHealthCheck(), interval=3600)  # 60 minutes
    health_manager.register(OpenAIHealthCheck())  # Uses default 5-minute interval
    health_manager.register(LocaleFileHealthCheck())  # Uses default 5-minute interval
    ok, critical_failures = await health_manager.run_startup_checks()
    if not ok:
        # Can't send Discord notification before login; log prominently instead.
        for result in critical_failures:
            print(f"  CRITICAL: [{result.check_name}] {result.message}")
        print("FATAL: Critical health checks failed. Bot cannot start.")
        return

    # Start periodic health checks
    asyncio.create_task(health_manager.start_periodic_checks(interval=300))

    # Step 6: Start the bot
    await bot.start(config.token)  # type: ignore[arg-type]


if __name__ == "__main__":
    asyncio.run(main())
