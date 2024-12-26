import discord
from discord.ext import commands
import os
import asyncio
import config
from translator import TanjunTranslator
import api
import asyncmy
from config import database_ip, database_password, database_user, database_schema
from commands.utility.twitch.twitchApi import initTwitch


async def loadextension(bot, extensionname):
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        raise e
        print(f"Failed to load extension {extensionname}")


async def loadTranslator(bot):
    print("loading translator...")
    translator = TanjunTranslator()
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

bot = commands.AutoShardedBot(
    "t.", intents=intents, application_id=config.applicationId
)


async def main():
    print("starting bot...")
    print("discord.py version: ", discord.__version__)
    for extension in os.listdir(os.fsencode("extensions")):
        if os.fsdecode(extension).endswith(".py"):
            extension = os.fsdecode(extension).replace(".py", "")
            await loadextension(bot, extension)
    await loadTranslator(bot)


async def create_pool():
    try:
        p = await asyncmy.create_pool(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
            maxsize=1,
            minsize=1,
        )
        return p
    except Exception as e:
        print(f"Error creating pool: {e}")
        return None


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name=config.activity.format(version=config.version))
    )
    pool = await create_pool()
    print(pool)
    api.set_pool(pool)
    await api.create_tables()
    await initTwitch()
    print("Bot is running!")


bot.run(config.token)
