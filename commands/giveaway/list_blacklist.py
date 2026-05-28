import utility
from services.giveaway_service import giveaway_service
from localizer import tanjunLocalizer


async def list_blacklist(
    command_info: utility.CommandInfo,
) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    blacklisted_roles = [role.entity_id for role in await giveaway_service.get_blacklisted_roles(str(command_info.guild.id))]  # type: ignore[union-attr]
    blacklisted_users = [user.entity_id for user in await giveaway_service.get_blacklisted_users(str(command_info.guild.id))]  # type: ignore[union-attr]

    if len(blacklisted_roles) == 0 and len(blacklisted_users) == 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.noBlacklist.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.noBlacklist.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.list_blacklist.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.list_blacklist.description",
        ),
    )

    if blacklisted_roles:
        embed.add_field(
            name=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.roles",
            ),
            value="\n".join([f"<@&{role}>" for role in blacklisted_roles]),
            inline=False,
        )

    if blacklisted_users:
        embed.add_field(
            name=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.list_blacklist.users",
            ),
            value="\n".join([f"<@{user}>" for user in blacklisted_users]),
            inline=False,
        )

    await command_info.reply(embed=embed)
