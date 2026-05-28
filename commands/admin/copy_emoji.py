import logging
import re

import aiohttp
import discord
from aiohttp import ClientTimeout

import utility
from localizer import tanjunLocalizer


async def copy_emoji(
    command_info: utility.CommandInfo,
    emoji: str,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_emojis
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyEmoji.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_emojis:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyEmoji.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyEmoji.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    # Find all emoji patterns in the string
    emoji_pattern = r"<(?:a)?:([^:]+):(\d+)>"
    matches = list(re.finditer(emoji_pattern, emoji))

    if not matches:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.error.noEmojis.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyEmoji.error.noEmojis.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    successful_emojis = []
    failed_emojis = []

    # Get current emoji counts
    guild_emojis = command_info.guild.emojis
    animated_count = sum(1 for e in guild_emojis if e.animated)
    static_count = sum(1 for e in guild_emojis if not e.animated)

    # Get emoji limits based on guild boost level
    animated_limit = command_info.guild.emoji_limit
    static_limit = command_info.guild.emoji_limit

    try:
        for match in matches:
            name = match.group(1)
            emoji_id = int(match.group(2))
            animated = match.group(0).startswith("<a:")

            # Check if we've hit the limit for this type
            if animated and animated_count >= animated_limit or not animated and static_count >= static_limit:
                failed_emojis.append(match.group(0))
                continue

            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if animated else 'png'}"

            try:
                async with aiohttp.ClientSession() as session, session.get(emoji_url, timeout=ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        failed_emojis.append(match.group(0))
                        continue
                    emoji_bytes = await resp.read()

                # Create the emoji in the guild
                new_emoji = await command_info.guild.create_custom_emoji(
                    name=name,
                    image=emoji_bytes,
                    reason=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.reason"),
                )
                successful_emojis.append(str(new_emoji))

                # Update counters
                if animated:
                    animated_count += 1
                else:
                    static_count += 1

            except Exception:
                logging.exception("Failed to copy emoji %s (id=%s)", name, emoji_id)
                failed_emojis.append(match.group(0))

        # Handle different response scenarios
        if not successful_emojis:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.copyEmoji.error.limitReached.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.copyEmoji.error.limitReached.description",
                ),
            )
        elif len(successful_emojis) == 1 and not failed_emojis:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.success.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.copyEmoji.success.description",
                    emoji=successful_emojis[0],
                ),
            )
        else:
            # Some succeeded, some might have failed
            description = tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyEmoji.success.multiple.description",
                emojis=" ".join(successful_emojis),
                count=len(successful_emojis),
            )

            if failed_emojis:
                description += "\n\n" + tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.copyEmoji.partialSuccess.description",
                    failed_count=len(failed_emojis),
                    failed_emojis=" ".join(failed_emojis),
                )

            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    (
                        "commands.admin.copyEmoji.partialSuccess.title"
                        if failed_emojis
                        else "commands.admin.copyEmoji.success.multiple.title"
                    ),
                ),
                description=description,
            )

        await command_info.reply(embed=embed)

    except Exception:
        logging.exception("Unexpected error in copy_emoji command")
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyEmoji.error.description"),
        )
        await command_info.reply(embed=embed)
