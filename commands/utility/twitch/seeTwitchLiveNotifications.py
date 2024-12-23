from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_twitch_notification_by_guild_id, remove_twitch_online_notification
import discord
from commands.utility.twitch.twitchApi import (
    get_uuid_by_twitch_name,
    subscribe_to_twitch_online_notification,
    parse_twitch_notification_message,
)


async def seeTwitchLiveNotifications(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
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

    notifications = await get_twitch_notification_by_guild_id(commandInfo.guild.id)

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
        def __init__(self, page: int = 0, notifications: list = notifications):
            super().__init__()
            self.current_page = page
            self.notifications = notifications

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous_page(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = len(self.notifications) - 1
            await self.update_message(interaction)

        @discord.ui.button(label="🗑️", style=discord.ButtonStyle.danger)
        async def delete_notification(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            global notifications
            await remove_twitch_online_notification(self.notifications[self.current_page][0])
            self.notifications = await get_twitch_notification_by_guild_id(
                commandInfo.guild.id
            )
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

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next_page(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.current_page += 1
            if self.current_page >= len(self.notifications):
                self.current_page = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction):
            notification = parse_twitch_notification_message(
                notifications[self.current_page][5],
                commandInfo.locale,
                notifications[self.current_page][4],
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
                await interaction.response.edit_message(embed=embed, view=discord.ui.View())

    view = TwitchLiveNotification(0, notifications)
    notification = parse_twitch_notification_message(
        notifications[0][5],
        commandInfo.locale,
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
        view = discord.ui.View()
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
