from utility import tanjunEmbed, relativeTimeStrToDate
from localizer import tanjunLocalizer

async def generateGiveawayEmbed(giveawayInformation, locale):
    requirements_parts = []

    if giveawayInformation["new_message_requirement"]:
        requirements_parts.append(tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.new_message_requirement",
            count=giveawayInformation["new_message_requirement"]))
    if giveawayInformation["day_requirement"]:
        requirements_parts.append(tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.day_requirement",
            count=giveawayInformation["day_requirement"]))
    if giveawayInformation["role_requirement"]:
        requirements_parts.append(tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.role_requirement",
            roles=", ".join(f"<@&{role}>" for role in giveawayInformation["role_requirement"])))
    if giveawayInformation["voice_requirement"]:
        requirements_parts.append(tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.voice_requirement",
            minutes=giveawayInformation["voice_requirement"]))
    if giveawayInformation["channel_requirements"]:
        channels_desc = ', '.join(f"<#{k}>: {v}" for k, v in giveawayInformation["channel_requirements"].items())
        requirements_parts.append(tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.channel_requirements",
            channels=channels_desc))

    requirements_text = "\n".join(requirements_parts) if requirements_parts else tanjunLocalizer.localize(
        locale, "commands.giveaway.giveawayEmbed.no_requirements")

    description = ""

    if giveawayInformation["description"]:
        description += giveawayInformation["description"] + "\n\n"

    if giveawayInformation["price"]:
        description +=tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.price",
            price=giveawayInformation["price"])

    if giveawayInformation["sponsor"]:
        description += tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.sponsor",
            sponsor=f"<@{giveawayInformation['sponsor']}>") + "\n"

    description += tanjunLocalizer.localize(
        locale,
        "commands.giveaway.giveawayEmbed.description",
        requirements=requirements_text,
        winners=giveawayInformation["winners"]
    )

    if giveawayInformation["end_time"]:
        description += "\n" + tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.end_time",
            date=f"<t:{int(relativeTimeStrToDate(giveawayInformation['end_time']).timestamp())}:R>")
        

    # Creating embed with localized content
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "commands.giveaway.giveawayEmbed.title", title=giveawayInformation["title"]),
        description=description
    )

    return embed
