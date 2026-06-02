from locale_keys import locale
import math
from datetime import datetime
from typing import Any, cast
import discord
from discord.ui import Button, View
import utility
from api import get_detailed_warnings, remove_warning
from models import DetailedWarningModel
WARNINGS_PER_PAGE = 5

class WarningView(View):

    def __init__(self, warnings: list[DetailedWarningModel], member: discord.Member, command_info: utility.CommandInfo) -> None:
        super().__init__(timeout=300)
        self.warnings: list[DetailedWarningModel] = warnings
        self.member: discord.Member = member
        self.command_info: utility.CommandInfo = command_info
        self.page: int = 0
        self.message: discord.Message | None = None
        self.update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.admin.viewwarns.unauthorizedUser(str(self.command_info.locale)), ephemeral=True)
            return False
        return True

    def update_buttons(self) -> None:
        self.clear_items()
        start = self.page * WARNINGS_PER_PAGE
        end = start + WARNINGS_PER_PAGE
        if self.page > 0:
            prev_button = Button(label=locale.commands.admin.viewwarns.prevButton(str(self.command_info.locale)), style=discord.ButtonStyle.primary)
            prev_button.callback = self.prev_page
            self.add_item(prev_button)
        for i, w in enumerate(self.warnings[start:end], start=start + 1):
            button = Button(label=locale.commands.admin.viewwarns.removeButton(str(self.command_info.locale), number=i), custom_id=f'remove_{w.id}', style=discord.ButtonStyle.danger, disabled=w.expires_at is not None and datetime.now() > w.expires_at)
            button.callback = self.remove_warning_callback
            self.add_item(button)
        if (self.page + 1) * WARNINGS_PER_PAGE < len(self.warnings):
            next_button = Button(label=locale.commands.admin.viewwarns.nextButton(str(self.command_info.locale)), style=discord.ButtonStyle.primary)
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def remove_warning_callback(self, interaction: discord.Interaction) -> None:
        data = cast(dict[str, Any], interaction.data)
        warning_id = int(str(data['custom_id']).split('_')[1])
        await remove_warning(warning_id)
        self.warnings = [w for w in self.warnings if w.id != warning_id]
        if len(self.warnings) == 0:
            embed = utility.tanjunEmbed(title=locale.commands.admin.viewwarns.noWarnings.title(str(self.command_info.locale)), description=locale.commands.admin.viewwarns.noWarnings.description(str(self.command_info.locale), user=self.member.name))
            await interaction.response.edit_message(embed=embed, view=None)
            return
        self.page = min(self.page, math.ceil(len(self.warnings) / WARNINGS_PER_PAGE) - 1)
        embed = create_warnings_embed(self.command_info, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction) -> None:
        self.page = max(0, self.page - 1)
        embed = create_warnings_embed(self.command_info, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction) -> None:
        self.page = min(math.ceil(len(self.warnings) / WARNINGS_PER_PAGE) - 1, self.page + 1)
        embed = create_warnings_embed(self.command_info, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

def create_warnings_embed(command_info: utility.CommandInfo, member: discord.Member, warnings: list[DetailedWarningModel], page: int) -> utility.tanjunEmbed:
    start = page * WARNINGS_PER_PAGE
    end = start + WARNINGS_PER_PAGE
    current_warnings = warnings[start:end]
    embed = utility.tanjunEmbed(title=locale.commands.admin.viewwarns.title(str(command_info.locale), user=member.name), description=locale.commands.admin.viewwarns.description(str(command_info.locale), count=len(warnings)))
    for i, w in enumerate(current_warnings, start=start + 1):
        expired = w.expires_at is not None and datetime.now() > w.expires_at
        expiration_str = f'<t:{int(w.expires_at.timestamp())}:D>' if w.expires_at is not None else locale.commands.admin.viewwarns.never(command_info.locale)
        expiration_str = f'~~{expiration_str}~~' if expired else expiration_str
        embed.add_field(name=locale.commands.admin.viewwarns.warningEntry(str(command_info.locale), number=i), value=locale.commands.admin.viewwarns.warningDetails(command_info.locale, reason=w.reason if w.reason is not None and len(w.reason.strip()) > 0 else locale.commands.admin.viewwarns.noReason(str(command_info.locale)), date=f'<t:{int(w.created_at.timestamp())}:D>', expiration=expiration_str, created_by=w.created_by), inline=False)
    if len(warnings) > WARNINGS_PER_PAGE > 1:
        embed.set_footer(text=locale.commands.admin.viewwarns.pageFooter(command_info.locale, current=page + 1, total=math.ceil(len(warnings) / WARNINGS_PER_PAGE)))
    return embed

async def view_warnings(command_info: utility.CommandInfo, member: discord.Member) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).kick_members):
        embed = utility.tanjunEmbed(title=locale.commands.admin.viewwarns.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.viewwarns.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    guild_id = command_info.guild.id
    user_id = member.id
    warnings = [w async for w in get_detailed_warnings(guild_id, user_id)]
    if len(warnings) == 0:
        embed = utility.tanjunEmbed(title=locale.commands.admin.viewwarns.noWarnings.title(str(command_info.locale)), description=locale.commands.admin.viewwarns.noWarnings.description(str(command_info.locale), user=member.name))
        await command_info.reply(embed=embed)
        return
    embed = create_warnings_embed(command_info, member, warnings, 0)
    view = WarningView(warnings, member, command_info)
    view.message = await command_info.reply(embed=embed, view=view)