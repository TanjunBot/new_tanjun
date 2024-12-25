import utility
from localizer import tanjunLocalizer
from api import remove_scheduled_message as remove_message, get_scheduled_messages
import discord
from discord.ui import View, Select


class MessageSelectView(View):
    def __init__(self, messages, locale):
        super().__init__(timeout=300)  # 5 minute timeout
        self.locale = locale

        # Create select menu with messages
        select = Select(
            placeholder=tanjunLocalizer.localize(
                locale, "commands.utility.removescheduled.select.placeholder"
            ),
            options=[
                discord.SelectOption(
                    label=f"ID: {msg[0]} - {msg[4][:50]}...",  # Truncate long messages
                    description=f"{msg[3]} | {msg[2] or 'DM'}",
                    value=str(msg[0]),
                )
                for msg in messages
            ][
                :25
            ],  # Discord limit of 25 options
        )

        @select.callback
        async def select_callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.locale,
                        "commands.utility.removescheduled.error.not_authorized",
                    ),
                    ephemeral=True,
                )
                return

            message_id = int(select.values[0])
            await remove_message(message_id)

            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.locale, "commands.utility.removescheduled.success.title"
                ),
                description=tanjunLocalizer.localize(
                    self.locale,
                    "commands.utility.removescheduled.success.description",
                    id=message_id,
                ),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()

        self.add_item(select)

    async def on_timeout(self):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.locale, "commands.utility.removescheduled.error.timeout.title"
            ),
            description=tanjunLocalizer.localize(
                self.locale,
                "commands.utility.removescheduled.error.timeout.description",
            ),
        )
        if self.message:
            await self.message.edit(embed=embed, view=None)


async def remove_scheduled_message(
    commandInfo: utility.commandInfo, message_id: int = None
):
    # Get all scheduled messages for the user
    messages = await get_scheduled_messages(commandInfo.user.id)

    if not messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.no_messages.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.no_messages.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # If no message_id provided, show selection menu
    if not message_id:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.removescheduled.select.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.select.description",
            ),
        )
        view = MessageSelectView(messages, commandInfo.locale)
        view.user = commandInfo.user
        view.message = await commandInfo.reply(embed=embed, view=view)
        return

    # If message_id provided, verify it exists and belongs to user
    message_exists = False
    for msg in messages:
        if msg[0] == message_id:
            message_exists = True
            break

    if not message_exists:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.not_found.description",
                id=message_id,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Remove the message from the database
    await remove_message(message_id)

    # Send confirmation message
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.removescheduled.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.removescheduled.success.description",
            id=message_id,
        ),
    )
    await commandInfo.reply(embed=embed)
