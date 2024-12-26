import discord
from discord.ext import commands
import os
import asyncio
import config
from translator import TanjunTranslator
import api
import asyncmy
from config import database_ip, database_password, database_user, database_schema
from commands.utility.twitch.twitchApi import initTwitch
from concurrent.futures import ThreadPoolExecutor
from functools import partial


async def loadextension(bot, extensionname):
    extensionname = f"extensions.{extensionname}"
    try:
        await bot.load_extension(extensionname)
        print(f"{extensionname} loaded!")
    except Exception as e:
        raise e
        print(f"Failed to load extension {extensionname}")


async def loadTranslator(bot):
    print("loading translator...")
    translator = TanjunTranslator()
    await bot.tree.set_translator(translator)
    print("translator loaded!")


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis_and_stickers = True
intents.voice_states = True
intents.messages = True
intents.typing = True
intents.message_content = True
intents.auto_moderation_configuration = True
intents.auto_moderation_execution = True
intents.invites = True
intents.presences = False


class ThreadedBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread_pool = ThreadPoolExecutor(max_workers=50)  # Adjust max_workers as needed
        self.active_threads = {}  # Track active command threads

    async def invoke_command_threaded(self, ctx):
        # Create a unique thread identifier
        thread_id = f"{ctx.command}_{ctx.message.id}"

        # Create partial function to run command
        command_func = partial(self.invoke_command_sync, ctx)

        # Submit to thread pool and track the thread
        future = self.thread_pool.submit(command_func)
        self.active_threads[thread_id] = future

        try:
            # Wait for command completion
            await self.loop.run_in_executor(None, future.result)
        finally:
            # Clean up completed thread
            if thread_id in self.active_threads:
                del self.active_threads[thread_id]

    def invoke_command_sync(self, ctx):
        # Synchronous wrapper for command invocation
        asyncio.run_coroutine_threadsafe(
            self._invoke_command(ctx), self.loop
        ).result()

    async def _invoke_command(self, ctx):
        try:
            if ctx.command is not None:
                await ctx.command.invoke(ctx)
        except commands.CommandError as e:
            await ctx.send(str(e))


bot = ThreadedBot("t.", intents=intents, application_id=config.applicationId)


async def main():
    print("starting bot...")
    print("discord.py version: ", discord.__version__)
    for extension in os.listdir(os.fsencode("extensions")):
        if os.fsdecode(extension).endswith(".py"):
            extension = os.fsdecode(extension).replace(".py", "")
            await loadextension(bot, extension)
    await loadTranslator(bot)


async def create_pool():
    try:
        p = await asyncmy.create_pool(
            host=database_ip,
            user=database_user,
            password=database_password,
            db=database_schema,
            maxsize=1,
            minsize=1,
        )
        return p
    except Exception as e:
        print(f"Error creating pool: {e}")
        return None


# Add event handler for command processing
@bot.event
async def on_command(ctx):
    await bot.invoke_command_threaded(ctx)


# Add event handler for application commands (slash commands)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)


@bot.tree.interaction_check
async def interaction_check(interaction: discord.Interaction):
    # Create a thread for slash command execution
    thread_id = f"{interaction.command.name}_{interaction.id}"

    async def execute_command():
        try:
            await interaction.command.callback(interaction.command, interaction)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    # Store the future in active_threads
    future = bot.thread_pool.submit(
        lambda: asyncio.run_coroutine_threadsafe(
            execute_command(), bot.loop
        ).result()
    )
    bot.active_threads[thread_id] = future

    return True


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game(name=config.activity.format(version=config.version))
    )
    pool = await create_pool()
    print(pool)
    api.set_pool(pool)
    await api.create_tables()
    await initTwitch()
    print("Bot is running!")

bot.run(config.token)
