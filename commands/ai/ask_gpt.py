from locale_keys import locale
import utility
from services.ai_service import AiService
from services.openrouter_client import get_openrouter_client, get_openrouter_model
client = get_openrouter_client()

async def ask_gpt(command_info: utility.CommandInfo, name: str, situation: str, prompt: str, temperature: float=1, top_p: float=1, frequency_penalty: float=0, presence_penalty: float=0) -> None:
    token = await AiService.get_available_tokens(command_info.user.id)
    if not token:
        await AiService.initialize_user(command_info.user.id)
        token = await AiService.get_available_tokens(command_info.user.id)
    if token < 20:
        embed = utility.tanjunEmbed(title=locale.commands.ai.ask.notoken.title(str(command_info.locale)), description=locale.commands.ai.ask.notoken.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    additional_prompt_information = f"You are a Personality from the AI commands from the Discord Bot `Tanjun`.\n    Stick to your personality as close as possible. Here are some additional information about the server and the prompter:\n    Name: {command_info.user.name}\n    userID: {command_info.user.id}\n    Server: {(command_info.guild.name if command_info.guild else 'Direct Message')}\n    User Roles: {', '.join([role.name for role in getattr(command_info.user, 'roles', [])])}\n\n    Here is your Personality. Here is the prompt you are supposed to answer:\n    "
    prompt = additional_prompt_information + '\n\n' + prompt
    if not client:
        embed = utility.tanjunEmbed(title=locale.commands.ai.ask.noapi.title(str(command_info.locale)), description=locale.commands.ai.ask.noapi.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    response = await client.chat.completions.create(model=get_openrouter_model(), messages=[{'role': 'system', 'content': situation}, {'role': 'user', 'content': prompt}], temperature=float(temperature), max_tokens=256, top_p=float(top_p), frequency_penalty=float(frequency_penalty), presence_penalty=float(presence_penalty))
    token_cost = int(response.usage.total_tokens * 0.125)
    consumed = await AiService.consume(command_info.user.id, token_cost)
    if not consumed:
        embed = utility.tanjunEmbed(title=locale.commands.ai.ask.notoken.title(str(command_info.locale)), description=locale.commands.ai.ask.notoken.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    token_overview = await AiService.get_token_overview(command_info.user.id)
    embed = utility.tanjunEmbed(title=locale.commands.ai.ask.success.title(str(command_info.locale), name=name), description=response.choices[0].message.content)
    embed.set_footer(text=locale.commands.ai.ask.success.footer(command_info.locale, cost=token_cost, token=token - token_cost if token - token_cost > 0 else 0, free=token_overview.free_token if token_overview else 0, plus=token_overview.plus_token if token_overview else 0, paid=token_overview.paid_token if token_overview else 0))
    await command_info.reply(embed=embed)