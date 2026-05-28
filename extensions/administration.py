"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""

import asyncio
import json
import os
import re
import subprocess
import tempfile
from typing import Any

import aiohttp
import discord
from aiohttp import ClientTimeout
from discord.ext import commands

import config
from api import feedbackBlockUser, feedbackUnblockUser
from commands.admin.join_to_create.listener import (
    removeAllJoinToCreateChannels,
)
from commands.channel.farewell import farewellUser
from commands.channel.welcome import welcomeNewUser
from extensions.logs import send_logEmbeds
from localizer import tanjunLocalizer
from loops.create_database_backup import create_database_backup
from minigames.add_level_xp import update_user_roles
from minigames.counting_modes import get_correct_next_number, get_first_number

# Import test functions only if they exist
try:
    from tests import test_commands, test_database, test_ping

    TEST_FUNCTIONS_AVAILABLE = True
except ImportError:
    TEST_FUNCTIONS_AVAILABLE = False
    print("Warning: Test functions not available in tests module")
import contextlib

from utility import addFeedback, missingLocalization, tanjunEmbed


def _mysql_defaults_file(user: str, password: str, host: str, port: int) -> str:
    """Create a temporary MySQL defaults file with credentials. Returns the file path."""
    content = f"[client]\nuser={user}\npassword={password}\nhost={host}\nport={port}\n"
    fd, path = tempfile.mkstemp(prefix="mysql_", suffix=".cnf", text=True)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class AdministrationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def _locale(self, ctx: commands.Context) -> str:
        """Get locale string from context."""
        guild = getattr(ctx, "guild", None)
        locale = str(guild.preferred_locale) if guild is not None else "en_US"

        # Normalize locale string
        locale = locale.replace("_", "-")

        # Canonicalize common English variants to "en"
        if locale.startswith("en-") or locale == "en":
            locale = "en"

        # Ensure fallback is valid
        if locale not in ["en", "de"]:
            locale = "en"

        return locale

    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        if not ctx.bot.tree:
            return
        fmt = await ctx.bot.tree.sync()
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.sync.completed", count=len(fmt)))

    @commands.command()
    async def feedback(self, ctx: commands.Context, *, content: str) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await addFeedback(content, ctx.author.name)
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.feedback.added"))

    @commands.command()
    async def blockFeedback(self, ctx: commands.Context, user: discord.User) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await feedbackBlockUser(user.id)
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.feedback.blocked", user_name=user.name))

    @commands.command()
    async def unblockFeedback(self, ctx: commands.Context, user: discord.User) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await feedbackUnblockUser(user.id)
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.feedback.unblocked", user_name=user.name))

    @commands.command()
    async def test_bot(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        locale = self._locale(ctx)
        message = await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.starting"))

        if not TEST_FUNCTIONS_AVAILABLE:
            await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.tests_unavailable"))
            return

        await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.current_test_ping"))
        try:
            await test_ping(self, ctx)
        except Exception as e:
            await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.error", test_name="Ping", error=e))
            return
        await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.current_test_db"))
        try:
            await test_database(self, ctx)
        except Exception as e:
            await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.error", test_name="Database", error=e))
            return
        await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.current_test_cmds"))
        try:
            await test_commands(self, ctx)
        except Exception as e:
            await message.edit(content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.error", test_name="Commands", error=e))
            return
        await message.edit(
            content=tanjunLocalizer.localize(locale, "commands.admin.administration.test_bot.all_completed")
        )

    @commands.command()
    async def test_translation(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        text = tanjunLocalizer.test_localize("de", "commands.logs")
        await ctx.send(str(text)[:4000])

    @commands.command()
    async def update(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        locale = self._locale(ctx)
        await send_logEmbeds(self.bot)
        await create_database_backup(self.bot)
        await removeAllJoinToCreateChannels()
        await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.update.updating"))
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    f"http://127.0.0.1:6969/restart/{self.bot.application_id}", timeout=ClientTimeout(total=10)
                ) as response,
            ):
                if response.status != 200:
                    await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.update.http_error", status=response.status, response=await response.text()))
                    return
                await ctx.send(await response.text())
        except (TimeoutError, aiohttp.ClientError) as e:
            await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.update.connection_failed", error=e))

    @commands.command()
    async def welcome(self, ctx: commands.Context, user: discord.Member | None = None) -> None:  # type: ignore[type-arg]
        if user is None:
            user = ctx.author  # type: ignore[assignment]
        if ctx.author.id not in config.adminIds:
            return
        await welcomeNewUser(user)  # type: ignore[arg-type]

    @commands.command()
    async def farewell(self, ctx: commands.Context, user: discord.Member | None = None) -> None:  # type: ignore[type-arg]
        if user is None:
            user = ctx.author  # type: ignore[assignment]
        if ctx.author.id not in config.adminIds:
            return
        await farewellUser(user)  # type: ignore[arg-type]

    @commands.command()
    async def onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus(
        self,
        ctx: commands.Context,  # type: ignore[type-arg]
    ) -> None:
        if ctx.author.id not in config.adminIds:
            return
        emoji = ctx.bot.get_emoji(1266369876524666920)
        await ctx.send(
            f"{emoji} One thing about me ich fahr Auto seit vier Jahn'. Eines Tages woll ich in den Club Fahrn'. Ich stand an einer roten Ampel und ich war ganz allein, hinter mir war ein bus, und er fier mir rein. Er hupte mich an HUP HUP und ich stieg aus, schau mir an was passiert ist und er kommt raus."
        )

    async def getBrawlers(self) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.brawlstarsToken}"}
            async with session.get(
                "https://api.brawlstars.com/v1/brawlers", headers=headers, timeout=ClientTimeout(total=10)
            ) as response:
                result = await response.json()
                if not isinstance(result, dict):
                    return {"items": []}
                return result

    @commands.command()
    async def bsstarpoweremojis(self, ctx: commands.Context, start: int = 0) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        all_brawlers = await self.getBrawlers()
        for i, brawler in enumerate(all_brawlers["items"]):
            if i < start:
                continue
            star_powers = brawler["star_powers"]
            for star_power in star_powers:
                url = f"https://cdn.brawlify.com/star-powers/borderless/{star_power['id']}.png"
                try:
                    async with (
                        aiohttp.ClientSession() as session,
                        session.get(url, timeout=ClientTimeout(total=10)) as response,
                    ):
                        if response.status != 200:
                            print(f"Download failed: {response.status} for {star_power['name']}")
                            await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_download_failed", status=response.status, name=star_power['name']))
                            continue
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(name=f"{star_power['id']}", image=image)  # type: ignore[union-attr]
                        await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_emoji_created", emoji=emoji, name=star_power['name'], index=i))
                except (TimeoutError, aiohttp.ClientError, discord.HTTPException) as e:
                    print(f"Failed to create emoji for {star_power['name']}: {e}")
                    await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_emoji_failed", name=star_power['name'], error=e))
                    continue

    @commands.command()
    async def bsgadgetsemojis(self, ctx: commands.Context, start: int = 0) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        all_brawlers = await self.getBrawlers()
        for i, brawler in enumerate(all_brawlers["items"]):
            if i < start:
                continue
            gadgets = brawler["gadgets"]
            for gadget in gadgets:
                url = f"https://cdn.brawlify.com/gadgets/borderless/{gadget['id']}.png"
                try:
                    async with (
                        aiohttp.ClientSession() as session,
                        session.get(url, timeout=ClientTimeout(total=10)) as response,
                    ):
                        if response.status != 200:
                            print(f"Download failed: {response.status} for {gadget['name']}")
                            await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_download_failed", status=response.status, name=gadget['name']))
                            continue
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(name=f"{gadget['id']}", image=image)  # type: ignore[union-attr]

                        await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_emoji_created", emoji=emoji, name=gadget['name'], index=i))
                except (TimeoutError, aiohttp.ClientError, discord.HTTPException) as e:
                    print(f"Failed to create emoji for {gadget['name']}: {e}")
                    await ctx.send(tanjunLocalizer.localize(locale, "commands.admin.administration.bs_emoji_failed", name=gadget['name'], error=e))
                    continue

    async def getAccData(self, id: str) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {config.brawlstarsToken}"}
            async with session.get(
                f"https://api.brawlstars.com/v1/players/%23{id}", headers=headers, timeout=ClientTimeout(total=10)
            ) as response:
                result = await response.json()
                if not isinstance(result, dict):
                    return {}
                return result

    @commands.command()
    async def bsaccdata(self, ctx: commands.Context, id: str) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        acc_data = await self.getAccData(id)
        acc_data["brawlers"] = acc_data["brawlers"][1]
        await ctx.send(f"```json\n{(json.dumps(acc_data, indent=4))[0:1900]}\n```")

    @commands.command()
    async def editembedmessage(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        message = await ctx.send(embed=tanjunEmbed(title="test", description="test. I will edit this soon.."))
        await asyncio.sleep(2)
        await message.edit(embed=tanjunEmbed(title="test2", description="test2. I have edited this!"))

    @commands.command()
    async def setguildlocale(self, ctx: commands.Context, locale: str) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await ctx.guild.edit(preferred_locale=locale)  # type: ignore[union-attr, arg-type]
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.set_guild_locale", locale=locale))

    @commands.command()
    async def testgithubauthtoken(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await missingLocalization("JUSTATEST.IGNORETHIS.JUSTATEST")
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.github_auth_test"))

    @commands.command()
    async def testupdateuserroles(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await update_user_roles(ctx.message, 10, str(ctx.guild.id))  # type: ignore[union-attr]

    @commands.command()
    async def testgetcorrectnextnumber(self, ctx: commands.Context, mode: int, numbers: int) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.console_check"))
        current_correct_number = get_first_number(mode)
        for i in range(numbers):
            print(f"i: {i}, current_correct_number: {current_correct_number}")
            current_correct_number = get_correct_next_number(mode, current_correct_number)  # type: ignore[assignment]

    @commands.command()
    async def sendUpdateTextToAllAdmins(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        def check(m) -> None:  # type: ignore[no-untyped-def]
            return m.author == ctx.author and m.channel == ctx.channel  # type: ignore[no-any-return]

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.confirm"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.confirm2"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.say_wallah"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "wallah":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.enter_password"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        expected_password = tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.expected_password").lower()
        if confirmation_message.content.lower() != expected_password:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.wrong_password"))
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

        sent_owners = []
        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue
            if owner.id in sent_owners:
                continue
            sent_owners.append(owner.id)

            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                await owner.send(
                    embed=tanjunEmbed(
                        title="Tanjun Update",
                        description=message,
                    )
                )

    @commands.command()
    async def sendDemoIsNoMoreToAllAdmins(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        def check(m) -> None:  # type: ignore[no-untyped-def]
            return m.author == ctx.author and m.channel == ctx.channel  # type: ignore[no-any-return]

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.demo_message.confirm"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.confirm2"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "y":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.say_wallah"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        if confirmation_message.content.lower() != "wallah":
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.cancelled"))
            return

        try:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.enter_password"))
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=30.0)  # type: ignore[arg-type]
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.timeout"))
            return

        expected_password = tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.expected_password").lower()
        if confirmation_message.content.lower() != expected_password:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.update_text.wrong_password"))
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

            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                await owner.send(
                    embed=tanjunEmbed(
                        title="Tanjun Update",
                        description=message,
                    )
                )

    @commands.command()
    async def me(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        me = ctx.guild.me  # type: ignore[union-attr]
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.me", name=me.name, id=me.id, mention=me.mention))

    @commands.command()
    async def permissionTest(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        permission_result = (
            not ctx.channel.permissions_for(ctx.guild.me).manage_messages  # type: ignore[union-attr]
            or not ctx.channel.permissions_for(ctx.guild.me).read_message_history  # type: ignore[union-attr]
            or not ctx.channel.permissions_for(ctx.guild.me).manage_channels  # type: ignore[union-attr]
        )
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.permission_result", result=permission_result))

    @commands.command()
    async def permissionTest2(self, ctx: commands.Context) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        permission_result = ctx.channel.permissions_for(ctx.guild.me).manage_messages  # type: ignore[union-attr]
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.permission_result", result=permission_result))

    @commands.command()
    async def listPermissions(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        if not channel:
            channel = ctx.channel  # type: ignore[assignment]

        permission_result = channel.permissions_for(ctx.guild.me)  # type: ignore[union-attr]
        permission_text = ""
        for permission in permission_result:
            permission_text += f"{permission}\n"
        await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.administration.permission_list", permissions=permission_text))

    @commands.command()
    async def database_sync(self, ctx: commands.Context, url: str | None = None) -> None:  # type: ignore[type-arg]
        if ctx.author.id not in config.adminIds:
            return

        attachment_url = None
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
        elif url:
            attachment_url = url
        else:
            await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.no_attachment"))
            return

        status_msg = await ctx.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.downloading"))

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(attachment_url, timeout=ClientTimeout(total=300)) as resp,
            ):
                if resp.status != 200:
                    await status_msg.edit(
                        content=tanjunLocalizer.localize(
                            self._locale(ctx), "commands.admin.database_sync.download_failed", status=resp.status
                        )
                    )
                    return
                content = await resp.read()

            with open("temp_import.sql", "wb") as f:
                f.write(content)
        except Exception as e:
            await status_msg.edit(
                content=tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.download_error", error=e)
            )
            return

        await status_msg.edit(content=tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.analyzing"))

        schemas: set[str] = set()
        with open("temp_import.sql", encoding="utf-8", errors="ignore") as f:
            for line in f:
                use_match = re.search(r"^USE\s+`?([^\s`;]+)`?", line, re.IGNORECASE)
                create_match = re.search(
                    r"CREATE DATABASE\s+(?:/\*.*?\*/\s+)?(?:IF NOT EXISTS\s+)?`?([^\s`;]+)`?", line, re.IGNORECASE
                )
                if create_match:
                    schemas.add(create_match.group(1))
                elif use_match:
                    schemas.add(use_match.group(1))

        if not schemas:
            schemas.add(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.no_schema_found"))

        schema_list = "\n".join([f"- `{s}`" for s in schemas])
        await status_msg.edit(
            content=tanjunLocalizer.localize(
                self._locale(ctx), "commands.admin.database_sync.schema_prompt", schema_list=schema_list
            )
        )

        def check(m: discord.Message) -> bool:
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            confirmation_message = await self.bot.wait_for("message", check=check, timeout=60.0)
        except TimeoutError:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.timeout"))
            return

        selected_schema = confirmation_message.content.strip()
        cancel_token = tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.cancel_token").lower()
        if selected_schema.lower() == cancel_token:
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.aborted"))
            return

        if selected_schema not in schemas and (
            tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.no_schema_found") not in list(schemas)[0]
        ):
            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.schema_warning"))

        # Parse and filter sql dump
        await ctx.channel.send(
            tanjunLocalizer.localize(
                self._locale(ctx), "commands.admin.database_sync.preparing_import", schema=selected_schema
            )
        )

        assert config.database_user is not None
        assert config.database_password is not None
        assert config.database_schema is not None

        # Backup current database
        backup_file = "current_db_backup.sql"
        defaults_file = _mysql_defaults_file(
            config.database_user, config.database_password, config.database_ip, config.database_port
        )
        dump_command = [
            "mysqldump",
            f"--defaults-extra-file={defaults_file}",
            config.database_schema,
        ]

        try:
            with open(backup_file, "w") as f:
                subprocess.run(dump_command, stdout=f, check=True)
            await ctx.channel.send(
                tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.backup_success"),
                file=discord.File(backup_file),
            )
        except Exception as e:
            await ctx.channel.send(
                tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.backup_error", error=e)
            )
            return
        finally:
            with contextlib.suppress(OSError):
                os.unlink(defaults_file)

        # Prepare filtered sql
        filtered_sql_file = "filtered_import.sql"
        current_schema = None

        try:
            with (
                open("temp_import.sql", encoding="utf-8", errors="ignore") as f_in,
                open(filtered_sql_file, "w", encoding="utf-8") as f_out,
            ):
                for line in f_in:
                    use_m = re.search(r"^USE\s+`?([^\s`;]+)`?", line, re.IGNORECASE)
                    create_m = re.search(
                        r"CREATE DATABASE\s+(?:/\*.*?\*/\s+)?(?:IF NOT EXISTS\s+)?`?([^\s`;]+)`?", line, re.IGNORECASE
                    )

                    if create_m:
                        current_schema = create_m.group(1)
                    elif use_m:
                        current_schema = use_m.group(1)

                    if current_schema is None or current_schema.lower() == selected_schema.lower():
                        mod_line = re.sub(
                            rf"(CREATE DATABASE\s+(?:/\*.*?\*/\s+)?(?:IF NOT EXISTS\s+)?)`?{re.escape(selected_schema)}`?",
                            rf"\g<1>`{config.database_schema}`",
                            line,
                            flags=re.IGNORECASE,
                        )
                        mod_line = re.sub(
                            rf"(USE\s+)`?{re.escape(selected_schema)}`?",
                            rf"\g<1>`{config.database_schema}`",
                            mod_line,
                            flags=re.IGNORECASE,
                        )
                        f_out.write(mod_line)
        except Exception as e:
            await ctx.channel.send(
                tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.filter_error", error=e)
            )
            return

        # Import filtered sql
        await ctx.channel.send(
            tanjunLocalizer.localize(
                self._locale(ctx), "commands.admin.database_sync.importing", schema=config.database_schema
            )
        )

        db_recreate_cmd = f"DROP DATABASE IF EXISTS `{config.database_schema}`; CREATE DATABASE `{config.database_schema}`;"
        try:
            subprocess.run(
                [
                    "mysql",
                    f"--defaults-extra-file={defaults_file}",
                    "-e",
                    db_recreate_cmd,
                ],
                check=True,
            )

            with open(filtered_sql_file) as f:
                subprocess.run(
                    [
                        "mysql",
                        f"--defaults-extra-file={defaults_file}",
                        config.database_schema,
                    ],
                    stdin=f,
                    check=True,
                )

            await ctx.channel.send(tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.success"))
        except subprocess.CalledProcessError as e:
            await ctx.channel.send(
                tanjunLocalizer.localize(self._locale(ctx), "commands.admin.database_sync.import_error", error=e)
            )

        # Clean up temporary files
        for tmp_file in ["temp_import.sql", "filtered_import.sql"]:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdministrationCog(bot))
