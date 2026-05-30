import discord

import utility
from localizer import tanjunLocalizer


async def copyrole(command_info: utility.CommandInfo, role: discord.Role, copy_members: bool = False) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyrole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyrole.missingPermission.description",
            ),
        )

        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    assert command_info.client.user is not None
    bot_member = command_info.guild.get_member(command_info.client.user.id)  # type: ignore[misc, union-attr]
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyrole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.copyrole.missingPermissionBot.description",
            ),
        )

        await command_info.reply(embed=embed)
        return

    reason_locale = tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyrole.reason", name=role.name)

    # Get display_icon as bytes or str (URL) or None
    if role.icon is not None:
        display_icon: bytes | str | None = await role.icon.read()
    elif role.unicode_emoji:
        display_icon = role.unicode_emoji
    else:
        display_icon = None

    new_role = await command_info.guild.create_role(
        name=role.name,
        color=role.color,
        hoist=role.hoist,
        mentionable=role.mentionable,
        permissions=role.permissions,
        display_icon=display_icon,  # type: ignore[arg-type]
        reason=reason_locale,
    )

    if copy_members:
        for member in role.members:
            await member.add_roles(new_role)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.copyrole.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.copyrole.success.description",
        ),
    )

    await command_info.reply(embed=embed)
    await new_role.edit(reason=reason_locale, position=role.position)
    return
