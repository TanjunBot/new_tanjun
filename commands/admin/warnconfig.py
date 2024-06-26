import discord
import utility
from localizer import tanjunLocalizer
from api import set_warn_config, get_warn_config


class WarnConfigModal(discord.ui.Modal):
    def __init__(self, commandInfo: utility.commandInfo):
        super().__init__(title="Warning Configuration")
        self.commandInfo = commandInfo

        self.add_item(
            discord.ui.TextInput(
                label="Warn Expiration",
                placeholder="Number of days until warns expire  (in days, 0 for no expiration), e.g. 30",
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Timeout Threshold",
                placeholder="Number of warns before timeout, e.g. 3",
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Timeout Duration",
                placeholder="Duration of timeout (in minutes), e.g. 60",
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Kick Threshold",
                placeholder="Number of warns before kick, e.g. 5",
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Ban Threshold",
                placeholder="Number of warns before ban, e.g. 10",
                required=True,
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            expiration_days = int(self.children[0].value)
            timeout_threshold = int(self.children[1].value)
            timeout_duration = int(self.children[2].value)
            kick_threshold = int(self.children[3].value)
            ban_threshold = int(self.children[4].value)

            set_warn_config(
                interaction.guild_id,
                expiration_days=expiration_days,
                timeout_threshold=timeout_threshold,
                timeout_duration=timeout_duration,
                kick_threshold=kick_threshold,
                ban_threshold=ban_threshold,
            )

            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.admin.warnconfig.success.title"
                ),
                description=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.warnconfig.success.description",
                ),
            )
            await interaction.response.send_message(embed=embed)

        except ValueError:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.admin.warnconfig.error.title"
                ),
                description=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.warnconfig.error.invalidInput",
                ),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def warn_config(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.warnconfig.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warnconfig.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Show current config
    config = get_warn_config(commandInfo.guild.id)
    if config:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.warnconfig.currentConfig.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warnconfig.currentConfig.description",
                expiration_days=config["expiration_days"],
                timeout_threshold=config["timeout_threshold"],
                timeout_duration=config["timeout_duration"]
                // 60,  # Convert back to minutes
                kick_threshold=config["kick_threshold"],
                ban_threshold=config["ban_threshold"],
            ),
        )
        await commandInfo.reply(embed=embed)

    # Show configuration modal
    modal = WarnConfigModal(commandInfo)
    await commandInfo.reply(modal)
