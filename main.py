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
from health.manager import HealthCheckManager
from OpenAIHealthCheck import OpenAIHealthCheck
from translator import TanjunTranslator

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


async def main():
    print("starting bot...")
    print("discord.py version: ", discord.__version__)

    # Load all extensions
    for filename in os.listdir("extensions"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = filename.replace(".py", "")
            await loadextension(bot, extension)

    # Load translator
    await loadTranslator(bot)

    # Initialize the database pool
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
        bot._pool = pool
        print("Database pool initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize database pool: {e}")
        raise

    from api import set_bot

    set_bot(bot)

    # Create database tables
    from api import create_tables

    await create_tables(bot)

    # Preload guild configs into cache to avoid cold-start latency
    from api import preload_guild_configs

    await preload_guild_configs(bot)

    # Run startup health checks
    health_manager = HealthCheckManager(bot)
    health_manager.register(OpenAIHealthCheck())
    health_manager.register(LocaleFileHealthCheck())
    ok, critical_failures = await health_manager.run_startup_checks()
    if not ok:
        # Can't send Discord notification before login; log prominently instead.
        for result in critical_failures:
            print(f"  CRITICAL: [{result.check_name}] {result.message}")
        print("FATAL: Critical health checks failed. Bot cannot start.")
        return

    # Start periodic health checks
    asyncio.create_task(health_manager.start_periodic_checks(interval=300))

    # Start the bot
    await bot.start(config.token)  # type: ignore[arg-type]


if __name__ == "__main__":
    asyncio.run(main())
