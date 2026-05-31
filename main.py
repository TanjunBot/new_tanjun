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
    database_connect_max_retries,
    database_connect_retry_delay_sec,
    database_connect_timeout_sec,
    database_ip,
    database_password,
    database_port,
    database_schema,
    database_user,
    prefix,
    sentry_dsn,
    sentry_environment,
    sentry_traces_sample_rate,
)


# ── Sentry event filter ──────────────────────────────────────────────────────
def _should_discard_sentry_event(event: dict, hint: dict) -> dict | None:
    """Drop noisy known-safe Discord API errors to save Sentry quota.

    Returns ``None`` to discard the event, or the ``event`` dict to send it.
    """
    exc_info = hint.get("exc_info")
    if exc_info is None:
        return event
    _exc_type, exc_value, _tb = exc_info

    # Discord HTTP 403 Forbidden — expected when the bot lacks a permission.
    if isinstance(exc_value, discord.Forbidden):
        return None

    # Discord HTTP 404 — Unknown Message, Unknown Interaction, etc.
    if isinstance(exc_value, discord.NotFound):
        return None

    # Discord HTTP 429 — rate-limited; logged locally, not actionable via Sentry.
    if isinstance(exc_value, discord.HTTPException):
        if exc_value.status in (429,):
            return None

    # Discord 10008 "Unknown Message" — common race when a message is deleted
    # between when a component interaction fires and the bot tries to respond.
    if isinstance(exc_value, discord.DiscordException):
        msg = str(exc_value).lower()
        if "10008" in msg and "unknown message" in msg:
            return None

    return event


# ── Sentry initialization (must be early) ────────────────────────────────────
if sentry_dsn:
    import sentry_sdk

    init_kwargs = {
        "dsn": sentry_dsn,
        "before_send": _should_discard_sentry_event,
        "traces_sample_rate": sentry_traces_sample_rate,
    }
    if sentry_environment:
        init_kwargs["environment"] = sentry_environment

    sentry_sdk.init(**init_kwargs)

from di import services
from health import (
    BrawlStarsHealthCheck,
    BytebinHealthCheck,
    DatabaseHealthCheck,
    GIPHYHealthCheck,
    GitHubAPIHealthCheck,
    ImgBBHealthCheck,
    LocaleFileHealthCheck,
    OpenRouterHealthCheck,
    TwitchAPIHealthCheck,
)
from health.manager import HealthCheckManager
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
async def on_ready() -> None:
    Path(tempfile.gettempdir(), "bot_ready").touch()
    user = bot.user
    if user is not None:
        print(f"Logged in as {user} (ID: {user.id})")
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))


async def _load_all_extensions(bot: commands.AutoShardedBot) -> None:
    """Load all extensions from the extensions directory."""
    for filename in os.listdir("extensions"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = filename.replace(".py", "")
            await loadextension(bot, extension)


def _database_connect_hint() -> str:
    if database_port == 3306:
        return ""
    return (
        f"\nHint: The bot is configured for port {database_port}. "
        "When the bot and MariaDB run in the same Docker network (e.g. Coolify), "
        "use the internal service hostname and port 3306, not the host-published port."
    )


async def _init_database_pool() -> asyncmy.Pool | None:
    """Initialize and return the database connection pool."""
    max_retries = database_connect_max_retries
    delay = database_connect_retry_delay_sec
    last_error: BaseException | None = None

    for attempt in range(1, max_retries + 1):
        try:
            pool = await asyncmy.create_pool(
                host=database_ip,
                port=database_port,
                user=database_user,
                password=database_password,
                db=database_schema,
                maxsize=20,
                minsize=1,
                connect_timeout=database_connect_timeout_sec,
            )
            print("Database pool initialized successfully!")
            return pool
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(
                    f"Failed to initialize database pool "
                    f"(attempt {attempt}/{max_retries}): {e}"
                )
                print(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print(f"Failed to initialize database pool after {max_retries} attempts: {e}")
                hint = _database_connect_hint()
                if hint:
                    print(hint, file=sys.stderr)
                raise last_error from e

    raise RuntimeError("Database pool initialization failed with no exception")


async def main() -> None:
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
    done, pending = await asyncio.wait({ext_task, pool_task}, return_when=asyncio.FIRST_EXCEPTION)

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
            if exception_to_raise is not None:
                raise exception_to_raise
            raise RuntimeError("A task failed with no exception information")

    # Both tasks completed successfully, extract pool result
    pool = pool_task.result()
    bot._pool = pool
    bot._pool_ready.set()  # Signal waiting tasks that pool is ready

    from api import db_manager

    db_manager.set_pool(pool)

    from api import set_bot

    set_bot(bot)

    # Populate DI container with core infrastructure.
    services.bot = bot
    services.pool = pool
    services.db_manager = db_manager

    # Step 2: Create tables concurrently with remaining extension loading.
    from api import create_tables

    table_task = asyncio.create_task(create_tables(bot))

    # Wait for both ext_task and table_task with fail-fast behavior
    done, pending = await asyncio.wait({ext_task, table_task}, return_when=asyncio.FIRST_EXCEPTION)

    # Check if any task raised an exception
    for task in done:
        if task.exception() is not None:
            exception_to_raise = task.exception()
            # Cancel all pending tasks
            for ptask in pending:
                ptask.cancel()
            # Await pending tasks to propagate cancellations
            await asyncio.gather(*pending, return_exceptions=True)
            if exception_to_raise is not None:
                raise exception_to_raise
            raise RuntimeError("A task failed with no exception information")

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
    health_manager.register(OpenRouterHealthCheck())
    health_manager.register(LocaleFileHealthCheck())  # Uses default 5-minute interval
    health_manager.register(DatabaseHealthCheck())  # Uses default 5-minute interval
    health_manager.register(TwitchAPIHealthCheck())  # Uses default 5-minute interval
    health_manager.register(GIPHYHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(BrawlStarsHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(ImgBBHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(BytebinHealthCheck(), interval=1800)  # 30 minutes
    health_manager.register(GitHubAPIHealthCheck(), interval=3600)  # 60 minutes
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
