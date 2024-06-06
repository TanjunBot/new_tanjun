import discord
from discord.ext import commands
import os 
import asyncio
import config

async def loadextension(bot, extensionname):
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        print(f"Failed to load extension {extensionname}")
        raise

bot = commands.Bot("t.", intents=discord.Intents.all(),
                   application_id=config.applicationId)

if __name__ == "__main__":
    print("starting bot...")
    print("discord.py version: ", discord.__version__)
    for extension in os.listdir(os.fsencode("extensions")):
        if os.fsdecode(extension).endswith(".py"):
            extension = os.fsdecode(extension).replace(".py", "")
            asyncio.run(loadextension(bot, extension))

@bot.event
async def on_ready():
    print("Bot is running!")
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))

bot.run(config.token)