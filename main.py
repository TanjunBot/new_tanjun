import discord
from discord.ext import commands
import os 
import asyncio
import config
from translator import TanjunTranslator
import api

async def loadextension(bot, extensionname):
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        print(f"Failed to load extension {extensionname}")
        raise

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
intents.presences = False

bot = commands.Bot("t.", intents=intents,
                   application_id=config.applicationId)

if __name__ == "__main__":
    print("starting bot...")
    print("discord.py version: ", discord.__version__)
    api.create_tables()
    for extension in os.listdir(os.fsencode("extensions")):
        if os.fsdecode(extension).endswith(".py"):
            extension = os.fsdecode(extension).replace(".py", "")
            asyncio.run(loadextension(bot, extension))
    asyncio.run(loadTranslator(bot))

@bot.event
async def on_ready():
    print("Bot is running!")
    await bot.change_presence(activity=discord.Game(name=config.activity.format(version=config.version)))

bot.run(config.token)