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
from minigames.addLevelXp import update_user_roles
from minigames.countingmodes import get_correct_next_number, get_first_number


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

    @commands.command()
    async def testupdateuserroles(self, ctx):
        if ctx.author.id not in config.adminIds:
            return
        await update_user_roles(ctx.message, 10, str(ctx.guild.id))

    @commands.command()
    async def testgetcorrectnextnumber(self, ctx, mode: int, numbers: int):
        if ctx.author.id not in config.adminIds:
            return
        await ctx.send("look in the console")
        current_correct_number = get_first_number(mode)
        for i in range(numbers):
            print(f"i: {i}, current_correct_number: {current_correct_number}")
            current_correct_number = get_correct_next_number(
                mode, current_correct_number
            )

    @commands.command()
    async def sendUpdateTextToAllAdmins(self, ctx):
        if ctx.author.id not in config.adminIds:
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            await ctx.channel.send(
                "Willst du wirklich die Update-Text an alle Admins senden? (y/n)\nWenn du das startest kannst du das nicht mehr abbrechen! Es wird eiene Nachricht an ganz viele Menschen gesendet!"
            )
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send(
                "Wirklich wirklich wirklich ganz ganz ganz ganz ganz sicher? (y/n)"
            )
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send("sag wallah.")
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "wallah":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send("Gebe das geheime geheim passwort ein.")
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "passwort":
            await ctx.channel.send("Falsches Passwort!")
            return

        message = """
<:info:1323229608379682826>Du erhältst diese Nachricht, weil dir ein Server gehört, auf dem <@885984139315122206> verwendet wird. Keine Sorge – du wirst keine nervige Werbung per DM erhalten. Dies ist eine einmalige Nachricht, die wir aufgrund einer wichtigen Ankündigung an alle Serveradministratoren schreiben.

Tanjun 1.0
TL;DR:
Wir haben Tanjun komplett überarbeitet, sodass er jetzt wesentlich besser läuft. Konfiguriere die Einstellungen, die du auf deinem Server nutzen möchtest, neu, damit Tanjun weiterhin reibungslos funktioniert. @entcheneric kann dir bei der Konfiguration helfen.

Nach vielen Monaten harter Arbeit ist es endlich so weit: Tanjun 1.0 ist fertig!
Falls du es nicht mitbekommen hast, hier eine kurze Erklärung:
Wir haben uns vor einer Weile dazu entschieden, Tanjun von Grund auf neu zu programmieren. Der Hauptgrund dafür war veralteter, inzwischen schwer zu pflegender Code in der vorherigen Version. Deshalb erschien es uns einfacher, einmal von neu zu beginnen.

Da die interne Funktionsweise von Tanjun grundlegend überarbeitet und verbessert wurde, sind allerdings alte Konfigurationen nicht mehr kompatibel, weshalb du die Einstellungen des Bots einmal neu vornehmen musst. Am besten klickst du dich hierfür einmal Schritt für Schritt durch unsere ebenfalls überarbeitete [Dokumentation](https://app.gitbook.com/o/U7ew1TeWd8WAWHGeDLLf/s/kxqAE1ifXfn1iwkp233g/~/changes/123/tanjun-plus-und-pro), dann sollte die Neukonfiguration relativ einfach erledigt sein.

Solltest du Funktionen von Tanjun genutzt haben, mit denen eine größere Menge an Daten gespeichert wurde (z.B. das Levelsystem), kannst du mir, @entcheneric, eine DM schreiben. Ich werde mein Bestes tun, um so viele Daten wie möglich wiederherzustellen.

Entschuldigung für die verlorenen Einstellungen
Es tut uns als Tanjun-Team sehr leid, dass wir die alten Daten nicht migrieren konnten. Eine Datenübertragung hätte jedoch einen enormen Aufwand bedeutet, da alles manuell hätte übertragen werden müssen. Als Entschuldigung gibt es für jeden Server bis zum 1. März 2025 kostenlos das Tanjun Pro-Abonnement. Außerdem erhält jeder Nutzer bis zu diesem Datum das Tanjun Plus-Abonnement kostenlos. Ab dem 1. März 2025 werden beide Abonnements dann als kostenpflichtige Optionen verfügbar sein.

Abonnements? Gibt es eine Paywall für Tanjun?
Nein, ganz im Gegenteil! Wir hassen Paywalls und Abonnements genauso wie du. Unser Ziel ist es, Tanjun für alle zugänglich zu machen, mit diversen Funktionen und ohne Einschränkungen. Tanjun erzeugt aber auch Betriebskosten und andere laufende Ausgaben, und die Arbeit an Tanjun ist ein Vollzeitjob. Deshalb freuen wir uns über jede Unterstützung. Tanjun weiterhin kostenlos zu nutzen, ist natürlich auch kein Problem!

Um mehr über Tanjun Pro und Tanjun Plus zu erfahren, erfährst du [hier](https://app.gitbook.com/o/U7ew1TeWd8WAWHGeDLLf/s/kxqAE1ifXfn1iwkp233g/docs/tanjun-plus-und-pro) genauere Details und Vorteile.

Vielen Dank, dass du Tanjun nutzt!

Liebe Grüße,
Das Tanjun-Team
@entcheneric, @arion2000 und @.pegi
                    """

        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue

            try:
                await owner.send(
                    embed=tanjunEmbed(
                        title="Tanjun Update",
                        description=message,
                    )
                )
            except Exception:
                pass

    @commands.command()
    async def sendDemoIsNoMoreToAllAdmins(self, ctx):
        if ctx.author.id not in config.adminIds:
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            await ctx.channel.send(
                "Willst du wirklich die Demo Dankes Nachricht an alle Admins senden? (y/n)\nWenn du das startest kannst du das nicht mehr abbrechen! Es wird eiene Nachricht an ganz viele Menschen gesendet!"
            )
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send(
                "Wirklich wirklich wirklich ganz ganz ganz ganz ganz sicher? (y/n)"
            )
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send("sag wallah.")
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "wallah":
            await ctx.channel.send("Abgebrochen!")
            return

        try:
            await ctx.channel.send("Gebe das geheime geheim passwort ein.")
            confirmation_message = await self.bot.wait_for(
                "message", check=check, timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.channel.send("Timeout! Abgebrochen!")
            return

        if confirmation_message.content.lower() != "passwort":
            await ctx.channel.send("Falsches Passwort!")
            return

        message = """
<:info:1323229608379682826>Du erhältst diese Nachricht, weil dir ein Server gehört, auf dem <@1255607578722046015> verwendet wird. Keine Sorge – du wirst keine nervige Werbung per DM erhalten. Dies ist eine einmalige Nachricht, die wir aufgrund einer wichtigen Ankündigung an alle Serveradministratoren schreiben.

Kurze rede langer sinn, Tanjun 1.0 ist fertig. Der Demo Bot wird nicht mehr weiter gepflegt. Du kannst ihn also ohne bedenken von deinem Server entfernen. Wenn du Tanjun 1.0 nutzen möchstes, kannst du ihn mit [diesem Link](https://discord.com/oauth2/authorize?client_id=885984139315122206) https://discord.com/oauth2/authorize?client_id=885984139315122206 einladen.
Der Demo Tanjun Bot wird in Zukunft unter umständen noch zum testen verwendet, allerdings wird er nicht immer 24/7 online sein, wodurch er keine alternative zu Tanjun darstellt.

Alle Daten, die über den Demo Tanjun Bot gespeichert wurden, sind im Tanjun 1.0 nicht verfügbar. Das Level System und andere Einstellungen sind also wieder auf 0. Wenn du möchstest, dass ich beispielsweise das Level System wiederherstelle, schreibe mir (@entcheneric) bitte eine DM.

Vielen Dank, dass du geholfen hast Tanjun 1.0 fertig zu stellen und zu testen.

Liebe Grüße,
Das Tanjun-Team
@entcheneric, @arion2000 und @.pegi
                    """

        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue

            try:
                await owner.send(
                    embed=tanjunEmbed(
                        title="Tanjun Update",
                        description=message,
                    )
                )
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(administrationCog(bot))
