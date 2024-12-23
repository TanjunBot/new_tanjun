import asyncio


async def test_commands(self, ctx):
    commands = self.bot.commands

    for command in commands:
        # Skip commands that require arguments
        if command.clean_params:
            # You can choose to provide default arguments instead of skipping
            continue  # Skipping commands that require arguments for now

        try:
            # Invoke the command
            await ctx.invoke(command)
        except Exception as e:
            await ctx.send(f"Error invoking {command.name}: {e}")

        # Wait for the bot's message and delete it
        def check(message):
            return message.author == self.bot.user and message.channel == ctx.channel

        try:
            # Wait for the message sent by the command
            message = await self.bot.wait_for('message', check=check, timeout=5)
            await message.delete()
        except asyncio.TimeoutError:
            pass  # No message was sent within the timeout period
