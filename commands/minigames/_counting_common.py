import discord

from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def require_moderate_members(command_info: CommandInfo, locale_key_prefix: str) -> bool:
    """Check if the user has moderate_members permission. Returns True if check failed (should return)."""
    if command_info.guild is None:
        return True
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).moderate_members
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.no_moderate_members_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True
    return False


async def require_bot_permissions(command_info: CommandInfo, channel: discord.TextChannel) -> bool:
    """Check bot permissions for counting. Returns True if any check failed (should return)."""
    if command_info.client.user is None:
        return True
    self_member = command_info.guild.get_member(command_info.client.user.id) if command_info.guild else None
    if self_member is None:
        return True

    if not channel.permissions_for(self_member).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_send_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_send_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    if not channel.permissions_for(self_member).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_message_delete_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_message_delete_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    if not channel.permissions_for(self_member).read_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_read_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_read_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    if not channel.permissions_for(self_member).view_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_view_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.setcountingchannel.error.no_view_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    return False


async def require_counting_channel(
    command_info: CommandInfo, channel_id: int, get_progress_func, locale_key_prefix: str
) -> int | None:
    """Check if the channel is a counting channel. Returns progress if found, None if not (should return)."""
    current_progress = await get_progress_func(channel_id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.not_counting_channel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.not_counting_channel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return None
    return current_progress


async def require_valid_progress(command_info: CommandInfo, progress: int, locale_key_prefix: str) -> bool:
    """Check progress bounds. Returns True if invalid (should return)."""
    if progress < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.invalid_progress.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.invalid_progress.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    if progress > 1_000_000_000:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.too_high.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                f"{locale_key_prefix}.error.too_high.description",
            ),
        )
        await command_info.reply(embed=embed)
        return True

    return False
