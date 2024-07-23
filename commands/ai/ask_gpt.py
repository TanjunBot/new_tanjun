import utility
from localizer import tanjunLocalizer
from api import getToken, getTokenOverview, useToken, includeToToken
import discord
from config import openAiKey
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=openAiKey)

async def ask_gpt(commandInfo: utility.commandInfo, 
                name: str, 
                situation: str, 
                prompt: str,
                temperature: float = 1,
                top_p: float = 1,
                frequency_penalty: float = 0,
                presence_penalty: float = 0):
    
    token = await getToken(commandInfo.user.id) 

    if not token:
        await includeToToken(commandInfo.user.id)
        token = await getToken(commandInfo.user.id)
    
    if token < 20:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.ask.notoken.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.ask.notoken.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": situation
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt
                }
            ]
            },
        ],
        temperature=float(temperature),
        max_tokens=256,
        top_p=float(top_p),
        frequency_penalty=float(frequency_penalty),
        presence_penalty=float(presence_penalty)
    )
    print(response)

    tokenOverview = await getTokenOverview(commandInfo.user.id)

    tokenCost = int(response.usage.total_tokens * 0.25)

    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.ask.success.title", name=name),
        description = response.choices[0].message.content,
    )
    embed.set_footer(text=tanjunLocalizer.localize(commandInfo.locale, "commands.ai.ask.success.footer", 
                                                   cost=tokenCost, 
                                                   token=token - tokenCost if token - tokenCost > 0 else 0, 
                                                   free=tokenOverview[0], 
                                                   plus=tokenOverview[1], 
                                                   paid=tokenOverview[2])
                                                   )
    await commandInfo.reply(embed=embed)

