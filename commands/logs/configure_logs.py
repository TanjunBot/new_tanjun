from api import get_log_enable as get_log_enable_api, set_log_enable as set_log_enable_api
import utility
import discord
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
    "guildRoleUpdate"
]





async def configure_logs(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    log_enabled = list(await get_log_enable_api(commandInfo.guild.id))

    async def build_log_settings_embed(locale: str, guild: discord.Guild, selectedIndex: int):
        description = ""
        for index, option in enumerate(LOG_OPTIONS):
            localizedOption = tanjunLocalizer.localize(locale, f"commands.logs.configureLogs.configurationEmbed.{option}")
            enabled = log_enabled[index + 1]
            enabledLocalized = tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configurationEmbed.activated") if enabled else tanjunLocalizer.localize(locale, "commands.logs.configureLogs.configurationEmbed.deactivated")
            if index == selectedIndex:
                description += f"➤ {localizedOption}: {enabledLocalized}\n"
            else:
                description += f"{localizedOption}: {enabledLocalized}\n"
        return description

    if not log_enabled:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.configureLogs.noLogEnabled.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.configureLogs.noLogEnabled.description")
        )
        await commandInfo.reply(embed=embed)
        return

    selectedIndex = 0

    class logConfigureView(discord.ui.View):
        def __init__(self, locale: str, guild: discord.Guild, selectedIndex: int):
            super().__init__()
            self.locale = locale
            self.guild = guild
            self.selectedIndex = selectedIndex

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.configureLogs.configurationEmbed.activate"),
            style=discord.ButtonStyle.success,
            custom_id="activate",
            disabled=log_enabled[selectedIndex + 1] == 1 if log_enabled else False
        )
        async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selectedIndex, True)
            log_enabled[self.selectedIndex + 1] = 1
            await self.regenerate_embed(interaction)

        @discord.ui.button(
            label="⬆️",
            custom_id="up"
        )
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex -= 1
            if self.selectedIndex < 0:
                self.selectedIndex = len(LOG_OPTIONS) - 1
            global selectedIndex
            selectedIndex = self.selectedIndex
            await self.regenerate_embed(interaction)

        @discord.ui.button(
            label="⬇️",
            custom_id="down"
        )
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex += 1
            if self.selectedIndex >= len(LOG_OPTIONS):
                self.selectedIndex = 0
            global selectedIndex
            selectedIndex = self.selectedIndex
            await self.regenerate_embed(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.configureLogs.configurationEmbed.deactivate"),
            style=discord.ButtonStyle.danger,
            custom_id="deactivate",
            disabled=log_enabled[selectedIndex + 1] == 0 if log_enabled else False
        )
        async def deactivate(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.enable_disable_by_id(self.selectedIndex, False)
            log_enabled[self.selectedIndex + 1] = 0
            await self.regenerate_embed(interaction)

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
        
        async def regenerate_embed(self, interaction: discord.Interaction):
            description = await build_log_settings_embed(self.locale, self.guild, self.selectedIndex)
            self.embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.configureLogs.title"),
                description=description
            )
            self.children[0].disabled = log_enabled[self.selectedIndex + 1] == 1 if log_enabled else True  # Activate button
            self.children[3].disabled = log_enabled[self.selectedIndex + 1] == 0 if log_enabled else True  # Deactivate button
            await interaction.response.edit_message(embed=self.embed, view=self)

        async def enable_disable_by_id(self, id: int, enable: bool):
            await set_log_enable_api(self.guild.id, **{LOG_OPTIONS[id]: enable})

    configurationEmbed = await build_log_settings_embed(commandInfo.locale, commandInfo.guild, 0)
    view = logConfigureView(commandInfo.locale, commandInfo.guild, 0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.configureLogs.title"),
        description=configurationEmbed
    )
    await commandInfo.reply(embed=embed, view=view)