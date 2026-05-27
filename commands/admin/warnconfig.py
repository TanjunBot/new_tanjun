import discord

import utility
from api import get_warn_config, set_warn_config
from localizer import tanjunLocalizer
from models import WarnConfigModel


async def warn_config(command_info: utility.CommandInfo) -> None:
    assert command_info.guild is not None
    config = await get_warn_config(command_info.guild.id)  # Retrieve current configuration settings

    class WarnConfigModal(discord.ui.Modal):
        def __init__(self, command_info: utility.CommandInfo, config: WarnConfigModel | None) -> None:
            super().__init__(title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warnconfig.modal.title"))
            self.command_info = command_info

            # Provide default values from the current configuration
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.warnexpiration.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.warnexpiration.placeholder",
                    ),
                    default=str(config.expiration_days) if config else "2",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.timeout_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.timeout_threshold.placeholder",
                    ),
                    default=str(config.timeout_threshold) if config else "2",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.timeout_duration.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.timeout_duration.placeholder",
                    ),
                    default=str(config.timeout_duration) if config else "60",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.kick_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.kick_threshold.placeholder",
                    ),
                    default=str(config.kick_threshold) if config else "5",
                    required=False,
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.ban_threshold.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.warnconfig.modal.ban_threshold.placeholder",
                    ),
                    default=str(config.ban_threshold) if config else "10",
                    required=False,
                )
            )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            # Parse input and update configurations
            try:
                expiration_days = int(self.children[0].value)  # type: ignore[attr-defined]
                timeout_threshold = int(self.children[1].value)  # type: ignore[attr-defined]
                timeout_duration = int(self.children[2].value)  # type: ignore[attr-defined]
                kick_threshold = int(self.children[3].value)  # type: ignore[attr-defined]
                ban_threshold = int(self.children[4].value)  # type: ignore[attr-defined]

                await set_warn_config(
                    interaction.guild_id,  # type: ignore[arg-type]
                    expiration_days=expiration_days,
                    timeout_threshold=timeout_threshold,
                    timeout_duration=timeout_duration,
                    kick_threshold=kick_threshold,
                    ban_threshold=ban_threshold,
                )

                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
                        "commands.admin.warnconfig.success.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
                        "commands.admin.warnconfig.success.description",
                    ),
                )
                await interaction.response.send_message(embed=embed)

            except ValueError:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(self.command_info.locale, "commands.admin.warnconfig.error.title"),  # type: ignore[misc]
                    description=tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
                        "commands.admin.warnconfig.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.warnconfig.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.warnconfig.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    # Display the modal with current config as default values
    modal = WarnConfigModal(command_info, config)
    await command_info.reply(modal)
