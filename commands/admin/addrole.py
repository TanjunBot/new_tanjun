import discord
import utility
from localizer import tanjunLocalizer

async def addrole(
    commandInfo: utility.commandInfo, target: discord.Member, role: discord.Role
):
    
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.missingPermission.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if not commandInfo.guild.get_member(commandInfo.client.user.id).guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.missingPermissionBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if role in target.roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.alreadyHasRole.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.alreadyHasRole.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if commandInfo.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.roleTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.roleTooHigh.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if commandInfo.guild.get_member(commandInfo.client.user.id).top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.roleTooHighBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.roleTooHighBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if role.managed:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.addrole.managedRole.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.managedRole.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return

    await target.add_roles(role)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.addrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.addrole.success.description",
            target=target.mention,
            role=role.mention,
        ),
    )
    await commandInfo.reply(embed=embed)
    return
