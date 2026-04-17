from __future__ import annotations

import asyncio
import os
import sys
from typing import cast

# import asyncmy  # type: ignore[import-not-found]
import discord
from discord.ext import commands

import config
from config import (
    database_ip,
    database_password,
    database_schema,
    database_user,
    prefix,
)
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


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))


if __name__ == "__main__":

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

        # Start the bot
        await bot.start(config.token)  # type: ignore[arg-type]

    asyncio.run(main())
