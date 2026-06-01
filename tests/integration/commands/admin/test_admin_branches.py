from locale_keys import locale
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from commands.admin.addrole import addrole
from commands.admin.boosterrole import create_booster_role
from commands.admin.copy_emoji import copy_emoji
from commands.admin.createemoji import create_emoji
from commands.admin.ticket.open_ticket import openTicket
from tests.helpers.discord import make_interaction, make_permissions, make_role, make_target_member
from tests.integration.commands.admin.conftest import make_aiohttp_session
pytestmark = pytest.mark.asyncio
_SAMPLE = '<:e:123456789012345678>'

@pytest.mark.parametrize('emoji_input', ['no emoji', 'plain text', ':notvalid:'])
async def test_copy_emoji_invalid_inputs(emoji_command_info, emoji_input):
    await copy_emoji(emoji_command_info, emoji=emoji_input)
    emoji_command_info.reply.assert_awaited_once()

@pytest.mark.parametrize('color', ['FF0000', '#00FF00', '0000FF', 'AABBCC'])
async def test_createrole_valid_colors(admin_command_info, color):
    from commands.admin.createrole import createrole
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    new_role = make_role(name=f'Role{color}')
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await createrole(admin_command_info, name=f'Role{color}', color=color)
    admin_command_info.reply.assert_awaited_once()

@pytest.mark.parametrize('reason', ['spam', 'harassment', 'nsfw', None])
@patch('commands.admin.warn.get_warnings')
@patch('commands.admin.warn.add_warning', new_callable=AsyncMock)
@patch('commands.admin.warn.get_warn_config', new_callable=AsyncMock)
async def test_warn_user_various_reasons(mock_config, mock_add, mock_warnings, admin_command_info, reason):
    from commands.admin.warn import warn_user
    from tests.helpers.discord import make_warn_config
    from tests.integration.commands.admin.conftest import async_iter_from
    mock_config.return_value = make_warn_config(ban_threshold=100)
    mock_warnings.return_value = async_iter_from([])
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason=reason)
    mock_add.assert_awaited_once()

@pytest.mark.parametrize('threshold', [1, 2, 3, 5])
@patch('commands.admin.warn.get_warnings')
@patch('commands.admin.warn.add_warning', new_callable=AsyncMock)
@patch('commands.admin.warn.get_warn_config', new_callable=AsyncMock)
async def test_warn_user_timeout_levels(mock_config, mock_add, mock_warnings, admin_command_info, threshold):
    from commands.admin.warn import warn_user
    from tests.helpers.discord import make_warn_config
    from tests.integration.commands.admin.conftest import async_iter_from
    mock_config.return_value = make_warn_config(ban_threshold=100, kick_threshold=100, timeout_threshold=threshold, timeout_duration=10)
    warnings = [MagicMock() for _ in range(threshold)]
    mock_warnings.return_value = async_iter_from(warnings)
    member = make_target_member(top_role_position=1)
    await warn_user(admin_command_info, member, reason='test')
    if threshold <= len(warnings):
        member.timeout.assert_awaited_once()

async def test_addrole_forbidden_on_add(admin_command_info):
    import discord as discord_mod
    user = make_target_member()
    role = make_role(position=5)
    user.roles = []
    user.add_roles = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), 'forbidden'))
    with pytest.raises(discord_mod.Forbidden):
        await addrole(admin_command_info, user, role)

@patch('commands.admin.boosterrole.booster_service')
async def test_booster_role_various_positions(mock_service, admin_command_info):
    mock_service.add = AsyncMock()
    admin_command_info.client.user = MagicMock(id=111)
    for pos in [1, 5, 10, 20]:
        role = make_role(position=pos)
        role.permissions = MagicMock(administrator=False)
        await create_booster_role(admin_command_info, role=role)
    assert admin_command_info.reply.await_count == 4

@patch('aiohttp.ClientSession')
@pytest.mark.parametrize('status', [200, 404, 500, 403])
async def test_create_emoji_http_statuses(mock_session_cls, emoji_command_info, status):
    mock_session_cls.return_value = make_aiohttp_session(status=status)
    await create_emoji(emoji_command_info, name='e', image_url='https://example.com/e.png')
    emoji_command_info.reply.assert_awaited_once()

@patch('commands.admin.ticket.open_ticket.check_if_opted_out', new_callable=AsyncMock, return_value=True)
async def test_open_ticket_opted_out_view_has_buttons(mock_optout):
    interaction = make_interaction()
    interaction.data = {'custom_id': 'ticket_create;1'}
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    await openTicket(interaction)
    call = interaction.followup.send.await_args
    assert call.kwargs.get('view') is not None

@pytest.mark.parametrize('name', ['Support', 'Help Desk', 'Billing', 'Technical'])
@patch('commands.admin.ticket.create_ticket.ticket_service')
async def test_create_ticket_various_names(mock_service, admin_command_info, name):
    from commands.admin.ticket.create_ticket import create_ticket
    from tests.helpers.discord import make_text_channel
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    mock_service.create_config = AsyncMock(return_value=1)
    await create_ticket(admin_command_info, channel=channel, name=name, description='desc')
    channel.send.assert_awaited_once()

@pytest.mark.parametrize('trigger,response', [('hello', 'hi there'), ('ping', 'pong'), ('help', 'need assistance?'), ('rules', 'read #rules')])
@patch('commands.admin.trigger_messages.add.trigger_message_service')
async def test_add_trigger_various_pairs(mock_service, admin_command_info, trigger, response):
    from commands.admin.trigger_messages.add import add_trigger_message
    mock_service.create = AsyncMock()
    await add_trigger_message(admin_command_info, trigger=trigger, response=response)
    mock_service.create.assert_awaited_once()

@pytest.mark.parametrize('role_name', ['Mod', 'Admin', 'Member', 'Guest', 'VIP'])
async def test_deleterole_various_roles(admin_command_info, role_name):
    from commands.admin.deleterole import deleterole
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    role = make_role(position=1, name=role_name)
    role.delete = AsyncMock()
    await deleterole(admin_command_info, role=role, reason=f'remove {role_name}')
    role.delete.assert_awaited_once()

@pytest.mark.parametrize('days', [1, 7, 14, 30, 90])
@patch('commands.admin.warnconfig.get_warn_config', new_callable=AsyncMock)
async def test_warn_config_various_expiration(mock_get, admin_command_info, days):
    from commands.admin.warnconfig import warn_config
    from tests.helpers.discord import make_warn_config
    mock_get.return_value = make_warn_config(expiration_days=days)
    await warn_config(admin_command_info)
    admin_command_info.reply.assert_awaited_once()

@pytest.mark.parametrize('page', [0, 1, 2])
@patch('commands.admin.viewwarns.get_detailed_warnings')
async def test_view_warnings_pagination_embed(mock_get, admin_command_info, page):
    from commands.admin.viewwarns import create_warnings_embed
    from tests.helpers.discord import make_target_member
    from tests.integration.commands.admin.conftest import make_detailed_warning
    warnings = [make_detailed_warning(warning_id=i) for i in range(12)]
    member = make_target_member()
    embed = create_warnings_embed(admin_command_info, member, warnings, page)
    assert embed is not None

@patch('commands.admin.copy_emoji.aiohttp.ClientSession')
async def test_copy_emoji_mixed_results(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.create_custom_emoji = AsyncMock(side_effect=[MagicMock(__str__=lambda s: '<:a:1>'), RuntimeError('fail')])
    await copy_emoji(emoji_command_info, emoji=f'{_SAMPLE} {_SAMPLE}')
    emoji_command_info.reply.assert_awaited_once()

@pytest.mark.parametrize('copy_members', [True, False])
async def test_copyrole_copy_members_flag(admin_command_info, copy_members):
    from commands.admin.copyrole import copyrole
    from tests.integration.commands.admin.test_copyrole import _setup_source_role
    role = make_role()
    _setup_source_role(role)
    if copy_members:
        role.members = [make_target_member()]
    new_role = make_role()
    new_role.edit = AsyncMock()
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await copyrole(admin_command_info, role=role, copy_members=copy_members)
    admin_command_info.reply.assert_awaited_once()

@pytest.mark.parametrize('locale', ['en-US', 'de', 'fr', 'es-ES'])
@patch('commands.admin.join_to_create.jointocreatechannel.set_join_to_create_channel', new_callable=AsyncMock)
@patch('commands.admin.join_to_create.jointocreatechannel.get_join_to_create_channel', new_callable=AsyncMock, return_value=None)
async def test_jointocreate_various_locales(mock_get, mock_set, admin_command_info, locale):
    from commands.admin.join_to_create.jointocreatechannel import jointocreatechannel
    from tests.helpers.discord import make_text_channel
    admin_command_info.locale = locale
    channel = make_text_channel(guild=admin_command_info.guild)
    await jointocreatechannel(admin_command_info, channel=channel)
    mock_set.assert_awaited_once()