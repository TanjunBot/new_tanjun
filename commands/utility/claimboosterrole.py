from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_booster_role
import utility
import discord

async def optIn(commandInfo: commandInfo):

    class WarnConfigModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo, config):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.warnconfig.modal.title"
                )
            )
            self.commandInfo = commandInfo

            # Provide default values from the current configuration
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.warn_expiration.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.warnconfig.modal.warn_expiration.placeholder",
                    ),
                    default=str(
                        config.get("expiration_days", "")
                    ),  # Provide current setting or empty string if not set
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
                    default=str(config.get("timeout_threshold", "") or "2"),
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
                    default=str(config.get("timeout_duration", "") or "3600"),
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
                    default=str(config.get("kick_threshold", "") or "5"),
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
                    default=str(config.get("ban_threshold", "") or "10"),
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

    if not commandInfo.user.premium_since:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.claimboosterrole.nobooster.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.nobooster.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    booster_role = await get_booster_role(commandInfo.guild.id)
    if not booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.no_booster_role.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    role = commandInfo.guild.get_role(booster_role)
    if not role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.role_not_found.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await commandInfo.user.add_roles(role)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.claimboosterrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.claimboosterrole.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)
