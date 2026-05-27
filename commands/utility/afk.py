import discord

from api import (
    addAfkMessage,
    check_if_opted_out,
    checkIfUserIsAfk,
    getAfkMessages,
    getAfkReason,
    removeAfk,
    setAfk,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def afk(command_info: CommandInfo, reason: str) -> None:
    if await check_if_opted_out(command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.afk.opted_out.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.afk.opted_out.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await checkIfUserIsAfk(command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.afk.already_afk.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.afk.already_afk.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await setAfk(command_info.user.id, reason)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.afk.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.afk.success.description",
            reason=reason,
        ),
    )
    await command_info.reply(embed=embed)


async def checkIfAfkHasToBeRemoved(message: discord.Message) -> None:
    if await check_if_opted_out(message.author.id) or message.guild is None:
        return
    if await checkIfUserIsAfk(message.author.id):
        messages = await getAfkMessages(message.author.id)
        locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"
        if not messages:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(locale, "commands.utility.afk.removed_no_messages.title"),
                description=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.afk.removed_no_messages.description",
                ),
            )
            await message.channel.send(embed=embed)
            await removeAfk(message.author.id)
            return
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "commands.utility.afk.removed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "commands.utility.afk.removed.description",
                messages="\n".join(
                    [
                        f"- https://discord.com/channels/{message.guild.id}/{msg.channel_id}/{msg.message_id}"
                        for msg in messages
                    ]
                ),
            ),
        )
        await removeAfk(message.author.id)
        await message.channel.send(embed=embed)


async def checkIfMentionsAreAfk(message: discord.Message) -> None:
    if await check_if_opted_out(message.author.id) or message.guild is None:
        return

    locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"

    afk_users = []
    reasons = []
    for mention in message.mentions:
        if await checkIfUserIsAfk(mention.id):
            afk_users.append(mention)
            reason = await getAfkReason(mention.id)
            reasons.append(reason)
            await addAfkMessage(mention.id, message.id, message.channel.id)
    if afk_users:
        if len(afk_users) == 1:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.afk.mentions_one.title",
                    user=afk_users[0].display_name,
                ),
                description=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.afk.mentions_one.description",
                    user=afk_users[0].mention,
                    reason=reasons[0],
                ),
            )
            await message.channel.send(embed=embed)
            return
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "commands.utility.afk.mentions.title"),
            description=tanjunLocalizer.localize(
                locale,
                "commands.utility.afk.mentions.description",
                users=(f"- {user.mention}\n" for user in afk_users),
            ),
        )
        await message.channel.send(embed=embed)
