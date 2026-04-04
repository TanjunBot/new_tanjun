import discord  # type: ignore[import-not-found]

import utility
from api import (
    add_log_user_blacklist as add_log_blacklist_user_api,
)
from api import (
    get_log_user_blacklist as get_log_blacklist_users_api,
)
from api import (
    remove_log_user_blacklist as remove_log_blacklist_user_api,
)
from localizer import tanjunLocalizer


async def blacklist_list_user(commandInfo: utility.CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistListUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistListUser.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    blacklisted_users = await get_log_blacklist_users_api(commandInfo.guild.id)

    class BlacklistView(discord.ui.View):  # type: ignore[misc,no-any-unimported]
        def __init__(self, users: list, locale: str, guild: discord.Guild) -> None:  # type: ignore[no-any-unimported,type-arg]
            super().__init__()
            self.users = users
            self.locale = locale
            self.guild = guild
            self.selectedIndex = 0

        @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)  # type: ignore[untyped-decorator]
        async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,name-defined,no-any-unimported]
            user_id = self.users[self.selectedIndex][0]
            await remove_log_blacklist_user_api(self.guild.id, user_id)
            self.users = tuple(x for x in self.users if x[0] != user_id)  # type: ignore[assignment]
            await self.update_view(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")  # type: ignore[untyped-decorator]
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,name-defined,no-any-unimported]
            self.selectedIndex = (self.selectedIndex - 1) % len(self.users)
            await self.update_view(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")  # type: ignore[untyped-decorator]
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,name-defined,no-any-unimported]
            self.selectedIndex = (self.selectedIndex + 1) % len(self.users)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:  # type: ignore[no-any-unimported]
            from typing import Any, cast

            data = cast(Any, interaction.data)
            if data["component_type"] == 5:  # UserSelect
                userId = data["values"][0]
                await add_log_blacklist_user_api(self.guild.id, userId)
                self.users += ((userId,),)
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
            if not self.users or len(self.users) == 0:
                description = tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListUser.noBlacklistedUsers")
            else:
                if self.selectedIndex >= len(self.users):
                    self.selectedIndex = len(self.users) - 1
                description = "\n".join(
                    [f"{'➤' if i == self.selectedIndex else ''} <@{user[0]}>" for i, user in enumerate(self.users)]
                )
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListUser.title"),
                description=description,
            )
            await interaction.response.edit_message(embed=embed, view=self)

    view = BlacklistView(blacklisted_users, commandInfo.locale, commandInfo.guild)
    view.add_item(
        discord.ui.UserSelect(
            custom_id="user_select",
            placeholder=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistListUser.addUser.placeholder",
            ),
        )
    )
    if not blacklisted_users or len(blacklisted_users) == 0:
        description = tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistListUser.noBlacklistedUsers")
    else:
        description = "\n".join([f"{'➤' if i == 0 else ''} <@{user[0]}>" for i, user in enumerate(blacklisted_users)])
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistListUser.title"),
        description=description,
    )
    await commandInfo.reply(embed=embed, view=view)
