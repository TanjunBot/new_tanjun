import discord
from typing import Optional

import utility
from localizer import tanjunLocalizer


async def createrole(
    commandInfo: utility.commandInfo,
    name: str,
    color: Optional[discord.Color | str] = None,
    reason: Optional[str] = None,
    hoist: bool = False,
    mentionable: bool = False,
    display_icon: Optional[discord.Attachment | str] = None,
) -> None:
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createrole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.missingPermission.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    assert commandInfo.client.user is not None
    if not commandInfo.guild.get_member(commandInfo.client.user.id).guild_permissions.manage_roles:  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.missingPermissionBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    if not name:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createrole.missingName.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.missingName.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    if len(name) > 100:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createrole.nameTooLong.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.nameTooLong.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    if color:
        if isinstance(color, str):
            if not color.startswith("#"):
                color = "#" + color
            try:
                color = discord.Color(int(color.replace("#", ""), 16))
            except ValueError:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.invalidColor.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.invalidColor.description",
                    ),
                )

                await commandInfo.reply(embed=embed)
                return

    if reason and len(reason) > 512:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createrole.reasonTooLong.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createrole.reasonTooLong.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    if display_icon:
        if "ROLE_ICONS" not in commandInfo.guild.features:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.createrole.roleIconsNotEnabled.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.createrole.roleIconsNotEnabled.description",
                ),
            )

            await commandInfo.reply(embed=embed)
            return

        if isinstance(display_icon, discord.Attachment):
            if display_icon.filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.invalidIcon.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.invalidIcon.description",
                    ),
                )

                await commandInfo.reply(embed=embed)
                return

            if display_icon.size > 256000:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.iconTooLarge.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.createrole.iconTooLarge.description",
                    ),
                )

                await commandInfo.reply(embed=embed)
                return

    display_icon_data: bytes | str | None = None
    if isinstance(display_icon, discord.Attachment):
        display_icon_data = await display_icon.read()
    elif isinstance(display_icon, str):
        display_icon_data = display_icon
    role = await commandInfo.guild.create_role(
        name=name,
        color=color if color is not None else discord.Color.default(),
        reason=reason,
        hoist=hoist,
        mentionable=mentionable,
        display_icon=display_icon_data,
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createrole.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.createrole.success.description",
            role=role,
        ),
    )

    await commandInfo.reply(embed=embed)
    return
