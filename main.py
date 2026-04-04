import asyncio
import os
from typing import cast

import asyncmy  # type: ignore[import-not-found]
import discord  # type: ignore[import-not-found]
from discord.ext import commands  # type: ignore[import-not-found]

import api
import config
from commands.utility.twitch.twitchApi import initTwitch
from config import (
    database_ip,
    database_password,
    database_schema,
    database_user,
    prefix,
)
from translator import TanjunTranslator


async def loadextension(bot: commands.AutoShardedBot, extensionname: str) -> None:  # type: ignore[no-any-unimported]
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        print(f"Failed to load extension {extensionname}")
        raise e


async def loadTranslator(bot: commands.AutoShardedBot) -> None:  # type: ignore[no-any-unimported]
    print("loading translator...")
    translator = TanjunTranslator()
    if bot.tree:
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

bot = commands.AutoShardedBot(prefix, intents=intents, application_id=config.applicationId)


async def main() -> None:
    print("starting bot...")
    print("discord.py version: ", discord.__version__)
    for filename in os.listdir("extensions"):
        if filename.endswith(".py") and not filename.startswith("__"):
            extension = filename.replace(".py", "")
            await loadextension(bot, extension)
    await loadTranslator(bot)


async def create_pool() -> asyncmy.Connection | None:  # type: ignore[no-any-unimported]
    try:
        # p = await asyncmy.create_pool(
        #     host=database_ip,
        #     user=database_user,
        #     password=database_password,
        #     db=database_schema,
        #     maxsize=1,
        #     minsize=1,
        # )
        # return p
        connection = await asyncmy.connect(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
        )
        return cast(asyncmy.Connection, connection)  # type: ignore[no-any-unimported]
    except Exception as e:
        print(f"Error creating pool: {e}")
        return None


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


@bot.event  # type: ignore[untyped-decorator]
async def on_ready() -> None:  # type: ignore[misc]
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))
    pool = await create_pool()
    print(pool)
    if pool:
        api.set_pool(pool)
    await api.create_tables()
    await initTwitch()
    print("Bot is running!")


bot.run(config.token)
