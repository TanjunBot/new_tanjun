import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def copyrole(commandInfo: utility.CommandInfo, role: discord.Role, copy_members: bool = False) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.copyrole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.copyrole.missingPermission.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    assert commandInfo.client.user is not None
    bot_member = CommandInfo.guild.get_member(commandInfo.client.user.id)  # type: ignore[misc, union-attr]
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.copyrole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.copyrole.missingPermissionBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    reasonLocale = tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.copyrole.reason", name=role.name)

    # Get display_icon as bytes or str (URL) or None
    if role.icon is not None:
        display_icon: bytes | str | None = await role.icon.read()
    elif role.unicode_emoji:
        display_icon = role.unicode_emoji
    else:
        display_icon = None

    newRole = await commandInfo.guild.create_role(
        name=role.name,
        color=role.color,
        hoist=role.hoist,
        mentionable=role.mentionable,
        permissions=role.permissions,
        display_icon=display_icon,  # type: ignore[arg-type]
        reason=reasonLocale,
    )

    if copy_members:
        for member in role.members:
            await member.add_roles(newRole)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.copyrole.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.copyrole.success.description",
        ),
    )

    await commandInfo.reply(embed=embed)
    await newRole.edit(reason=reasonLocale, position=role.position)
    return
