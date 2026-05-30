"""7TV Emote Copy Command — browse and add a streamer's 7TV emotes to the server.

Provides a paginated UI (like Brawl Stars brawlers) showing the emotes from a
streamer's 7TV emote set, with a button to copy each emote to the server.
"""

from __future__ import annotations

import logging

import discord

import utility
from localizer import tanjunLocalizer
from services.seventv_service import SevenTVEmote, get_seventv_service
from utility import EmbedColor


async def copy_7tv_emote(  # noqa: C901
    command_info: utility.CommandInfo,
    twitch_username: str,
) -> None:
    """Browse a streamer's 7TV emotes and optionally add them to the server."""
    # Permission checks
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_emojis
    ):
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_emojis:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.missingPermissionBot.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    # Fetch user from 7TV
    service = get_seventv_service()
    user = await service.get_user_by_twitch(twitch_username)

    if user is None or not user.emotes:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.error.notFound.title"
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.copy7tv.error.notFound.description",
                username=twitch_username,
            ),
        )
        await command_info.reply(embed=embed)
        return

    total_emotes = len(user.emotes)
    emotes_per_page = 10  # Show 10 emotes per page

    async def generate_page(page_number: int) -> discord.Embed:
        start_idx = page_number * emotes_per_page
        end_idx = min(start_idx + emotes_per_page, total_emotes)
        page_emotes = user.emotes[start_idx:end_idx]

        description_lines = []
        for i, emote in enumerate(page_emotes, start=start_idx + 1):
            animated_tag = "🎬" if emote.animated else ""
            owner_tag = f" by *{emote.owner_name}*" if emote.owner_name else ""
            line = f"**{i}.** {animated_tag} `:{emote.name}:`{owner_tag}"
            description_lines.append(line)

        description = "\n".join(description_lines)
        if not description:
            description = tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.copy7tv.noEmotes"
            )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.copy7tv.title",
                username=user.display_name,
                total=total_emotes,
            ),
            description=description,
        )
        if user.avatar_url:
            embed.set_thumbnail(url=user.avatar_url)

        # Show page info in footer
        total_pages = (total_emotes + emotes_per_page - 1) // emotes_per_page
        embed.set_footer(
            text=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.copy7tv.footer",
                page=page_number + 1,
                total_pages=total_pages,
            )
        )
        return embed

    class CopyEmotePaginator(discord.ui.View):
        def __init__(self, current_page: int = 0):
            super().__init__(timeout=300)
            self.current_page = current_page

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(command_info.locale), "commands.admin.copy7tv.notYourEmbed"
                    ),
                    ephemeral=True,
                )
                return

            total_pages = (total_emotes + emotes_per_page - 1) // emotes_per_page
            if self.current_page == 0:
                self.current_page = total_pages - 1
            else:
                self.current_page -= 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(command_info.locale), "commands.admin.copy7tv.notYourEmbed"
                    ),
                    ephemeral=True,
                )
                return

            total_pages = (total_emotes + emotes_per_page - 1) // emotes_per_page
            if self.current_page == total_pages - 1:
                self.current_page = 0
            else:
                self.current_page += 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="➕", style=discord.ButtonStyle.success)
        async def add_emote(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
            """Open a modal to pick which emote number to add."""
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(command_info.locale), "commands.admin.copy7tv.notYourEmbed"
                    ),
                    ephemeral=True,
                )
                return
            await interaction.response.send_modal(AddEmoteModal(command_info, user.emotes))

    class AddEmoteModal(discord.ui.Modal):
        def __init__(
            self,
            cmd_info: utility.CommandInfo,
            emotes: list[SevenTVEmote],
        ) -> None:
            self.cmd_info = cmd_info
            self.emotes = emotes
            super().__init__(
                title=tanjunLocalizer.localize(
                    str(cmd_info.locale), "commands.admin.copy7tv.addModal.title"
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        str(cmd_info.locale), "commands.admin.copy7tv.addModal.label"
                    ),
                    placeholder=tanjunLocalizer.localize(
                        str(cmd_info.locale), "commands.admin.copy7tv.addModal.placeholder"
                    ),
                    required=True,
                    max_length=3,
                )
            )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            try:
                emote_number = int(self.children[0].value) - 1  # Convert to 0-based
                if emote_number < 0 or emote_number >= len(self.emotes):
                    raise ValueError("Out of range")

                emote = self.emotes[emote_number]

                # Check emoji limits
                assert self.cmd_info.guild is not None
                guild_emojis = self.cmd_info.guild.emojis
                animated_count = sum(1 for e in guild_emojis if e.animated)
                static_count = sum(1 for e in guild_emojis if not e.animated)
                animated_limit = self.cmd_info.guild.emoji_limit
                static_limit = self.cmd_info.guild.emoji_limit

                if emote.animated and animated_count >= animated_limit:
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            str(self.cmd_info.locale),
                            "commands.admin.copy7tv.addModal.limitAnimated",
                        ),
                        ephemeral=True,
                    )
                    return
                if not emote.animated and static_count >= static_limit:
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            str(self.cmd_info.locale),
                            "commands.admin.copy7tv.addModal.limitStatic",
                        ),
                        ephemeral=True,
                    )
                    return

                # Download the emote image
                service = get_seventv_service()
                image_bytes = await service.get_emote_image_bytes(emote.image_url)
                if image_bytes is None:
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            str(self.cmd_info.locale),
                            "commands.admin.copy7tv.addModal.downloadError",
                        ),
                        ephemeral=True,
                    )
                    return

                # Create the emoji in the guild
                new_emoji = await self.cmd_info.guild.create_custom_emoji(
                    name=emote.name,
                    image=image_bytes,
                    reason=tanjunLocalizer.localize(
                        str(self.cmd_info.locale),
                        "commands.admin.copy7tv.addModal.reason",
                    ),
                )

                embed = utility.tanjunEmbed(
                    colour=EmbedColor.SUCCESS,
                    title=tanjunLocalizer.localize(
                        str(self.cmd_info.locale), "commands.admin.copy7tv.addModal.success.title"
                    ),
                    description=tanjunLocalizer.localize(
                        str(self.cmd_info.locale),
                        "commands.admin.copy7tv.addModal.success.description",
                        emoji=str(new_emoji),
                        name=emote.name,
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except (ValueError, IndexError):
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(self.cmd_info.locale),
                        "commands.admin.copy7tv.addModal.invalidNumber",
                    ),
                    ephemeral=True,
                )
            except discord.HTTPException as e:
                logging.exception("Failed to create emoji from 7TV")
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(self.cmd_info.locale),
                        "commands.admin.copy7tv.addModal.error",
                        error=str(e),
                    ),
                    ephemeral=True,
                )

    # Show the first page with paginator
    first_page = await generate_page(0)
    view = CopyEmotePaginator()
    await command_info.reply(embed=first_page, view=view)
