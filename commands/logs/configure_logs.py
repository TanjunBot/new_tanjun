from locale_keys import locale as l10n
import discord
import utility
from api import get_log_enable as get_log_enable_api
from api import set_log_enable as set_log_enable_api
LOG_OPTIONS = ['automodRuleCreate', 'automodRuleUpdate', 'automodRuleDelete', 'automodAction', 'guild_channelDelete', 'guild_channelCreate', 'guild_channelUpdate', 'guildUpdate', 'inviteCreate', 'inviteDelete', 'memberJoin', 'memberLeave', 'memberUpdate', 'userUpdate', 'memberBan', 'memberUnban', 'presenceUpdate', 'messageEdit', 'messageDelete', 'reactionAdd', 'reactionRemove', 'guildRoleCreate', 'guildRoleDelete', 'guildRoleUpdate']

async def configure_logs(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(title=l10n.commands.logs.setLogChannel.missingPermission.title(command_info.locale), description=l10n.commands.logs.setLogChannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    log_enabled = await get_log_enable_api(command_info.guild.id)
    config_embed = l10n.commands.logs.configureLogs.configuration_embed

    async def build_log_settings_embed(loc: str, guild: discord.Guild, selected_index: int):
        description = ''
        for index, option in enumerate(LOG_OPTIONS):
            localized_option = getattr(config_embed, option)(loc)
            enabled = log_enabled.get_option(index)
            enabled_localized = config_embed.activated(loc) if enabled else config_embed.deactivated(loc)
            if index == selected_index:
                description += f'➤ {localized_option}: {enabled_localized}\n'
            else:
                description += f'{localized_option}: {enabled_localized}\n'
        return description
    selected_index = 0

    class LogConfigureView(discord.ui.View):

        def __init__(self, loc: str, guild: discord.Guild, selected_index: int):
            super().__init__()
            self.loc = loc
            self.guild = guild
            self.selected_index = selected_index

        @discord.ui.button(label=l10n.commands.logs.configureLogs.configuration_embed.activate(command_info.locale), style=discord.ButtonStyle.success, custom_id='activate', disabled=log_enabled.get_option(selected_index) if log_enabled else False)
        async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selected_index, True)
            log_enabled.set_option(self.selected_index, True)
            await self.regenerate_embed(interaction)

        @discord.ui.button(label='⬆️', custom_id='up')
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = len(LOG_OPTIONS) - 1
            global selected_index
            selected_index = self.selected_index
            await self.regenerate_embed(interaction)

        @discord.ui.button(label='⬇️', custom_id='down')
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index += 1
            if self.selected_index >= len(LOG_OPTIONS):
                self.selected_index = 0
            global selected_index
            selected_index = self.selected_index
            await self.regenerate_embed(interaction)

        @discord.ui.button(label=l10n.commands.logs.configureLogs.configuration_embed.deactivate(command_info.locale), style=discord.ButtonStyle.danger, custom_id='deactivate', disabled=not log_enabled.get_option(selected_index) if log_enabled else False)
        async def deactivate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selected_index, False)
            log_enabled.set_option(self.selected_index, False)
            await self.regenerate_embed(interaction)

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

        async def regenerate_embed(self, interaction: discord.Interaction):
            description = await build_log_settings_embed(self.loc, self.guild, self.selected_index)
            self.embed = utility.tanjunEmbed(title=l10n.commands.logs.configureLogs.title(self.loc), description=description)
            self.children[0].disabled = log_enabled.get_option(self.selected_index) if log_enabled else True
            self.children[3].disabled = not log_enabled.get_option(self.selected_index) if log_enabled else True
            await interaction.response.edit_message(embed=self.embed, view=self)

        async def enable_disable_by_id(self, id: int, enable: bool):
            await set_log_enable_api(self.guild.id, **{LOG_OPTIONS[id]: enable})
    configuration_embed = await build_log_settings_embed(command_info.locale, command_info.guild, 0)
    view = LogConfigureView(command_info.locale, command_info.guild, 0)
    embed = utility.tanjunEmbed(title=l10n.commands.logs.configureLogs.title(command_info.locale), description=configuration_embed)
    await command_info.reply(embed=embed, view=view)
