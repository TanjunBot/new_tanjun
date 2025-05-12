import discord

from api import (
    add_channel_to_blacklist,
    add_role_to_blacklist,
    add_user_to_blacklist,
    get_blacklist,
    remove_channel_from_blacklist,
    remove_role_from_blacklist,
    remove_user_from_blacklist,
)
from localizer import tanjunLocalizer
from utility import checkIfHasPro, commandInfo, tanjunEmbed


async def add_channel_to_blacklist_command(commandInfo: commandInfo, channel: discord.TextChannel, reason: str = None):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_channel.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_channel.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_channel_to_blacklist(str(commandInfo.guild.id), str(channel.id), reason)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.add_channel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.add_channel.success.description",
            channel=channel.mention,
            reason=(reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.no_reason")),
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_channel_from_blacklist_command(commandInfo: commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_channel.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_channel.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_channel_from_blacklist(str(commandInfo.guild.id), str(channel.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.remove_channel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.remove_channel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def add_role_to_blacklist_command(commandInfo: commandInfo, role: discord.Role, reason: str = None):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_role.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_role.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_role_to_blacklist(str(commandInfo.guild.id), str(role.id), reason)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.add_role.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.add_role.success.description",
            role=role.mention,
            reason=(reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.no_reason")),
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_role_from_blacklist_command(commandInfo: commandInfo, role: discord.Role):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_role.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_role.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_role_from_blacklist(str(commandInfo.guild.id), str(role.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.remove_role.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.remove_role.success.description",
            role=role.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def add_user_to_blacklist_command(commandInfo: commandInfo, user: discord.Member, reason: str = None):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_user.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_user.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_channel.error.no_pro.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.add_channel.error.no_pro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_user_to_blacklist(str(commandInfo.guild.id), str(user.id), reason)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.add_user.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.add_user.success.description",
            user=user.mention,
            reason=(reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.no_reason")),
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_user_from_blacklist_command(commandInfo: commandInfo, user: discord.Member):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_user.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.remove_user.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_user_from_blacklist(str(commandInfo.guild.id), str(user.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.remove_user.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.blacklist.remove_user.success.description",
            user=user.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def show_blacklist_command(commandInfo: commandInfo):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.show.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.blacklist.show.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    blacklist = await get_blacklist(str(commandInfo.guild.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.description"),
    )

    if blacklist["channels"]:
        channel_list = "\n".join(
            [
                f"<#{channel_id}> - {reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.blacklist.no_reason')}"
                for channel_id, reason in blacklist["channels"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.channels"),
            value=channel_list,
            inline=False,
        )

    if blacklist["roles"]:
        role_list = "\n".join(
            [
                f"<@&{role_id}> - {reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.blacklist.no_reason')}"
                for role_id, reason in blacklist["roles"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.roles"),
            value=role_list,
            inline=False,
        )

    if blacklist["users"]:
        user_list = "\n".join(
            [
                f"<@{user_id}> - {reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.blacklist.no_reason')}"
                for user_id, reason in blacklist["users"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.users"),
            value=user_list,
            inline=False,
        )

    if not (blacklist["channels"] or blacklist["roles"] or blacklist["users"]):
        embed.description = tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.blacklist.show.empty")

    await commandInfo.reply(embed=embed)
