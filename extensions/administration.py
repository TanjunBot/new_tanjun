"""
THE COMMANDS IN THIS FILE ARE FOR ADMINISTRATIVE PURPOSES ONLY. THEY ARE NOT TO BE SHARED WITH ANYONE ELSE!
"""
from locale_keys import locale as l10n
from localizer import tanjunLocalizer
import asyncio
import json
import os
import re
import tempfile
import time
from typing import Any
import aiohttp
import discord
from aiohttp import ClientTimeout
from discord.ext import commands
import config
from api import feedbackBlockUser, feedbackUnblockUser
from commands.admin.join_to_create.listener import removeAllJoinToCreateChannels
from commands.channel.farewell import farewellUser
from commands.channel.welcome import welcomeNewUser
from extensions.logs import send_logEmbeds
from loops.create_database_backup import create_database_backup
from minigames.add_level_xp import update_user_roles
from minigames.counting_modes import get_correct_next_number, get_first_number
import contextlib
try:
    from diagnostics.benchmark_runner import BenchmarkRunner
    from diagnostics.runner import DiagnosticsRunner
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False
    BenchmarkRunner = None
from utility import addFeedback, embed_or_wrap, error_embed, missingLocalization, success_embed, tanjunEmbed, warning_embed
from utils.database_dump_sql import (
    extract_schemas_from_sql,
    filter_sql_dump,
    validate_filtered_import_sql,
)
from utils.github import begin_missing_localization_capture, cleanup_captured_missing_localization_issues, end_missing_localization_capture

def _mysql_defaults_file(user: str, password: str, host: str, port: int) -> str:
    """Create a temporary MySQL defaults file with credentials. Returns the file path."""
    content = f'[client]\nuser={user}\npassword={password}\nhost={host}\nport={port}\n'
    fd, path = tempfile.mkstemp(prefix='mysql_', suffix='.cnf', text=True)
    with os.fdopen(fd, 'w') as f:
        f.write(content)
    return path


class AdministrationCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._apply_command_docs()

    def _apply_command_docs(self) -> None:
        docs: dict[str, tuple[str, str, str]] = {
            'sync': ('Syncs application commands to Discord.', 'Sync commands', 't.sync'),
            'feedback': ('Stores internal feedback text.', 'Store feedback', 't.feedback <text>'),
            'blockFeedback': ('Blocks a user from feedback features.', 'Block feedback user', 't.blockFeedback @user'),
            'unblockFeedback': ('Unblocks a user from feedback features.', 'Unblock feedback user', 't.unblockFeedback @user'),
            'test_bot': ('Runs the diagnostics suite.', 'Run diagnostics', 't.test_bot'),
            'benchmark_bot': ('Runs the benchmark suite.', 'Run benchmarks', 't.benchmark_bot'),
            'test_translation': ('Sends translation test output.', 'Test translations', 't.test_translation'),
            'update': ('Runs maintenance steps and triggers restart endpoint.', 'Run maintenance update', 't.update'),
            'welcome': ('Triggers welcome flow for a user.', 'Test welcome flow', 't.welcome [@user]'),
            'farewell': ('Triggers farewell flow for a user.', 'Test farewell flow', 't.farewell [@user]'),
            'onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus': ('Sends the hardcoded long text message.', 'Send long meme text', 't.onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus'),
            'bsstarpoweremojis': ('Imports Brawl Stars star power emojis.', 'Import star power emojis', 't.bsstarpoweremojis [start]'),
            'bsgadgetsemojis': ('Imports Brawl Stars gadget emojis.', 'Import gadget emojis', 't.bsgadgetsemojis [start]'),
            'bsaccdata': ('Fetches and prints Brawl Stars account data.', 'Show Brawl Stars data', 't.bsaccdata <player_tag_without_hash>'),
            'editembedmessage': ('Sends and edits a test embed message.', 'Test embed edit', 't.editembedmessage'),
            'setguildlocale': ('Sets guild preferred locale.', 'Set guild locale', 't.setguildlocale <locale>'),
            'testgithubauthtoken': ('Runs the GitHub auth token test path.', 'Test GitHub auth path', 't.testgithubauthtoken'),
            'testupdateuserroles': ('Runs user role update logic test.', 'Test role updates', 't.testupdateuserroles'),
            'testgetcorrectnextnumber': ('Prints sequence output for counting mode logic.', 'Test counting sequence', 't.testgetcorrectnextnumber <mode> <numbers>'),
            'sendUpdateTextToAllAdmins': ('Broadcasts update text after confirmation flow.', 'Broadcast update message', 't.sendUpdateTextToAllAdmins'),
            'sendDemoIsNoMoreToAllAdmins': ('Broadcasts demo deprecation text after confirmation flow.', 'Broadcast demo deprecation', 't.sendDemoIsNoMoreToAllAdmins'),
            'me': ('Shows bot identity in current guild.', 'Show bot identity', 't.me'),
            'permissionTest': ('Checks composite channel permissions.', 'Check permissions', 't.permissionTest'),
            'permissionTest2': ('Checks manage_messages permission.', 'Check manage_messages', 't.permissionTest2'),
            'listPermissions': ('Lists bot permissions for a channel.', 'List bot permissions', 't.listPermissions [#channel]'),
            'database_sync': ('Imports SQL from attachment or URL, selects schema, backs up current DB, recreates target schema and imports.', 'Sync database from SQL backup', 't.database_sync [url] (or attach .sql)'),
        }
        for name, (help_text, brief_text, usage_text) in docs.items():
            cmd = self.bot.get_command(name)
            if cmd is None:
                continue
            cmd.help = help_text
            cmd.brief = brief_text
            cmd.usage = usage_text

    async def cog_check(self, ctx: commands.Context) -> bool:
        if ctx.author.id in config.adminIds:
            return True
        await ctx.send(embed=warning_embed('You are not allowed to use this command.', title='Permission Denied'))
        return False

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CheckFailure):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=error_embed(f'Missing required argument: `{error.param.name}`.', title='Invalid Command Usage'))
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=error_embed('One or more command arguments are invalid.', title='Invalid Command Usage'))
            return
        if isinstance(error, commands.BadUnionArgument):
            await ctx.send(embed=error_embed('Could not parse one or more arguments for this command.', title='Invalid Command Usage'))
            return

    def _locale(self, ctx: commands.Context) -> str:
        """Get locale string from context."""
        guild = getattr(ctx, 'guild', None)
        locale = str(guild.preferred_locale) if guild is not None else 'en_US'
        locale = locale.replace('_', '-')
        if locale.startswith('en-') or locale == 'en':
            locale = 'en'
        if locale not in ['en', 'de']:
            locale = 'en'
        return locale

    @commands.command()
    async def sync(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        if not ctx.bot.tree:
            return
        locale = self._locale(ctx)
        command_count = sum((1 for _ in ctx.bot.tree.walk_commands()))
        started = time.monotonic()
        spinner_frames = ('⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏')
        tick = 0
        status_msg = await ctx.send(embed=embed_or_wrap(l10n.commands.admin.sync.in_progress(locale, command_count=command_count, elapsed=0, spinner=spinner_frames[0]), title='Command Sync'))
        sync_task = asyncio.create_task(ctx.bot.tree.sync())
        try:
            while not sync_task.done():
                await asyncio.sleep(2)
                if sync_task.done():
                    break
                tick += 1
                elapsed = int(time.monotonic() - started)
                await status_msg.edit(embed=embed_or_wrap(l10n.commands.admin.sync.in_progress(locale, command_count=command_count, elapsed=elapsed, spinner=spinner_frames[tick % len(spinner_frames)]), title='Command Sync'))
            fmt = await sync_task
            duration = round(time.monotonic() - started, 1)
            await status_msg.edit(embed=success_embed(l10n.commands.admin.sync.completed(locale, count=len(fmt), duration=duration), title='Command Sync'))
        except Exception as e:
            if not sync_task.done():
                sync_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await sync_task
            await status_msg.edit(embed=error_embed(l10n.commands.admin.sync.failed(locale, error=e), title='Command Sync'))

    @commands.command()
    async def feedback(self, ctx: commands.Context, *, content: str) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await addFeedback(content, ctx.author.name)
        await ctx.send(embed=success_embed(l10n.commands.admin.feedback.added(self._locale(ctx))))

    @commands.command()
    async def blockFeedback(self, ctx: commands.Context, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackBlockUser(user.id)
        await ctx.send(embed=success_embed(l10n.commands.admin.feedback.blocked(self._locale(ctx), user_name=user.name)))

    @commands.command()
    async def unblockFeedback(self, ctx: commands.Context, user: discord.User) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await feedbackUnblockUser(user.id)
        await ctx.send(embed=success_embed(l10n.commands.admin.feedback.unblocked(self._locale(ctx), user_name=user.name)))

    @commands.command()
    async def test_bot(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        message = await ctx.send(embed=tanjunEmbed(title='Bot Diagnostics', description=l10n.commands.admin.administration.test_bot.starting(locale)))
        if not DIAGNOSTICS_AVAILABLE:
            await message.edit(embed=tanjunEmbed(title='Bot Diagnostics', description=l10n.commands.admin.administration.test_bot.tests_unavailable(locale)))
            return
        thread = None
        begin_missing_localization_capture()
        try:
            thread_name = f'bot-diagnostics-{ctx.message.id}'
            thread = await message.create_thread(name=thread_name[:100])
            runner = DiagnosticsRunner(self.bot, ctx, thread, message, locale=locale)
            await runner.run_all()
        except Exception as e:
            await message.edit(embed=error_embed(l10n.commands.admin.administration.test_bot.error(locale, test_name='Diagnostics', error=e), title='Bot Diagnostics'))
            if thread is not None:
                await thread.send(f'Diagnostics aborted: {e}')
        finally:
            end_missing_localization_capture()
            closed_count = await cleanup_captured_missing_localization_issues()
            if thread is not None and closed_count:
                await thread.send(f"Closed {closed_count} temporary missing-localization issue(s) created during this diagnostics run.")

    @commands.command()
    async def benchmark_bot(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        message = await ctx.send(embed=tanjunEmbed(title='Bot Benchmarks', description=l10n.commands.admin.administration.benchmark_bot.starting(locale)))
        if not DIAGNOSTICS_AVAILABLE or BenchmarkRunner is None:
            await message.edit(embed=tanjunEmbed(title='Bot Benchmarks', description=l10n.commands.admin.administration.benchmark_bot.unavailable(locale)))
            return
        thread = None
        try:
            thread_name = f'bot-benchmarks-{ctx.message.id}'
            thread = await message.create_thread(name=thread_name[:100])
            runner = BenchmarkRunner(self.bot, ctx, thread, message, locale=locale)
            await runner.run_all()
        except Exception as e:
            await message.edit(embed=error_embed(l10n.commands.admin.administration.benchmark_bot.error(locale, error=e), title='Bot Benchmarks'))
            if thread is not None:
                await thread.send(f'Benchmark aborted: {e}')

    @commands.command()
    async def test_translation(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        text = tanjunLocalizer.test_localize('de', 'commands.logs')
        await ctx.send(embed=embed_or_wrap(str(text)[:4000], title='Translation Test'))

    @commands.command()
    async def update(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        await send_logEmbeds(self.bot)
        await create_database_backup(self.bot)
        await removeAllJoinToCreateChannels()
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.update.updating(locale), title='Update'))
        try:
            async with aiohttp.ClientSession() as session, session.get(f'http://127.0.0.1:6969/restart/{self.bot.application_id}', timeout=ClientTimeout(total=10)) as response:
                if response.status != 200:
                    await ctx.send(embed=error_embed(l10n.commands.admin.administration.update.http_error(locale, status=response.status, response=await response.text()), title='Update Error'))
                    return
                await ctx.send(embed=embed_or_wrap(await response.text(), title='Update Response'))
        except (TimeoutError, aiohttp.ClientError) as e:
            await ctx.send(embed=error_embed(l10n.commands.admin.administration.update.connection_failed(locale, error=e), title='Update Error'))

    @commands.command()
    async def welcome(self, ctx: commands.Context, user: discord.Member | None=None) -> None:
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await welcomeNewUser(user)

    @commands.command()
    async def farewell(self, ctx: commands.Context, user: discord.Member | None=None) -> None:
        if user is None:
            user = ctx.author
        if ctx.author.id not in config.adminIds:
            return
        await farewellUser(user)

    @commands.command()
    async def onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        emoji = ctx.bot.get_emoji(config.WELCOME_EMOJI_ID)
        await ctx.send(embed=tanjunEmbed(description=f"{emoji} One thing about me ich fahr Auto seit vier Jahn'. Eines Tages woll ich in den Club Fahrn'. Ich stand an einer roten Ampel und ich war ganz allein, hinter mir war ein bus, und er fier mir rein. Er hupte mich an HUP HUP und ich stieg aus, schau mir an was passiert ist und er kommt raus."))

    async def getBrawlers(self) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {config.brawlstarsToken}'}
            async with session.get('https://api.brawlstars.com/v1/brawlers', headers=headers, timeout=ClientTimeout(total=10)) as response:
                result = await response.json()
                if not isinstance(result, dict):
                    return {'items': []}
                return result

    @commands.command()
    async def bsstarpoweremojis(self, ctx: commands.Context, start: int=0) -> None:
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        all_brawlers = await self.getBrawlers()
        for i, brawler in enumerate(all_brawlers['items']):
            if i < start:
                continue
            star_powers = brawler['star_powers']
            for star_power in star_powers:
                url = f"https://cdn.brawlify.com/star-powers/borderless/{star_power['id']}.png"
                try:
                    async with aiohttp.ClientSession() as session, session.get(url, timeout=ClientTimeout(total=10)) as response:
                        if response.status != 200:
                            print(f"Download failed: {response.status} for {star_power['name']}")
                            await ctx.send(embed=error_embed(l10n.commands.admin.administration.bs_download_failed(locale, status=response.status, name=star_power['name'])))
                            continue
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(name=f"{star_power['id']}", image=image)
                        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.bs_emoji_created(locale, emoji=emoji, name=star_power['name'], index=i)))
                except (TimeoutError, aiohttp.ClientError, discord.HTTPException) as e:
                    print(f"Failed to create emoji for {star_power['name']}: {e}")
                    await ctx.send(embed=error_embed(l10n.commands.admin.administration.bs_emoji_failed(locale, name=star_power['name'], error=e)))
                    continue

    @commands.command()
    async def bsgadgetsemojis(self, ctx: commands.Context, start: int=0) -> None:
        if ctx.author.id not in config.adminIds:
            return
        locale = self._locale(ctx)
        all_brawlers = await self.getBrawlers()
        for i, brawler in enumerate(all_brawlers['items']):
            if i < start:
                continue
            gadgets = brawler['gadgets']
            for gadget in gadgets:
                url = f"https://cdn.brawlify.com/gadgets/borderless/{gadget['id']}.png"
                try:
                    async with aiohttp.ClientSession() as session, session.get(url, timeout=ClientTimeout(total=10)) as response:
                        if response.status != 200:
                            print(f"Download failed: {response.status} for {gadget['name']}")
                            await ctx.send(embed=error_embed(l10n.commands.admin.administration.bs_download_failed(locale, status=response.status, name=gadget['name'])))
                            continue
                        image = await response.read()
                        emoji = await ctx.guild.create_custom_emoji(name=f"{gadget['id']}", image=image)
                        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.bs_emoji_created(locale, emoji=emoji, name=gadget['name'], index=i)))
                except (TimeoutError, aiohttp.ClientError, discord.HTTPException) as e:
                    print(f"Failed to create emoji for {gadget['name']}: {e}")
                    await ctx.send(embed=error_embed(l10n.commands.admin.administration.bs_emoji_failed(locale, name=gadget['name'], error=e)))
                    continue

    async def getAccData(self, id: str) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {config.brawlstarsToken}'}
            async with session.get(f'https://api.brawlstars.com/v1/players/%23{id}', headers=headers, timeout=ClientTimeout(total=10)) as response:
                result = await response.json()
                if not isinstance(result, dict):
                    return {}
                return result

    @commands.command()
    async def bsaccdata(self, ctx: commands.Context, id: str) -> None:
        if ctx.author.id not in config.adminIds:
            return
        acc_data = await self.getAccData(id)
        acc_data['brawlers'] = acc_data['brawlers'][1]
        await ctx.send(embed=embed_or_wrap(f'```json\n{json.dumps(acc_data, indent=4)[0:1900]}\n```', title='Brawl Stars Account Data'))

    @commands.command()
    async def editembedmessage(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        message = await ctx.send(embed=tanjunEmbed(title='test', description='test. I will edit this soon..'))
        await asyncio.sleep(2)
        await message.edit(embed=tanjunEmbed(title='test2', description='test2. I have edited this!'))

    @commands.command()
    async def setguildlocale(self, ctx: commands.Context, locale: str) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await ctx.guild.edit(preferred_locale=locale)
        await ctx.send(embed=success_embed(l10n.commands.admin.administration.set_guild_locale(self._locale(ctx), locale=locale), title='Locale'))

    @commands.command()
    async def testgithubauthtoken(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await missingLocalization('test', 'JUSTATEST.IGNORETHIS.JUSTATEST')
        await ctx.send(embed=success_embed(l10n.commands.admin.administration.github_auth_test(self._locale(ctx)), title='GitHub Auth Token Test'))

    @commands.command()
    async def testupdateuserroles(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await update_user_roles(ctx.message, 10, str(ctx.guild.id))

    @commands.command()
    async def testgetcorrectnextnumber(self, ctx: commands.Context, mode: int, numbers: int) -> None:
        if ctx.author.id not in config.adminIds:
            return
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.console_check(self._locale(ctx))))
        current_correct_number = get_first_number(mode)
        for i in range(numbers):
            print(f'i: {i}, current_correct_number: {current_correct_number}')
            current_correct_number = get_correct_next_number(mode, current_correct_number)

    @commands.command()
    async def sendUpdateTextToAllAdmins(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return

        def check(m) -> None:
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.confirm(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'y':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.confirm2(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'y':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.say_wallah(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'wallah':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.enter_password(self._locale(ctx)), title='Enter Password'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        expected_password = l10n.commands.admin.update_text.expected_password(self._locale(ctx)).lower()
        if confirmation_message.content.lower() != expected_password:
            await ctx.channel.send(embed=error_embed(l10n.commands.admin.update_text.wrong_password(self._locale(ctx)), title='Wrong Password'))
            return
        message = '\n<:info:1323229608379682826>Du erhältst diese Nachricht, weil dir ein Server gehört, auf dem <@885984139315122206> verwendet wird. Keine Sorge – du wirst keine nervige Werbung per DM erhalten. Dies ist eine einmalige Nachricht, die wir aufgrund einer wichtigen Ankündigung an alle Serveradministratoren schreiben.\n\nTanjun 1.0\nTL;DR:\nWir haben Tanjun komplett überarbeitet, sodass er jetzt wesentlich besser läuft. Konfiguriere die Einstellungen, die du auf deinem Server nutzen möchtest, neu, damit Tanjun weiterhin reibungslos funktioniert. @entcheneric kann dir bei der Konfiguration helfen.\n\nNach vielen Monaten harter Arbeit ist es endlich so weit: Tanjun 1.0 ist fertig!\nFalls du es nicht mitbekommen hast, hier eine kurze Erklärung:\nWir haben uns vor einer Weile dazu entschieden, Tanjun von Grund auf neu zu programmieren. Der Hauptgrund dafür war veralteter, inzwischen schwer zu pflegender Code in der vorherigen Version. Deshalb erschien es uns einfacher, einmal von neu zu beginnen.\n\nDa die interne Funktionsweise von Tanjun grundlegend überarbeitet und verbessert wurde, sind allerdings alte Konfigurationen nicht mehr kompatibel, weshalb du die Einstellungen des Bots einmal neu vornehmen musst. Am besten klickst du dich hierfür einmal Schritt für Schritt durch unsere ebenfalls überarbeitete [Dokumentation](https://app.gitbook.com/o/U7ew1TeWd8WAWHGeDLLf/s/kxqAE1ifXfn1iwkp233g/~/changes/123/tanjun-plus-und-pro), dann sollte die Neukonfiguration relativ einfach erledigt sein.\n\nSolltest du Funktionen von Tanjun genutzt haben, mit denen eine größere Menge an Daten gespeichert wurde (z.B. das Levelsystem), kannst du mir, @entcheneric, eine DM schreiben. Ich werde mein Bestes tun, um so viele Daten wie möglich wiederherzustellen.\n\nEntschuldigung für die verlorenen Einstellungen\nEs tut uns als Tanjun-Team sehr leid, dass wir die alten Daten nicht migrieren konnten. Eine Datenübertragung hätte jedoch einen enormen Aufwand bedeutet, da alles manuell hätte übertragen werden müssen. Als Entschuldigung gibt es für jeden Server bis zum 1. März 2025 kostenlos das Tanjun Pro-Abonnement. Außerdem erhält jeder Nutzer bis zu diesem Datum das Tanjun Plus-Abonnement kostenlos. Ab dem 1. März 2025 werden beide Abonnements dann als kostenpflichtige Optionen verfügbar sein.\n\nAbonnements? Gibt es eine Paywall für Tanjun?\nNein, ganz im Gegenteil! Wir hassen Paywalls und Abonnements genauso wie du. Unser Ziel ist es, Tanjun für alle zugänglich zu machen, mit diversen Funktionen und ohne Einschränkungen. Tanjun erzeugt aber auch Betriebskosten und andere laufende Ausgaben, und die Arbeit an Tanjun ist ein Vollzeitjob. Deshalb freuen wir uns über jede Unterstützung. Tanjun weiterhin kostenlos zu nutzen, ist natürlich auch kein Problem!\n\nUm mehr über Tanjun Pro und Tanjun Plus zu erfahren, erfährst du [hier](https://app.gitbook.com/o/U7ew1TeWd8WAWHGeDLLf/s/kxqAE1ifXfn1iwkp233g/docs/tanjun-plus-und-pro) genauere Details und Vorteile.\n\nVielen Dank, dass du Tanjun nutzt!\n\nLiebe Grüße,\nDas Tanjun-Team\n@entcheneric, @arion2000 und @.pegi\n                    '
        sent_owners = []
        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue
            if owner.id in sent_owners:
                continue
            sent_owners.append(owner.id)
            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                await owner.send(embed=tanjunEmbed(title='Tanjun Update', description=message))

    @commands.command()
    async def sendDemoIsNoMoreToAllAdmins(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return

        def check(m) -> None:
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.demo_message.confirm(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'y':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.confirm2(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'y':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.say_wallah(self._locale(ctx)), title='Confirmation'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        if confirmation_message.content.lower() != 'wallah':
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.cancelled(self._locale(ctx)), title='Cancelled'))
            return
        try:
            await ctx.channel.send(embed=embed_or_wrap(l10n.commands.admin.update_text.enter_password(self._locale(ctx)), title='Enter Password'))
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await ctx.channel.send(embed=warning_embed(l10n.commands.admin.update_text.timeout(self._locale(ctx)), title='Timeout'))
            return
        expected_password = l10n.commands.admin.update_text.expected_password(self._locale(ctx)).lower()
        if confirmation_message.content.lower() != expected_password:
            await ctx.channel.send(embed=error_embed(l10n.commands.admin.update_text.wrong_password(self._locale(ctx)), title='Wrong Password'))
            return
        message = '\n<:info:1323229608379682826>Du erhältst diese Nachricht, weil dir ein Server gehört, auf dem <@1255607578722046015> verwendet wird. Keine Sorge – du wirst keine nervige Werbung per DM erhalten. Dies ist eine einmalige Nachricht, die wir aufgrund einer wichtigen Ankündigung an alle Serveradministratoren schreiben.\n\nKurze rede langer sinn, Tanjun 1.0 ist fertig. Der Demo Bot wird nicht mehr weiter gepflegt. Du kannst ihn also ohne bedenken von deinem Server entfernen. Wenn du Tanjun 1.0 nutzen möchstes, kannst du ihn mit [diesem Link](https://discord.com/oauth2/authorize?client_id=885984139315122206) https://discord.com/oauth2/authorize?client_id=885984139315122206 einladen.\nDer Demo Tanjun Bot wird in Zukunft unter umständen noch zum testen verwendet, allerdings wird er nicht immer 24/7 online sein, wodurch er keine alternative zu Tanjun darstellt.\n\nAlle Daten, die über den Demo Tanjun Bot gespeichert wurden, sind im Tanjun 1.0 nicht verfügbar. Das Level System und andere Einstellungen sind also wieder auf 0. Wenn du möchstest, dass ich beispielsweise das Level System wiederherstelle, schreibe mir (@entcheneric) bitte eine DM.\n\nVielen Dank, dass du geholfen hast Tanjun 1.0 fertig zu stellen und zu testen.\n\nLiebe Grüße,\nDas Tanjun-Team\n@entcheneric, @arion2000 und @.pegi\n                    '
        for guild in self.bot.guilds:
            owner = guild.owner
            if not owner:
                continue
            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                await owner.send(embed=tanjunEmbed(title='Tanjun Update', description=message))

    @commands.command()
    async def me(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        me = ctx.guild.me
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.me(self._locale(ctx), name=me.name, id=me.id, mention=me.mention), title='Bot Info'))

    @commands.command()
    async def permissionTest(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        permission_result = not ctx.channel.permissions_for(ctx.guild.me).manage_messages or not ctx.channel.permissions_for(ctx.guild.me).read_message_history or (not ctx.channel.permissions_for(ctx.guild.me).manage_channels)
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.permission_result(self._locale(ctx), result=permission_result), title='Permission Test'))

    @commands.command()
    async def permissionTest2(self, ctx: commands.Context) -> None:
        if ctx.author.id not in config.adminIds:
            return
        permission_result = ctx.channel.permissions_for(ctx.guild.me).manage_messages
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.permission_result(self._locale(ctx), result=permission_result), title='Permission Test 2'))

    @commands.command()
    async def listPermissions(self, ctx: commands.Context, channel: discord.TextChannel | None=None) -> None:
        if ctx.author.id not in config.adminIds:
            return
        if not channel:
            channel = ctx.channel
        permission_result = channel.permissions_for(ctx.guild.me)
        permission_text = ''
        for permission in permission_result:
            permission_text += f'{permission}\n'
        await ctx.send(embed=embed_or_wrap(l10n.commands.admin.administration.permission_list(self._locale(ctx), permissions=permission_text), title='Permissions'))

    @commands.command()
    async def database_sync(self, ctx: commands.Context, url: str | None=None) -> None:
        if ctx.author.id not in config.adminIds:
            return

        _MAX_LOG = 1900

        def _truncate_log(text: str) -> str:
            if len(text) > _MAX_LOG:
                return text[:_MAX_LOG] + '\n... (truncated)'
            return text

        thread = await ctx.channel.create_thread(
            name=f'Database Sync — {ctx.author.display_name}',
            message=None,
            type=discord.ChannelType.public_thread,
        )

        async def _thread_send(
            content: str | None = None,
            embed: discord.Embed | None = None,
            file: discord.File | None = None,
        ) -> discord.Message | None:
            try:
                return await thread.send(content=content, embed=embed, file=file)
            except Exception:
                return None

        attachment_url = None
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
        elif url:
            attachment_url = url
        else:
            await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.no_attachment(self._locale(ctx)), title='Database Sync'))
            return
        status_msg = await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.downloading(self._locale(ctx)), title='Database Sync'))
        if status_msg is None:
            return
        try:
            async with aiohttp.ClientSession() as session, session.get(attachment_url, timeout=ClientTimeout(total=300)) as resp:
                if resp.status != 200:
                    await status_msg.edit(embed=error_embed(l10n.commands.admin.database_sync.download_failed(self._locale(ctx), status=resp.status), title='Database Sync'))
                    return
                content = await resp.read()
            with open('temp_import.sql', 'wb') as f:
                f.write(content)
        except Exception as e:
            await status_msg.edit(embed=error_embed(l10n.commands.admin.database_sync.download_error(self._locale(ctx), error=e), title='Database Sync'))
            return
        await status_msg.edit(embed=embed_or_wrap(l10n.commands.admin.database_sync.analyzing(self._locale(ctx)), title='Database Sync'))
        with open('temp_import.sql', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        detected_schemas = extract_schemas_from_sql(sql_content)
        schemas = set(detected_schemas)
        if not detected_schemas:
            schemas.add(l10n.commands.admin.database_sync.no_schema_found(self._locale(ctx)))
        schema_list = '\n'.join([f'- `{s}`' for s in schemas])
        await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.schema_prompt(self._locale(ctx), schema_list=schema_list), title='Database Sync'))

        def check(m: discord.Message) -> bool:
            return m.author == ctx.author and m.channel == thread
        try:
            confirmation_message = await self.bot.wait_for('message', check=check, timeout=60.0)
        except TimeoutError:
            await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.timeout(self._locale(ctx)), title='Database Sync'))
            return
        selected_schema = confirmation_message.content.strip()
        cancel_token = l10n.commands.admin.database_sync.cancel_token(self._locale(ctx)).lower()
        if selected_schema.lower() == cancel_token:
            await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.aborted(self._locale(ctx)), title='Database Sync'))
            return
        if detected_schemas and selected_schema not in detected_schemas:
            await _thread_send(embed=error_embed(l10n.commands.admin.database_sync.schema_warning(self._locale(ctx)), title='Database Sync'))
            return
        await _thread_send(embed=embed_or_wrap(l10n.commands.admin.database_sync.preparing_import(self._locale(ctx), schema=selected_schema), title='Database Sync'))
        assert config.database_user is not None
        assert config.database_password is not None
        assert config.database_schema is not None
        backup_file = 'current_db_backup.sql'
        defaults_file = _mysql_defaults_file(config.database_user, config.database_password, config.database_ip, config.database_port)
        try:
            await _thread_send(embed=embed_or_wrap('Running mysqldump…', title='Database Sync'))
            proc = await asyncio.create_subprocess_exec(
                'mysqldump', f'--defaults-extra-file={defaults_file}', config.database_schema,
                stdout=open(backup_file, 'w'),
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                stderr_text = _truncate_log(stderr.decode(errors='replace')) if stderr else ''
                await _thread_send(embed=error_embed(f"mysqldump failed (exit {proc.returncode}):\n```\n{stderr_text}\n```", title='Database Sync'))
                return
            await _thread_send(embed=success_embed(l10n.commands.admin.database_sync.backup_success(self._locale(ctx)), title='Database Sync'), file=discord.File(backup_file))
        except Exception as e:
            await _thread_send(embed=error_embed(l10n.commands.admin.database_sync.backup_error(self._locale(ctx), error=e), title='Database Sync'))
            return
        finally:
            with contextlib.suppress(OSError):
                os.unlink(defaults_file)
        filtered_sql_file = 'filtered_import.sql'
        selected_dump_file = f'{selected_schema}_only.sql'
        expected_table_names: list[str] = []
        try:
            filtered_content = filter_sql_dump(
                sql_content,
                selected_schema=selected_schema,
                target_schema=config.database_schema,
            )
            is_valid, validation_error, expected_table_names = validate_filtered_import_sql(
                filtered_content, config.database_schema
            )
            if not is_valid:
                await _thread_send(embed=error_embed(validation_error, title='Database Sync'))
                return
            with open(filtered_sql_file, 'w', encoding='utf-8') as f_out:
                f_out.write(filtered_content)
            with open(selected_dump_file, 'w', encoding='utf-8') as f_out:
                f_out.write(filtered_content)
        except Exception as e:
            await _thread_send(embed=error_embed(l10n.commands.admin.database_sync.filter_error(self._locale(ctx), error=e), title='Database Sync'))
            return
        db_recreate_cmd = f'DROP DATABASE IF EXISTS `{config.database_schema}`; CREATE DATABASE `{config.database_schema}`;'
        import_defaults_file = _mysql_defaults_file(config.database_user, config.database_password, config.database_ip, config.database_port)
        try:
            await _thread_send(embed=embed_or_wrap('Dropping and recreating database…', title='Database Sync'))
            proc = await asyncio.create_subprocess_exec(
                'mysql', f'--defaults-extra-file={import_defaults_file}', '-e', db_recreate_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                stderr_text = _truncate_log(stderr.decode(errors='replace')) if stderr else ''
                await _thread_send(embed=error_embed(f"Database recreate failed (exit {proc.returncode}):\n```\n{stderr_text}\n```", title='Database Sync'))
                return
            if stdout and stdout.decode(errors='replace').strip():
                await _thread_send(f"```\n{_truncate_log(stdout.decode(errors='replace'))}\n```")

            await _thread_send(embed=embed_or_wrap('Importing data…', title='Database Sync'))
            with open(filtered_sql_file, 'rb') as f:
                proc = await asyncio.create_subprocess_exec(
                    'mysql', f'--defaults-extra-file={import_defaults_file}', config.database_schema,
                    stdin=f,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                stdout_text = stdout.decode(errors='replace') if stdout else ''
                stderr_text = stderr.decode(errors='replace') if stderr else ''
                log_output = _truncate_log(stderr_text or stdout_text or f'exit code {proc.returncode}')
                await _thread_send(embed=error_embed(f"Import failed (exit {proc.returncode}):\n```\n{log_output}\n```", title='Database Sync'))
                return

            if stdout:
                stdout_text = stdout.decode(errors='replace')
                if stdout_text.strip():
                    await _thread_send(f"```\n{_truncate_log(stdout_text)}\n```")
            if stderr:
                stderr_text = stderr.decode(errors='replace')
                if stderr_text.strip():
                    await _thread_send(f"```\n{_truncate_log(stderr_text)}\n```")
            verify_sql = (
                f"USE `{config.database_schema}`; "
                "SELECT COUNT(*) FROM information_schema.tables "
                f"WHERE table_schema='{config.database_schema}';"
            )
            verify_proc = await asyncio.create_subprocess_exec(
                'mysql', f'--defaults-extra-file={import_defaults_file}', '-N', '-B', '-e', verify_sql,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            verify_stdout, verify_stderr = await verify_proc.communicate()
            if verify_proc.returncode != 0:
                verify_error = _truncate_log((verify_stderr or b'').decode(errors='replace'))
                await _thread_send(embed=error_embed(f'Post-import verification failed:\n```\n{verify_error}\n```', title='Database Sync'))
                return
            table_count_text = (verify_stdout or b'').decode(errors='replace').strip()
            try:
                imported_table_count = int(table_count_text.splitlines()[-1])
            except (ValueError, IndexError):
                await _thread_send(embed=error_embed('Post-import verification returned an unreadable table count.', title='Database Sync'))
                return
            expected_table_count = len(set(expected_table_names))
            if imported_table_count < expected_table_count or imported_table_count == 0:
                await _thread_send(
                    embed=error_embed(
                        f'Post-import verification failed: expected at least {expected_table_count} tables, found {imported_table_count}.',
                        title='Database Sync',
                    ),
                )
                return
            await _thread_send(embed=success_embed(l10n.commands.admin.database_sync.success(self._locale(ctx)), title='Database Sync'))
        except Exception as e:
            await _thread_send(embed=error_embed(l10n.commands.admin.database_sync.import_error(self._locale(ctx), error=e), title='Database Sync'))
        finally:
            with contextlib.suppress(OSError):
                os.unlink(import_defaults_file)
        for tmp_file in ['temp_import.sql', 'filtered_import.sql']:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdministrationCog(bot))