import num2words
import utility
from localizer import tanjunLocalizer


async def num2word(commandInfo: utility.commandInfo, number: int, locale: str):
    validLocales = [
        "en",
        "am",
        "ar",
        "az",
        "by",
        "ce",
        "cy",
        "cz",
        "de",
        "dk",
        "en_GB",
        "en_IN",
        "en_NG",
        "es",
        "es_CO",
        "es_CR",
        "es_VE",
        "es_GT",
        "eu",
        "fa",
        "fi",
        "fr",
        "fr_CH",
        "fr_BE",
        "fr_DZ",
        "he",
        "hu",
        "id",
        "is",
        "it",
        "ja",
        "kn",
        "ko",
        "kz",
        "lt",
        "lv",
        "no",
        "pl",
        "pt",
        "pt_BR",
        "sl",
        "sr",
        "sv",
        "ro",
        "ru",
        "te",
        "tg",
        "tr",
        "th",
        "vi",
        "nl",
        "uk",
    ]

    if locale == "en_US":
        locale = "en"

    if locale not in validLocales:
        locale = "en"

    word = num2words.num2words(number, lang=locale)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.math.num2word.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.math.num2word.description",
            number=number,
            word=word[:4000],
        ),
    )
    await commandInfo.reply(embed=embed)
