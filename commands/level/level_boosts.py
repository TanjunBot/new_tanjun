# noqa: E501

import discord

from api import (
    add_channel_boost,
    add_role_boost,
    add_user_boost,
    get_all_boosts,
    get_channel_boost,
    get_user_boost,
    get_user_roles_boosts,
    remove_channel_boost,
    remove_role_boost,
    remove_user_boost,
)
from localizer import tanjunLocalizer
from utility import checkIfHasPro, CommandInfo, tanjunEmbed


async def calculate_user_channel_boost_command(
    commandInfo: CommandInfo, user: discord.Member, channel: discord.TextChannel
) -> None:
    assert commandInfo.guild is not None
    user_boost = await get_user_boost(str(commandInfo.guild.id), str(user.id))
    role_boosts = await get_user_roles_boosts(str(commandInfo.guild.id), [str(role.id) for role in user.roles])
    channel_boost = await get_channel_boost(str(commandInfo.guild.id), str(channel.id))

    total_additive_boost = 0.0
    total_multiplicative_boost = 1.0

    if user_boost:
        boost_value, is_additive = user_boost
        if is_additive:  # if additive
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value

    for role_boost in role_boosts:
        boost_value, is_additive = role_boost
        if is_additive:  # if additive
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value

    if channel_boost:
        boost_value, is_additive = channel_boost
        if is_additive:  # if additive
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value

    total_boost = (1.0 + total_additive_boost) * total_multiplicative_boost

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.calculate_user_channel.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.calculate_user_channel.description",
            user=user.mention,
            channel=channel.mention,
            boost=f"{total_boost:.2f}",
        ),
    )
    await commandInfo.reply(embed=embed)


async def add_role_boost_command(commandInfo: CommandInfo, role: discord.Role, boost: float, additive: bool) -> None:
    assert commandInfo.guild is not None
    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_role_boost(str(commandInfo.guild.id), str(role.id), boost, additive)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.add_role.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.add_role.success.description",
            role=role.mention,
            boost=boost,
            type=(
                tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.additive")
                if additive
                else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.multiplicative")
            ),
        ),
    )
    await commandInfo.reply(embed=embed)


async def add_channel_boost_command(
    commandInfo: CommandInfo, channel: discord.TextChannel, boost: float, additive: bool
) -> None:
    assert commandInfo.guild is not None
    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_channel_boost(str(commandInfo.guild.id), str(channel.id), boost, additive)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.add_channel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.add_channel.success.description",
            channel=channel.mention,
            boost=boost,
            type=(
                tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.additive")
                if additive
                else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.multiplicative")
            ),
        ),
    )
    await commandInfo.reply(embed=embed)


async def add_user_boost_command(commandInfo: CommandInfo, user: discord.Member, boost: float, additive: bool) -> None:
    assert commandInfo.guild is not None
    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.error.no_pro.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_user_boost(str(commandInfo.guild.id), str(user.id), boost, additive)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.add_user.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.add_user.success.description",
            user=user.mention,
            boost=boost,
            type=(
                tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.additive")
                if additive
                else tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.multiplicative")
            ),
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_role_boost_command(commandInfo: CommandInfo, role: discord.Role) -> None:
    assert commandInfo.guild is not None
    await remove_role_boost(str(commandInfo.guild.id), str(role.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.remove_role.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.remove_role.success.description",
            role=role.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_channel_boost_command(commandInfo: CommandInfo, channel: discord.TextChannel) -> None:
    assert commandInfo.guild is not None
    await remove_channel_boost(str(commandInfo.guild.id), str(channel.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.remove_channel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.remove_channel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_user_boost_command(commandInfo: CommandInfo, user: discord.Member) -> None:
    assert commandInfo.guild is not None
    await remove_user_boost(str(commandInfo.guild.id), str(user.id))
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.remove_user.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.boosts.remove_user.success.description",
            user=user.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def show_boosts_command(commandInfo: CommandInfo) -> None:
    assert commandInfo.guild is not None
    boosts = await get_all_boosts(str(commandInfo.guild.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.description"),
    )

    if boosts["roles"]:
        role_boosts = "\n".join(
            [
                f"<@&{role_id}>: {boost} ({tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.additive') if additive else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.multiplicative')})"
                for role_id, boost, additive in boosts["roles"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.roles"),
            value=role_boosts,
            inline=False,
        )

    if boosts["channels"]:
        channel_boosts = "\n".join(
            [
                f"<#{channel_id}>: {boost} ({tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.additive') if additive else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.multiplicative')})"
                for channel_id, boost, additive in boosts["channels"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.channels"),
            value=channel_boosts,
            inline=False,
        )

    if boosts["users"]:
        user_boosts = "\n".join(
            [
                f"<@{user_id}>: {boost} ({tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.additive') if additive else tanjunLocalizer.localize(str(commandInfo.locale), 'commands.level.boosts.multiplicative')})"
                for user_id, boost, additive in boosts["users"]
            ]
        )
        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.users"),
            value=user_boosts,
            inline=False,
        )

    if not (boosts["roles"] or boosts["channels"] or boosts["users"]):
        embed.description = tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.boosts.show.no_boosts")

    await commandInfo.reply(embed=embed)
