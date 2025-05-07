import discord

import utility
from api import get_warn_config, set_warn_config
from localizer import tanjunLocalizer


async def warn_config(commandInfo: utility.commandInfo):
    config = await get_warn_config(commandInfo.guild.id)  # Retrieve current configuration settings

    class WarnConfigModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo, config):
            super().__init__(title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.warnconfig.modal.title"))
            self.commandInfo = commandInfo

            # Provide default values from the current configuration
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.warnexpiration.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.warnexpiration.placeholder",
                    ),
                    default=str(config.get("expiration_days", "") or "2") if config else "2",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.timeout_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.timeout_threshold.placeholder",
                    ),
                    default=str(config.get("timeout_threshold", "") or "2") if config else "2",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.timeout_duration.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.timeout_duration.placeholder",
                    ),
                    default=str(config.get("timeout_duration", "") or "60") if config else "60",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.kick_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.kick_threshold.placeholder",
                    ),
                    default=str(config.get("kick_threshold", "") or "5") if config else "5",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.ban_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.ban_threshold.placeholder",
                    ),
                    default=str(config.get("ban_threshold", "") or "10") if config else "10",
                    required=False,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            # Parse input and update configurations
            try:
                expiration_days = int(self.children[0].value)
                timeout_threshold = int(self.children[1].value)
                timeout_duration = int(self.children[2].value)
                kick_threshold = int(self.children[3].value)
                ban_threshold = int(self.children[4].value)

                await set_warn_config(
                    interaction.guild_id,
                    expiration_days=expiration_days,
                    timeout_threshold=timeout_threshold,
                    timeout_duration=timeout_duration,
                    kick_threshold=kick_threshold,
                    ban_threshold=ban_threshold,
                )

                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.warnconfig.success.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.warnconfig.success.description",
                    ),
                )
                await interaction.response.send_message(embed=embed)

            except ValueError:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.warnconfig.error.title"),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.warnconfig.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.warnconfig.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warnconfig.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Display the modal with current config as default values
    modal = WarnConfigModal(commandInfo, config)
    await commandInfo.reply(modal)
