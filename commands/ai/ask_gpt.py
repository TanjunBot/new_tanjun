import os

from openai import AsyncOpenAI

import utility
from api import getToken, getTokenOverview, includeToToken, useToken
from config import openAiKey
from localizer import tanjunLocalizer

# Make OpenAI API key optional
open_ai_key = openAiKey or os.getenv("OPENAI_API_KEY")

# Initialize client only if API key is available
client = AsyncOpenAI(api_key=open_ai_key) if open_ai_key else None


async def ask_gpt(
    command_info: utility.CommandInfo,
    name: str,
    situation: str,
    prompt: str,
    temperature: float = 1,
    top_p: float = 1,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
) -> None:
    token = await getToken(command_info.user.id)

    if not token:
        await includeToToken(command_info.user.id)
        token = await getToken(command_info.user.id)

    if token < 20:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.ask.notoken.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.ask.notoken.description"),
        )
        await command_info.reply(embed=embed)
        return

    additional_prompt_information = f"""You are a Personality from the AI commands from the Discord Bot `Tanjun`.
    Stick to your personality as close as possible. Here are some additional information about the server and the prompter:
    Name: {command_info.user.name}
    userID: {command_info.user.id}
    Server: {command_info.guild.name if command_info.guild else "Direct Message"}
    User Roles: {", ".join([role.name for role in getattr(command_info.user, "roles", [])])}

    Here is your Personality. Here is the prompt you are supposed to answer:
    """

    prompt = additional_prompt_information + "\n\n" + prompt

    if not client:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.ask.noapi.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.ask.noapi.description"),
        )
        await command_info.reply(embed=embed)
        return

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": situation}]},
            {"role": "user", "content": [{"type": "text", "text": prompt}]},
        ],
        temperature=float(temperature),
        max_tokens=256,
        top_p=float(top_p),
        frequency_penalty=float(frequency_penalty),
        presence_penalty=float(presence_penalty),
    )

    token_cost = int(response.usage.total_tokens * 0.125)  # type: ignore[union-attr]

    await useToken(command_info.user.id, token_cost)

    token_overview = await getTokenOverview(command_info.user.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.ask.success.title", name=name),
        description=response.choices[0].message.content,
    )

    embed.set_footer(
        text=tanjunLocalizer.localize(
            command_info.locale,
            "commands.ai.ask.success.footer",
            cost=token_cost,
            token=token - token_cost if token - token_cost > 0 else 0,
            free=token_overview.free_token,
            plus=token_overview.plus_token,
            paid=token_overview.paid_token,
        )
    )
    await command_info.reply(embed=embed)
