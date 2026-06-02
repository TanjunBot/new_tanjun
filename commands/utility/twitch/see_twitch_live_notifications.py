from locale_keys import locale
from typing import Any
import discord
from commands.utility.twitch.twitch_api import parse_twitch_notification_message
from services.twitch_service import get_twitch_service
from utility import CommandInfo, tanjunEmbed

async def seeTwitchLiveNotifications(command_info: CommandInfo) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.title(command_info.locale), description=locale.commands.utility.twitch.listTwitchLiveNotifications.error.missingPermissions.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    service = get_twitch_service()
    if service is None:
        embed = tanjunEmbed(title='Service Unavailable', description='Twitch service is not initialized.')
        await command_info.reply(embed=embed)
        return
    notifications = await service.get_notifications_by_guild(str(command_info.guild.id))
    if not notifications:
        embed = tanjunEmbed(title=locale.commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.title(command_info.locale), description=locale.commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.description(command_info.locale))
        await command_info.reply(embed=embed)
        return

    class TwitchLiveNotification(discord.ui.View):

        def __init__(self, page: int=0, notifications: list | None=None, command_info: CommandInfo | None=None) -> None:
            super().__init__()
            self.current_page = page
            self.notifications = notifications if notifications is not None else []
            self.command_info = command_info

        @discord.ui.button(label='⬅️', style=discord.ButtonStyle.secondary, disabled=len(notifications) <= 1)
        async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description(command_info.locale), ephemeral=True)
                return
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = len(self.notifications) - 1
            await self.update_message(interaction)

        @discord.ui.button(label='🗑️', style=discord.ButtonStyle.danger)
        async def delete_notification(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description(command_info.locale), ephemeral=True)
                return
            twitch_service = get_twitch_service()
            if twitch_service is None:
                await interaction.response.send_message('Twitch service is not available. Cannot delete notification.', ephemeral=True)
                return
            await twitch_service.remove_notification(self.notifications[self.current_page].id)
            self.notifications = await twitch_service.get_notifications_by_guild(str(command_info.guild.id))
            if not self.notifications:
                embed = tanjunEmbed(title=locale.commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.title(command_info.locale), description=locale.commands.utility.twitch.listTwitchLiveNotifications.error.noNotifications.description(command_info.locale))
                await interaction.response.edit_message(embed=embed)
                return
            self.current_page -= 1
            await self.update_message(interaction)

        @discord.ui.button(label='➡️', style=discord.ButtonStyle.secondary, disabled=len(notifications) <= 1)
        async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != self.command_info.user.id:
                await interaction.response.send_message(locale.commands.utility.twitch.listTwitchLiveNotifications.error.notYourNotification.description(command_info.locale), ephemeral=True)
                return
            self.current_page += 1
            if self.current_page >= len(self.notifications):
                self.current_page = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction) -> None:
            notification = parse_twitch_notification_message(self.notifications[self.current_page].notification_message, command_info.locale, self.notifications[self.current_page].twitch_name)
            if len(self.notifications) > 1:
                title = locale.commands.utility.twitch.listTwitchLiveNotifications.title(command_info.locale, current_page=self.current_page + 1, total_pages=len(self.notifications))
            else:
                title = locale.commands.utility.twitch.listTwitchLiveNotifications.titleNoPages(command_info.locale)
            embed = tanjunEmbed(title=title, description=locale.commands.utility.twitch.listTwitchLiveNotifications.description(command_info.locale, channel=self.notifications[self.current_page].id, twitch_name=self.notifications[self.current_page].twitch_name, message=notification))
            if len(self.notifications) > 1:
                view = TwitchLiveNotification(self.current_page, self.notifications, self.command_info)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.edit_message(embed=embed, view=view)
    view = TwitchLiveNotification(0, notifications, command_info)
    notification = parse_twitch_notification_message(notifications[0].notification_message, command_info.locale, notifications[0].twitch_name)
    if len(notifications) > 1:
        title = locale.commands.utility.twitch.listTwitchLiveNotifications.title(command_info.locale, current_page=1, total_pages=len(notifications))
    else:
        title = locale.commands.utility.twitch.listTwitchLiveNotifications.titleNoPages(command_info.locale)
    embed = tanjunEmbed(title=title, description=locale.commands.utility.twitch.listTwitchLiveNotifications.description(command_info.locale, channel=notifications[0].id, twitch_name=notifications[0].twitch_name, message=notification))
    await command_info.reply(embed=embed, view=view)