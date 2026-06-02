from locale_keys import locale
import discord
import utility
from api import get_warn_config, set_warn_config
from models import WarnConfigModel

async def warn_config(command_info: utility.CommandInfo) -> None:
    assert command_info.guild is not None
    config = await get_warn_config(command_info.guild.id)

    class WarnConfigModal(discord.ui.Modal):

        def __init__(self, command_info: utility.CommandInfo, config: WarnConfigModel | None) -> None:
            super().__init__(title=locale.commands.admin.warnconfig.modal.title(str(command_info.locale)))
            self.command_info = command_info
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.warnconfig.modal.warnexpiration.label(command_info.locale), placeholder=locale.commands.admin.warnconfig.modal.warnexpiration.placeholder(command_info.locale), default=str(config.expiration_days) if config else '2', required=False))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.warnconfig.modal.timeout_threshold.label(command_info.locale), placeholder=locale.commands.admin.warnconfig.modal.timeout_threshold.placeholder(command_info.locale), default=str(config.timeout_threshold) if config else '2', required=False))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.warnconfig.modal.timeout_duration.label(command_info.locale), placeholder=locale.commands.admin.warnconfig.modal.timeout_duration.placeholder(command_info.locale), default=str(config.timeout_duration) if config else '60', required=False))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.warnconfig.modal.kick_threshold.label(command_info.locale), placeholder=locale.commands.admin.warnconfig.modal.kick_threshold.placeholder(command_info.locale), default=str(config.kick_threshold) if config else '5', required=False))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.warnconfig.modal.ban_threshold.label(command_info.locale), placeholder=locale.commands.admin.warnconfig.modal.ban_threshold.placeholder(command_info.locale), default=str(config.ban_threshold) if config else '10', required=False))

        async def on_submit(self, interaction: discord.Interaction) -> None:
            try:
                expiration_days = int(self.children[0].value)
                timeout_threshold = int(self.children[1].value)
                timeout_duration = int(self.children[2].value)
                kick_threshold = int(self.children[3].value)
                ban_threshold = int(self.children[4].value)
                await set_warn_config(interaction.guild_id, expiration_days=expiration_days, timeout_threshold=timeout_threshold, timeout_duration=timeout_duration, kick_threshold=kick_threshold, ban_threshold=ban_threshold)
                embed = utility.tanjunEmbed(title=locale.commands.admin.warnconfig.success.title(self.command_info.locale), description=locale.commands.admin.warnconfig.success.description(self.command_info.locale))
                await interaction.response.send_message(embed=embed)
            except ValueError:
                embed = utility.tanjunEmbed(title=locale.commands.admin.warnconfig.error.title(self.command_info.locale), description=locale.commands.admin.warnconfig.error.invalidInput(self.command_info.locale))
                await interaction.response.send_message(embed=embed, ephemeral=True)
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.admin.warnconfig.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.warnconfig.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    modal = WarnConfigModal(command_info, config)
    await command_info.reply(modal)