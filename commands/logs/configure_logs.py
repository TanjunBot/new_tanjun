from typing import Any

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
    "guildChannelDelete",
    "guildChannelCreate",
    "guildChannelUpdate",
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


async def configure_logs(commandInfo: utility.CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    log_enabled = list(await get_log_enable_api(commandInfo.guild.id))

    async def build_log_settings_embed(locale: str, guild: discord.Guild, selectedIndex: int) -> None:
        description = ""
        for index, option in enumerate(LOG_OPTIONS):
            localizedOption = tanjunLocalizer.localize(locale, f"commands.logs.configureLogs.configurationEmbed.{option}")
            enabled = log_enabled[index + 1]
            enabledLocalized = (
                tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configurationEmbed.activated")
                if enabled
                else tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configurationEmbed.deactivated")
            )
            if index == selectedIndex:
                description += f"➤ {localizedOption}: {enabledLocalized}\n"
            else:
                description += f"{localizedOption}: {enabledLocalized}\n"
        return description  # type: ignore[return-value]

    if not log_enabled:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.configureLogs.noLogEnabled.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.configureLogs.noLogEnabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    selectedIndex = 0

    class logConfigureView(discord.ui.View):
        def __init__(self, locale: str, guild: discord.Guild, selectedIndex: int) -> None:
            super().__init__()
            self.locale = locale
            self.guild = guild
            self.selectedIndex = selectedIndex

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.configureLogs.configurationEmbed.activate",
            ),
            style=discord.ButtonStyle.success,
            custom_id="activate",
            disabled=log_enabled[selectedIndex + 1] == 1 if log_enabled else False,
        )
        async def activate(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await self.enable_disable_by_id(self.selectedIndex, True)
            log_enabled[self.selectedIndex + 1] = 1
            await self.regenerate_embed(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            self.selectedIndex -= 1
            if self.selectedIndex < 0:
                self.selectedIndex = len(LOG_OPTIONS) - 1
            global selectedIndex
            selectedIndex = self.selectedIndex  # type: ignore[name-defined]
            await self.regenerate_embed(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            self.selectedIndex += 1
            if self.selectedIndex >= len(LOG_OPTIONS):
                self.selectedIndex = 0
            global selectedIndex
            selectedIndex = self.selectedIndex  # type: ignore[name-defined]
            await self.regenerate_embed(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.configureLogs.configurationEmbed.deactivate",
            ),
            style=discord.ButtonStyle.danger,
            custom_id="deactivate",
            disabled=log_enabled[selectedIndex + 1] == 0 if log_enabled else False,
        )
        async def deactivate(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await self.enable_disable_by_id(self.selectedIndex, False)
            log_enabled[self.selectedIndex + 1] = 0
            await self.regenerate_embed(interaction)

        async def on_timeout(self) -> None:
            for item in self.children:
                item.disabled = True  # type: ignore[attr-defined]
            await self.message.edit(view=self)  # type: ignore[attr-defined]

        async def regenerate_embed(self, interaction: discord.Interaction) -> None:
            description = await build_log_settings_embed(self.locale, self.guild, self.selectedIndex)  # type: ignore[func-returns-value]
            self.embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.configureLogs.title"),
                description=description,
            )
            self.children[0].disabled = log_enabled[self.selectedIndex + 1] == 1 if log_enabled else True  # type: ignore[attr-defined]
            self.children[3].disabled = log_enabled[self.selectedIndex + 1] == 0 if log_enabled else True  # type: ignore[attr-defined]
            await interaction.response.edit_message(embed=self.embed, view=self)

        async def enable_disable_by_id(self, id: int, enable: bool) -> None:
            await set_log_enable_api(self.guild.id, **{LOG_OPTIONS[id]: enable})

    configurationEmbed = await build_log_settings_embed(commandInfo.locale, commandInfo.guild, 0)  # type: ignore[func-returns-value]
    view = logConfigureView(commandInfo.locale, commandInfo.guild, 0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.configureLogs.title"),
        description=configurationEmbed,
    )
    await commandInfo.reply(embed=embed, view=view)
