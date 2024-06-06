import discord
import utility
from localizer import tanjunLocalizer

async def removerole(
    commandInfo: utility.commandInfo, target: discord.Member, role: discord.Role
):
    
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removerole.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.removerole.missingPermission.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if not commandInfo.guild.get_member(commandInfo.client.user.id).guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removerole.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.removerole.missingPermissionBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if role not in target.roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removerole.doesNotHaveRole.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.removerole.doesNotHaveRole.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if commandInfo.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removerole.roleTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.removerole.roleTooHigh.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    if commandInfo.guild.get_member(commandInfo.client.user.id).top_role.position <= role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.removerole.roleTooHighBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.removerole.roleTooHighBot.description",
            ),
        )

        await commandInfo.reply(embed=embed)
        return
    
    await target.remove_roles(role)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.removerole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.removerole.success.description",
            target=target,
            role=role,
        ),
    )
    await commandInfo.reply(embed=embed)