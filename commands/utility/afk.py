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
from utility import commandInfo, tanjunEmbed


async def afk(commandInfo: commandInfo, reason: str):
    if await check_if_opted_out(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.afk.opted_out.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.afk.opted_out.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await checkIfUserIsAfk(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.afk.already_afk.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.afk.already_afk.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await setAfk(commandInfo.user.id, reason)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.afk.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.afk.success.description",
            reason=reason,
        ),
    )
    await commandInfo.reply(embed=embed)


async def checkIfAfkHasToBeRemoved(message: discord.message):
    if await check_if_opted_out(message.author.id):
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
                    [f"- https://discord.com/channels/{message.guild.id}/{msg[1]}/{msg[0]}" for msg in messages]
                ),
            ),
        )
        await removeAfk(message.author.id)
        await message.channel.send(embed=embed)


async def checkIfMentionsAreAfk(message: discord.message):
    if await check_if_opted_out(message.author.id):
        return

    locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"

    afkUsers = []
    reasons = []
    for mention in message.mentions:
        if await checkIfUserIsAfk(mention.id):
            afkUsers.append(mention)
            reason = await getAfkReason(mention.id)
            reasons.append(reason)
            await addAfkMessage(mention.id, message.id, message.channel.id)
    if afkUsers:
        if len(afkUsers) == 1:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.afk.mentions_one.title",
                    user=afkUsers[0].display_name,
                ),
                description=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.afk.mentions_one.description",
                    user=afkUsers[0].mention,
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
                users=(f"- {user.mention}\n" for user in afkUsers),
            ),
        )
        await message.channel.send(embed=embed)
