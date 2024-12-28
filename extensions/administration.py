"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""

# Unused imports:
# import asyncio
# import subprocess
# import platform
import discord
from discord.ext import commands
from localizer import tanjunLocalizer
import config
from utility import addFeedback, tanjunEmbed, missingLocalization
from api import feedbackBlockUser, feedbackUnblockUser
from tests import (
    test_ping,
    test_database,
    test_commands,
)
from extensions.logs import sendLogEmbeds
from loops.create_database_backup import create_database_backup
from commands.admin.joinToCreate.joinToCreateListener import (
    removeAllJoinToCreateChannels,
)
import aiohttp
from commands.channel.welcome import welcomeNewUser

from commands.channel.farewell import farewellUser
import json
import asyncio


class administrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        if ctx.author.id not in config.adminIds:
            return
        fmt = await ctx.bot.tree.sync()
        await ctx.send(f"{len(fmt)} Befehle wurden gesynced.")

    @commands.command()
    async def feedback(self, ctx, *, content) -> None:
        if ctx.author.id not in [
            689755528947433555,
            892113092387942420,
            806086469268668437,
        ]:
            return
        addFeedback(content, ctx.author.name)
        await ctx.send("Feedback wurde hinzugefügt. Vielen dank!")

    @commands.command()
    async def blockFeedback(self, ctx, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackBlockUser(user.id)
        await ctx.send(f"{user.name} wurde blockiert.")

    @commands.command()
    async def unblockFeedback(self, ctx, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackUnblockUser(user.id)
        await ctx.send(f"{user.name} wurde entblockiert.")

    @commands.command()
    async def test_bot(self, ctx):
        if ctx.author.id not in config.adminIds:
            return

        message = await ctx.send("Starting bot tests...")

        await message.edit(content="Starting bot tests... \ncurrent Test: `Ping`")
        try:
            await test_ping(self, ctx)
        except Exception as e:
            await message.edit(content=f"❌ Error in Ping test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\ncurrent Test: `Database`"
        )
        try:
            await test_database(self, ctx)
        except Exception as e:
            await message.edit(content=f"❌ Error in Database test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\nDatabase Test: ✅\ncurrent Test: `Commands`"
        )
        try:
            await test_commands(self, ctx)
        except Exception as e:
            await message.edit(content=f"❌ Error in Commands test: {e}")
            return
        await message.edit(
            content="Starting bot tests... \nPing Test: ✅\nDatabase Test: ✅\nCommands Test: ✅\nAll tests completed successfully. The bot seems to be working fine."
        )

    @commands.command()
    async def test_translation(self, ctx):
        if ctx.author.id not in config.adminIds:
            return
        text = tanjunLocalizer.test_localize("de", "commands.logs")
        await ctx.send(str(text)[:4000])

    @commands.command()
    async def update(self, ctx):
        if ctx.author.id not in config.adminIds:
            return

        await sendLogEmbeds(self.bot)
        await create_database_backup(self.bot)
        await removeAllJoinToCreateChannels()
        await ctx.send("Updating...")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://127.0.0.1:6969/restart/{self.bot.application_id}"
            ) as response:
                await ctx.send(await response.text())

    @commands.command()
    async def welcome(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await welcomeNewUser(user)

    @commands.command()
    async def farewell(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await farewellUser(user)

    @commands.command()
    async def onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus(
        self, ctx
    ):
        if ctx.author.id not in config.adminIds:
            return
        emoji = ctx.bot.get_emoji(1266369876524666920)
        await ctx.send(
            f"{emoji} One thing about me ich fahr Auto seit vier Jahn'. Eines Tages woll ich in den Club Fahrn'. Ich stand an einer roten Ampel und ich war ganz allein, hinter mir war ein bus, und er fier mir rein. Er hupte mich an HUP HUP und ich stieg aus, schau mir an was passiert ist und er kommt raus."
        )

    async def getBrawlers(self):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.brawlstarsToken}"}
            async with session.get(
                "https://api.brawlstars.com/v1/brawlers", headers=headers
            ) as response:
                return await response.json()

    @commands.command()
    async def bsstarpoweremojis(self, ctx, start: int = 0):
        if ctx.author.id not in config.adminIds:
            return
        allBrawlers = await self.getBrawlers()
        for i, brawler in enumerate(allBrawlers["items"]):
            if i < start:
                continue
            starPowers = brawler["starPowers"]
            for starPower in starPowers:
                url = f"https://cdn.brawlify.com/star-powers/borderless/{starPower['id']}.png"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(
                            name=f"{starPower['id']}", image=image
                        )
                        await ctx.send(f"{emoji} {starPower['name']}; i:{i}")

    @commands.command()
    async def bsgadgetsemojis(self, ctx, start: int = 0):
        if ctx.author.id not in config.adminIds:
            return
        allBrawlers = await self.getBrawlers()
        for i, brawler in enumerate(allBrawlers["items"]):
            if i < start:
                continue
            gadgets = brawler["gadgets"]
            for gadget in gadgets:
                url = f"https://cdn.brawlify.com/gadgets/borderless/{gadget['id']}.png"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(
                            name=f"{gadget['id']}", image=image
                        )

                        await ctx.send(f"{emoji} {gadget['name']}; i:{i}")

    async def getAccData(self, id: str):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.brawlstarsToken}"}
            async with session.get(
                f"https://api.brawlstars.com/v1/players/%23{id}", headers=headers
            ) as response:
                return await response.json()

    @commands.command()
    async def bsaccdata(self, ctx, id: str):
        if ctx.author.id not in config.adminIds:
            return
        accData = await self.getAccData(id)
        accData["brawlers"] = accData["brawlers"][1]
        await ctx.send(f"```json\n{(json.dumps(accData, indent=4))[0:1900]}\n```")

    @commands.command()
    async def editembedmessage(self, ctx):
        if ctx.author.id not in config.adminIds:
            return
        message = await ctx.send(
            embed=tanjunEmbed(title="test", description="test. I will edit this soon..")
        )
        await asyncio.sleep(2)
        await message.edit(
            embed=tanjunEmbed(title="test2", description="test2. I have edited this!")
        )

    @commands.command()
    async def setguildlocale(self, ctx, locale: str):
        if ctx.author.id not in config.adminIds:
            return
        await ctx.guild.edit(preferred_locale=locale)
        await ctx.send(f"The guild locale has been set to {locale}")

    @commands.command()
    async def testgithubauthtoken(self, ctx):
        if ctx.author.id not in config.adminIds:
            return
        missingLocalization("JUSTATEST.IGNORETHIS.JUSTATEST")
        await ctx.send("jup gemacht :)")


async def setup(bot):
    await bot.add_cog(administrationCog(bot))
