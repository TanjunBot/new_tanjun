from typing import Any

import discord

from api import get_twitch_notification_by_guild_id, remove_twitch_online_notification
from commands.utility.twitch.twitchApi import (
    parse_twitch_notification_message,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def seeTwitchLiveNotifications(commandInfo: CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    notifications = await get_twitch_notification_by_guild_id(commandInfo.guild.id)  # type: ignore[union-attr]

    if not notifications:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    class TwitchLiveNotification(discord.ui.View):
        def __init__(self, page: int = 0, notifications: list = notifications) -> None:  # type: ignore[type-arg, assignment]
            super().__init__()
            self.current_page = page
            self.notifications = notifications

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary, disabled=len(notifications) <= 1)  # type: ignore[arg-type]
        async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not interaction.user.id == CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description",
                    ),
                    ephemeral=True,
                )
                return
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = len(self.notifications) - 1
            await self.update_message(interaction)

        @discord.ui.button(label="🗑️", style=discord.ButtonStyle.danger)
        async def delete_notification(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not interaction.user.id == CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description",
                    ),
                    ephemeral=True,
                )
                return
            global notifications
            await remove_twitch_online_notification(self.notifications[self.current_page][0])
            self.notifications = await get_twitch_notification_by_guild_id(commandInfo.guild.id)  # type: ignore[assignment, union-attr]
            if not self.notifications:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.description",
                    ),
                )
                await interaction.response.edit_message(embed=embed)
                return

            self.current_page -= 1
            await self.update_message(interaction)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary, disabled=len(notifications) <= 1)  # type: ignore[arg-type]
        async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not interaction.user.id == CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description",
                    ),
                    ephemeral=True,
                )
                return
            self.current_page += 1
            if self.current_page >= len(self.notifications):
                self.current_page = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction) -> None:
            notification = parse_twitch_notification_message(
                notifications[self.current_page][5],  # type: ignore[index]
                CommandInfo.locale,  # type: ignore[misc]
                notifications[self.current_page][4],  # type: ignore[index]
            )
            if len(self.notifications) > 1:
                title = tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.twitch.listTwitchLiveNotifications.title",
                    current_page=self.current_page + 1,
                    total_pages=len(self.notifications),
                )
            else:
                title = tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.twitch.listTwitchLiveNotifications.titleNoPages",
                )
            embed = tanjunEmbed(
                title=title,
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.twitch.listTwitchLiveNotifications.description",
                    channel=self.notifications[self.current_page][0],
                    twitch_name=self.notifications[self.current_page][4],
                    message=notification,
                ),
            )
            if len(self.notifications) > 1:
                view = TwitchLiveNotification(self.current_page, self.notifications)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.edit_message(embed=embed, view=view)  # type: ignore[used-before-def]

    view = TwitchLiveNotification(0, notifications)
    notification = parse_twitch_notification_message(
        notifications[0][5],
        CommandInfo.locale,  # type: ignore[misc]
        notifications[0][4],
    )
    if len(notifications) > 1:
        title = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.twitch.listTwitchLiveNotifications.title",
            current_page=1,
            total_pages=len(notifications),
        )
    else:
        title = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.twitch.listTwitchLiveNotifications.titleNoPages",
        )
    embed = tanjunEmbed(
        title=title,
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.twitch.listTwitchLiveNotifications.description",
            channel=notifications[0][0],
            twitch_name=notifications[0][4],
            message=notification,
        ),
    )
    await commandInfo.reply(embed=embed, view=view)
