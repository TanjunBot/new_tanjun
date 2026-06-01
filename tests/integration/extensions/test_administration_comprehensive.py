from __future__ import annotations
from locale_keys import locale
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
import pytest
import config
import extensions.administration as admin_mod
from extensions.administration import AdministrationCog, _mysql_defaults_file
from tests.helpers.discord import make_guild, make_member, make_message, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot
EXTENSION = 'extensions.administration'
COG_NAME = 'AdministrationCog'
ADMIN_ID = 1001
NON_ADMIN_ID = 999999

def make_context(bot: MagicMock, *, author_id: int=ADMIN_ID, guild_locale: str='en-US', guild: MagicMock | None=None, channel: MagicMock | None=None, attachments: list[Any] | None=None) -> MagicMock:
    guild = guild or make_guild()
    guild.preferred_locale = guild_locale
    channel = channel or make_text_channel(guild=guild)
    author = make_member(user_id=author_id)
    ctx = MagicMock()
    ctx.author = author
    ctx.guild = guild
    ctx.channel = channel
    ctx.bot = bot
    ctx.send = AsyncMock()
    ctx.message = make_message(author=author, guild=guild, channel=channel)
    ctx.message.attachments = attachments or []
    return ctx

@pytest.fixture
async def cog() -> AdministrationCog:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    return bot.cogs[COG_NAME]

@pytest.fixture
def bot(cog: AdministrationCog) -> MagicMock:
    return cog.bot

class TestLocale:

    def test_locale_no_guild(self, cog: AdministrationCog) -> None:
        ctx = MagicMock()
        ctx.guild = None
        assert cog._locale(ctx) == 'en'

    def test_locale_german(self, cog: AdministrationCog) -> None:
        ctx = MagicMock()
        ctx.guild = MagicMock(preferred_locale='de')
        assert cog._locale(ctx) == 'de'

    def test_locale_unknown_fallback(self, cog: AdministrationCog) -> None:
        ctx = MagicMock()
        ctx.guild = MagicMock(preferred_locale='fr')
        assert cog._locale(ctx) == 'en'

    def test_locale_en_gb(self, cog: AdministrationCog) -> None:
        ctx = MagicMock()
        ctx.guild = MagicMock(preferred_locale='en_GB')
        assert cog._locale(ctx) == 'en'

@pytest.mark.asyncio
class TestNonAdminEarlyReturn:

    @pytest.mark.parametrize('method_name,extra_kwargs', [('sync', {}), ('feedback', {'content': 'hi'}), ('blockFeedback', {'user': make_member()}), ('unblockFeedback', {'user': make_member()}), ('test_bot', {}), ('benchmark_bot', {}), ('test_translation', {}), ('update', {}), ('welcome', {}), ('farewell', {}), ('onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus', {}), ('bsstarpoweremojis', {}), ('bsgadgetsemojis', {}), ('bsaccdata', {'id': 'ABC123'}), ('editembedmessage', {}), ('setguildlocale', {'locale': 'de'}), ('testgithubauthtoken', {}), ('testupdateuserroles', {}), ('testgetcorrectnextnumber', {'mode': 1, 'numbers': 3}), ('sendUpdateTextToAllAdmins', {}), ('sendDemoIsNoMoreToAllAdmins', {}), ('me', {}), ('permissionTest', {}), ('permissionTest2', {}), ('listPermissions', {}), ('database_sync', {})])
    async def test_non_admin_returns(self, cog: AdministrationCog, bot: MagicMock, method_name: str, extra_kwargs: dict[str, Any]) -> None:
        ctx = make_context(bot, author_id=NON_ADMIN_ID)
        method = getattr(cog, method_name)
        await method(ctx, **extra_kwargs)
        ctx.send.assert_not_called()

@pytest.mark.asyncio
class TestSync:

    async def test_sync_no_tree(self, cog: AdministrationCog, bot: MagicMock) -> None:
        bot.tree = None
        ctx = make_context(bot)
        await cog.sync(ctx)
        ctx.send.assert_not_called()

    async def test_sync_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        bot.tree = MagicMock()
        bot.tree.walk_commands = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        bot.tree.sync = AsyncMock(return_value=[MagicMock(), MagicMock()])
        status_msg = MagicMock()
        status_msg.edit = AsyncMock()
        ctx = make_context(bot)
        ctx.send = AsyncMock(return_value=status_msg)
        await cog.sync(ctx)
        ctx.send.assert_awaited_once()
        bot.tree.sync.assert_awaited_once()
        status_msg.edit.assert_awaited()

    async def test_sync_failure(self, cog: AdministrationCog, bot: MagicMock) -> None:
        bot.tree = MagicMock()
        bot.tree.walk_commands = MagicMock(return_value=[])
        bot.tree.sync = AsyncMock(side_effect=RuntimeError('discord down'))
        status_msg = MagicMock()
        status_msg.edit = AsyncMock()
        ctx = make_context(bot)
        ctx.send = AsyncMock(return_value=status_msg)
        await cog.sync(ctx)
        status_msg.edit.assert_awaited()
        assert status_msg.edit.await_args.kwargs['embed'] is not None

@pytest.mark.asyncio
class TestFeedbackCommands:

    async def test_feedback(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.addFeedback', new=AsyncMock()) as add_fb:
            await cog.feedback(ctx, content='test feedback')
        add_fb.assert_awaited_once_with('test feedback', ctx.author.name)
        ctx.send.assert_awaited_once()

    async def test_block_feedback(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        user = make_member(user_id=222222222, name='Blocked')
        with patch('extensions.administration.feedbackBlockUser', new=AsyncMock()) as block:
            await cog.blockFeedback(ctx, user=user)
        block.assert_awaited_once_with(222222222)
        ctx.send.assert_awaited_once()

    async def test_unblock_feedback(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        user = make_member(user_id=333333333, name='Unblocked')
        with patch('extensions.administration.feedbackUnblockUser', new=AsyncMock()) as unblock:
            await cog.unblockFeedback(ctx, user=user)
        unblock.assert_awaited_once_with(333333333)
        ctx.send.assert_awaited_once()

@pytest.mark.asyncio
class TestTestBot:

    async def test_diagnostics_unavailable(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', False):
            await cog.test_bot(ctx)
        sent.edit.assert_awaited()

    async def test_diagnostics_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.create_thread = AsyncMock(return_value=MagicMock(send=AsyncMock()))
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', True), patch('extensions.administration.DiagnosticsRunner', autospec=True) as mock_runner_cls:
            mock_runner = mock_runner_cls.return_value
            mock_runner.run_all = AsyncMock(side_effect=RuntimeError('diagnostics fail'))
            await cog.test_bot(ctx)
        sent.edit.assert_awaited()

    async def test_diagnostics_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.create_thread = AsyncMock(return_value=MagicMock(send=AsyncMock()))
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        mock_runner = MagicMock()
        mock_runner.run_all = AsyncMock()
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', True), patch('extensions.administration.DiagnosticsRunner', return_value=mock_runner):
            await cog.test_bot(ctx)
        mock_runner.run_all.assert_awaited_once()

@pytest.mark.asyncio
class TestBenchmarkBot:

    async def test_benchmark_unavailable(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', False):
            await cog.benchmark_bot(ctx)
        sent.edit.assert_awaited()

    async def test_benchmark_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.create_thread = AsyncMock(return_value=MagicMock(send=AsyncMock()))
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', True), patch.object(admin_mod, 'BenchmarkRunner', autospec=True) as mock_runner_cls:
            mock_runner = mock_runner_cls.return_value
            mock_runner.run_all = AsyncMock(side_effect=RuntimeError('benchmark fail'))
            await cog.benchmark_bot(ctx)
        sent.edit.assert_awaited()

    async def test_benchmark_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        sent = MagicMock()
        sent.create_thread = AsyncMock(return_value=MagicMock(send=AsyncMock()))
        sent.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=sent)
        mock_runner = MagicMock()
        mock_runner.run_all = AsyncMock()
        with patch.object(admin_mod, 'DIAGNOSTICS_AVAILABLE', True), patch.object(admin_mod, 'BenchmarkRunner', return_value=mock_runner):
            await cog.benchmark_bot(ctx)
        mock_runner.run_all.assert_awaited_once()

@pytest.mark.asyncio
class TestMiscCommands:

    async def test_test_translation(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        await cog.test_translation(ctx)
        ctx.send.assert_awaited_once()

    async def test_update_http_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        bot.application_id = 12345
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.text = AsyncMock(return_value='error body')

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.send_logEmbeds', new=AsyncMock()), patch('extensions.administration.create_database_backup', new=AsyncMock()), patch('extensions.administration.removeAllJoinToCreateChannels', new=AsyncMock()), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.update(ctx)
        assert ctx.send.await_count >= 2

    async def test_update_connection_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        bot.application_id = 12345
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=aiohttp.ClientError('connection refused'))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.send_logEmbeds', new=AsyncMock()), patch('extensions.administration.create_database_backup', new=AsyncMock()), patch('extensions.administration.removeAllJoinToCreateChannels', new=AsyncMock()), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.update(ctx)
        assert ctx.send.await_count >= 2

    async def test_update_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        bot.application_id = 12345
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value='restarting')

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.send_logEmbeds', new=AsyncMock()), patch('extensions.administration.create_database_backup', new=AsyncMock()), patch('extensions.administration.removeAllJoinToCreateChannels', new=AsyncMock()), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.update(ctx)
        assert ctx.send.await_count >= 2

    async def test_welcome_default_user(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.welcomeNewUser', new=AsyncMock()) as welcome:
            await cog.welcome(ctx)
        welcome.assert_awaited_once_with(ctx.author)

    async def test_welcome_explicit_user(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        member = make_member(user_id=777777777)
        with patch('extensions.administration.welcomeNewUser', new=AsyncMock()) as welcome:
            await cog.welcome(ctx, user=member)
        welcome.assert_awaited_once_with(member)

    async def test_farewell_default_user(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.farewellUser', new=AsyncMock()) as farewell:
            await cog.farewell(ctx)
        farewell.assert_awaited_once_with(ctx.author)

    async def test_farewell_explicit_user(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        member = make_member(user_id=888888888)
        with patch('extensions.administration.farewellUser', new=AsyncMock()) as farewell:
            await cog.farewell(ctx, user=member)
        farewell.assert_awaited_once_with(member)

    async def test_onething_command(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        emoji = MagicMock()
        bot.get_emoji = MagicMock(return_value=emoji)
        config.WELCOME_EMOJI_ID = 12345
        await cog.onethingaboutmeichfahrautoseitvierjahreneinestageswolltichindenclubfahnichstandaneinerrotenampelundichwarganzalleinhintermirwareinbusunderfihrmirreinerhuptemichanhuphupichschaumiranwaspassiertistunderkommtraus(ctx)
        ctx.send.assert_awaited_once()

    async def test_me(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        await cog.me(ctx)
        ctx.send.assert_awaited_once()

    async def test_permission_test(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        perms = MagicMock()
        perms.manage_messages = False
        perms.read_message_history = True
        perms.manage_channels = True
        ctx.channel.permissions_for = MagicMock(return_value=perms)
        await cog.permissionTest(ctx)
        ctx.send.assert_awaited_once()

    async def test_permission_test2(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        perms = MagicMock()
        perms.manage_messages = True
        ctx.channel.permissions_for = MagicMock(return_value=perms)
        await cog.permissionTest2(ctx)
        ctx.send.assert_awaited_once()

    async def test_list_permissions_default_channel(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        perms = MagicMock()
        perms.__iter__ = MagicMock(return_value=iter(['send_messages', 'read_messages']))
        ctx.channel.permissions_for = MagicMock(return_value=perms)
        await cog.listPermissions(ctx)
        ctx.send.assert_awaited_once()

    async def test_list_permissions_explicit_channel(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        channel = make_text_channel()
        perms = MagicMock()
        perms.__iter__ = MagicMock(return_value=iter(['manage_messages']))
        channel.permissions_for = MagicMock(return_value=perms)
        await cog.listPermissions(ctx, channel=channel)
        ctx.send.assert_awaited_once()

    async def test_setguildlocale(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.tanjunLocalizer.localize', return_value='locale set'):
            await cog.setguildlocale(ctx, locale='de')
        ctx.guild.edit.assert_awaited_once()
        ctx.send.assert_awaited_once()

    async def test_testgithubauthtoken(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.missingLocalization', new=AsyncMock()):
            await cog.testgithubauthtoken(ctx)
        ctx.send.assert_awaited_once()

    async def test_testupdateuserroles(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch('extensions.administration.update_user_roles', new=AsyncMock()) as update:
            await cog.testupdateuserroles(ctx)
        update.assert_awaited_once()

    async def test_testgetcorrectnextnumber(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        await cog.testgetcorrectnextnumber(ctx, mode=1, numbers=5)
        ctx.send.assert_awaited_once()

    async def test_editembedmessage(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        msg = MagicMock()
        msg.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=msg)
        with patch('extensions.administration.asyncio.sleep', new=AsyncMock()):
            await cog.editembedmessage(ctx)
        msg.edit.assert_awaited_once()

@pytest.mark.asyncio
class TestBrawlStars:

    async def test_get_brawlers_non_dict(self, cog: AdministrationCog) -> None:
        mock_resp = MagicMock()
        mock_resp.json = AsyncMock(return_value=[])

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            result = await cog.getBrawlers()
        assert result == {'items': []}

    async def test_get_acc_data_non_dict(self, cog: AdministrationCog) -> None:
        mock_resp = MagicMock()
        mock_resp.json = AsyncMock(return_value='not a dict')

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            result = await cog.getAccData('ABC')
        assert result == {}

    async def test_bsaccdata(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        with patch.object(cog, 'getAccData', new=AsyncMock(return_value={'brawlers': [{'name': 'a'}, {'name': 'b'}]})):
            await cog.bsaccdata(ctx, id='TAG')
        ctx.send.assert_awaited_once()

    async def test_bsstarpoweremojis_download_fail(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        brawlers = {'items': [{'star_powers': [{'id': 1, 'name': 'Power1'}]}]}
        mock_resp = MagicMock()
        mock_resp.status = 404

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsstarpoweremojis(ctx)
        ctx.send.assert_awaited()

    async def test_bsstarpoweremojis_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        emoji = MagicMock()
        ctx.guild.create_custom_emoji = AsyncMock(return_value=emoji)
        brawlers = {'items': [{'star_powers': [{'id': 1, 'name': 'Power1'}]}]}
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=b'png')

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsstarpoweremojis(ctx)
        ctx.send.assert_awaited()

    async def test_bsstarpoweremojis_exception(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        brawlers = {'items': [{'star_powers': [{'id': 1, 'name': 'Power1'}]}]}
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=TimeoutError())
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsstarpoweremojis(ctx)
        ctx.send.assert_awaited()

    async def test_bsstarpoweremojis_skip_start(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        brawlers = {'items': [{'star_powers': [{'id': 1, 'name': 'P0'}]}, {'star_powers': [{'id': 2, 'name': 'P1'}]}]}
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)):
            await cog.bsstarpoweremojis(ctx, start=1)

    async def test_bsgadgetsemojis_download_fail(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        brawlers = {'items': [{'gadgets': [{'id': 10, 'name': 'Gadget1'}]}]}
        mock_resp = MagicMock()
        mock_resp.status = 500

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsgadgetsemojis(ctx)
        ctx.send.assert_awaited()

    async def test_bsgadgetsemojis_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        emoji = MagicMock()
        ctx.guild.create_custom_emoji = AsyncMock(return_value=emoji)
        brawlers = {'items': [{'gadgets': [{'id': 10, 'name': 'Gadget1'}]}]}
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=b'png')

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsgadgetsemojis(ctx)
        ctx.send.assert_awaited()

    async def test_bsgadgetsemojis_exception(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        brawlers = {'items': [{'gadgets': [{'id': 10, 'name': 'Gadget1'}]}]}
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=aiohttp.ClientError('fail'))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch.object(cog, 'getBrawlers', new=AsyncMock(return_value=brawlers)), patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.bsgadgetsemojis(ctx)
        ctx.send.assert_awaited()

def _confirmation_msg(content: str, author: MagicMock, channel: MagicMock) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    msg.author = author
    msg.channel = channel
    return msg

@pytest.mark.asyncio
class TestBroadcastCommands:

    async def test_send_update_timeout(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(side_effect=TimeoutError())
        await cog.sendUpdateTextToAllAdmins(ctx)
        ctx.channel.send.assert_awaited()

    async def test_send_update_cancelled_first(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('n', ctx.author, ctx.channel))
        await cog.sendUpdateTextToAllAdmins(ctx)
        assert ctx.channel.send.await_count >= 2

    async def test_send_update_wrong_password(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        from localizer import tanjunLocalizer
        expected = locale.commands.admin.update_text.expected_password('en').lower()
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('wallah', ctx.author, ctx.channel), _confirmation_msg('wrong-password', ctx.author, ctx.channel)])
        await cog.sendUpdateTextToAllAdmins(ctx)
        assert ctx.channel.send.await_count >= 4

    async def test_send_update_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        from localizer import tanjunLocalizer
        expected = locale.commands.admin.update_text.expected_password('en').lower()
        owner = make_member(user_id=555555555)
        owner.send = AsyncMock()
        guild = make_guild()
        guild.owner = owner
        bot.guilds = [guild]
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('wallah', ctx.author, ctx.channel), _confirmation_msg(expected, ctx.author, ctx.channel)])
        await cog.sendUpdateTextToAllAdmins(ctx)
        owner.send.assert_awaited()

    async def test_send_update_wallah_cancel(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('no-wallah', ctx.author, ctx.channel)])
        await cog.sendUpdateTextToAllAdmins(ctx)
        assert ctx.channel.send.await_count >= 3

    async def test_send_update_second_confirm_timeout(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), TimeoutError()])
        await cog.sendUpdateTextToAllAdmins(ctx)

    async def test_send_demo_timeout(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(side_effect=TimeoutError())
        await cog.sendDemoIsNoMoreToAllAdmins(ctx)

    async def test_send_demo_cancelled(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('n', ctx.author, ctx.channel))
        await cog.sendDemoIsNoMoreToAllAdmins(ctx)

    async def test_send_demo_wrong_password(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('wallah', ctx.author, ctx.channel), _confirmation_msg('bad', ctx.author, ctx.channel)])
        await cog.sendDemoIsNoMoreToAllAdmins(ctx)

    async def test_send_demo_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        from localizer import tanjunLocalizer
        expected = locale.commands.admin.update_text.expected_password('en').lower()
        owner = make_member(user_id=666666666)
        owner.send = AsyncMock()
        guild = make_guild()
        guild.owner = owner
        bot.guilds = [guild, guild]
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('wallah', ctx.author, ctx.channel), _confirmation_msg(expected, ctx.author, ctx.channel)])
        await cog.sendDemoIsNoMoreToAllAdmins(ctx)
        owner.send.assert_awaited()

    async def test_send_update_no_owner(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        ctx.channel.send = AsyncMock()
        from localizer import tanjunLocalizer
        expected = locale.commands.admin.update_text.expected_password('en').lower()
        guild = make_guild()
        guild.owner = None
        bot.guilds = [guild]
        bot.wait_for = AsyncMock(side_effect=[_confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('y', ctx.author, ctx.channel), _confirmation_msg('wallah', ctx.author, ctx.channel), _confirmation_msg(expected, ctx.author, ctx.channel)])
        await cog.sendUpdateTextToAllAdmins(ctx)

@pytest.mark.asyncio
class TestDatabaseSync:

    async def test_no_attachment(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        await cog.database_sync(ctx)
        ctx.send.assert_awaited_once()

    async def test_with_url(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        mock_resp = MagicMock()
        mock_resp.status = 404

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')
        status.edit.assert_awaited()

    async def test_download_exception(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        mock_session = MagicMock()
        mock_session.get = MagicMock(side_effect=RuntimeError('download failed'))
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_schema_timeout(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(side_effect=TimeoutError())
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_schema_cancel(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        from localizer import tanjunLocalizer
        cancel = locale.commands.admin.database_sync.cancel_token('en')
        bot.wait_for = AsyncMock(return_value=_confirmation_msg(cancel, ctx.author, ctx.channel))
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_schema_warning_unknown(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('unknown_schema', ctx.author, ctx.channel))
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session), patch('extensions.administration.subprocess.run', side_effect=RuntimeError('dump fail')):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_full_import_success(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\nCREATE TABLE foo (id INT);\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('testdb', ctx.author, ctx.channel))
        attachment = MagicMock()
        attachment.url = 'http://example.com/dump.sql'
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session), patch('extensions.administration.subprocess.run'), patch('extensions.administration.discord.File', return_value=MagicMock()), patch('extensions.administration.os.path.exists', return_value=True), patch('extensions.administration.os.remove'), patch('extensions.administration.os.unlink'), patch('builtins.open', create=True) as mock_open:
            file_handle = MagicMock()
            file_handle.__enter__ = MagicMock(return_value=file_handle)
            file_handle.__exit__ = MagicMock(return_value=False)
            file_handle.write = MagicMock()
            file_handle.read = MagicMock(return_value='')
            mock_open.return_value = file_handle
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_import_subprocess_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('testdb', ctx.author, ctx.channel))
        import subprocess
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session), patch('extensions.administration.subprocess.run', side_effect=[None, subprocess.CalledProcessError(1, 'mysql')]), patch('extensions.administration.discord.File', return_value=MagicMock()), patch('extensions.administration.os.path.exists', return_value=True), patch('extensions.administration.os.remove'), patch('extensions.administration.os.unlink'), patch('builtins.open', create=True) as mock_open:
            file_handle = MagicMock()
            file_handle.__enter__ = MagicMock(return_value=file_handle)
            file_handle.__exit__ = MagicMock(return_value=False)
            file_handle.write = MagicMock()
            mock_open.return_value = file_handle
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_no_schema_in_dump(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'-- empty dump\nSELECT 1;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(side_effect=TimeoutError())
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

    async def test_with_attachment(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        attachment = MagicMock()
        attachment.url = 'http://example.com/from-attachment.sql'
        ctx.message.attachments = [attachment]
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        mock_resp = MagicMock()
        mock_resp.status = 500

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session):
            await cog.database_sync(ctx)

    async def test_filter_error(self, cog: AdministrationCog, bot: MagicMock) -> None:
        ctx = make_context(bot)
        status = MagicMock()
        status.edit = AsyncMock()
        ctx.channel.send = AsyncMock()
        ctx.send = AsyncMock(return_value=status)
        sql_content = b'CREATE DATABASE `testdb`;\nUSE `testdb`;\n'
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=sql_content)

        @asynccontextmanager
        async def mock_get(*_a: Any, **_k: Any):
            yield mock_resp
        mock_session = MagicMock()
        mock_session.get = mock_get
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        bot.wait_for = AsyncMock(return_value=_confirmation_msg('testdb', ctx.author, ctx.channel))
        real_open = open

        def failing_open(path: str, *args: Any, **kwargs: Any):
            if path == 'filtered_import.sql' and 'w' in args:
                raise OSError('cannot write filter')
            return real_open(path, *args, **kwargs)
        with patch('extensions.administration.aiohttp.ClientSession', return_value=mock_session), patch('extensions.administration.subprocess.run'), patch('extensions.administration.discord.File', return_value=MagicMock()), patch('extensions.administration.os.unlink'), patch('builtins.open', side_effect=failing_open):
            await cog.database_sync(ctx, url='http://example.com/dump.sql')

class TestHelpers:

    def test_mysql_defaults_file(self) -> None:
        path = _mysql_defaults_file('user', 'pass', 'host', 3306)
        try:
            with open(path) as f:
                content = f.read()
            assert 'user=user' in content
            assert 'password=pass' in content
        finally:
            import os
            os.unlink(path)

@pytest.mark.asyncio
async def test_setup_registers_cog() -> None:
    bot = MagicMock()
    bot.add_cog = AsyncMock()
    await admin_mod.setup(bot)
    bot.add_cog.assert_awaited_once()