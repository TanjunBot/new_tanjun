import discord

import utility
from api import (
    get_log_enable as get_log_enable_api,
)
from api import (
    set_log_enable as set_log_enable_api,
)
from localizer import tanjunLocalizer

LOG_OPTIONS = [
    "automodRuleCreate",
    "automodRuleUpdate",
    "automodRuleDelete",
    "automodAction",
    "guild_channelDelete",
    "guild_channelCreate",
    "guild_channelUpdate",
    "guildUpdate",
    "inviteCreate",
    "inviteDelete",
    "memberJoin",
    "memberLeave",
    "memberUpdate",
    "userUpdate",
    "memberBan",
    "memberUnban",
    "presenceUpdate",
    "messageEdit",
    "messageDelete",
    "reactionAdd",
    "reactionRemove",
    "guildRoleCreate",
    "guildRoleDelete",
    "guildRoleUpdate",
]


async def configure_logs(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.setLogChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    log_enabled = await get_log_enable_api(command_info.guild.id)

    async def build_log_settings_embed(locale: str, guild: discord.Guild, selected_index: int):
        description = ""
        for index, option in enumerate(LOG_OPTIONS):
            localized_option = tanjunLocalizer.localize(locale, f"commands.logs.configureLogs.configuration_embed.{option}")
            enabled = log_enabled.get_option(index)
            enabled_localized = (
                tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configuration_embed.activated")
                if enabled
                else tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configuration_embed.deactivated")
            )
            if index == selected_index:
                description += f"➤ {localized_option}: {enabled_localized}\n"
            else:
                description += f"{localized_option}: {enabled_localized}\n"
        return description

    selected_index = 0

    class LogConfigureView(discord.ui.View):
        def __init__(self, locale: str, guild: discord.Guild, selected_index: int):
            super().__init__()
            self.locale = locale
            self.guild = guild
            self.selected_index = selected_index

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.configureLogs.configuration_embed.activate",
            ),
            style=discord.ButtonStyle.success,
            custom_id="activate",
            disabled=log_enabled.get_option(selected_index) if log_enabled else False,
        )
        async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selected_index, True)
            log_enabled.set_option(self.selected_index, True)
            await self.regenerate_embed(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = len(LOG_OPTIONS) - 1
            global selected_index
            selected_index = self.selected_index
            await self.regenerate_embed(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index += 1
            if self.selected_index >= len(LOG_OPTIONS):
                self.selected_index = 0
            global selected_index
            selected_index = self.selected_index
            await self.regenerate_embed(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.configureLogs.configuration_embed.deactivate",
            ),
            style=discord.ButtonStyle.danger,
            custom_id="deactivate",
            disabled=not log_enabled.get_option(selected_index) if log_enabled else False,
        )
        async def deactivate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selected_index, False)
            log_enabled.set_option(self.selected_index, False)
            await self.regenerate_embed(interaction)

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            if self.message:
                await self.message.edit(view=self)

        async def regenerate_embed(self, interaction: discord.Interaction):
            description = await build_log_settings_embed(self.locale, self.guild, self.selected_index)
            self.embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.configureLogs.title"),
                description=description,
            )
            self.children[0].disabled = log_enabled.get_option(self.selected_index) if log_enabled else True  # Activate button
            self.children[3].disabled = (
                not (log_enabled.get_option(self.selected_index)) if log_enabled else True
            )  # Deactivate button
            await interaction.response.edit_message(embed=self.embed, view=self)

        async def enable_disable_by_id(self, id: int, enable: bool):
            await set_log_enable_api(self.guild.id, **{LOG_OPTIONS[id]: enable})

    configuration_embed = await build_log_settings_embed(command_info.locale, command_info.guild, 0)
    view = LogConfigureView(command_info.locale, command_info.guild, 0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.logs.configureLogs.title"),
        description=configuration_embed,
    )
    message = await command_info.reply(embed=embed, view=view)
    if message:
        view.message = message
