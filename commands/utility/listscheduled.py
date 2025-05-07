import discord
from discord.ui import Button, View

import utility
from api import get_scheduled_messages
from localizer import tanjunLocalizer

MESSAGES_PER_PAGE = 1
MAX_CONTENT_LENGTH = 1000  # Maximum length for message content preview
MAX_EMBED_LENGTH = 6000  # Discord's maximum embed length


async def list_scheduled_messages(commandInfo: utility.commandInfo):
    class PaginationView(View):
        def __init__(self, messages, locale, page=0):
            super().__init__(timeout=300)  # 5 minute timeout
            self.messages = messages
            self.page = page
            self.max_pages = (len(messages) - 1) // MESSAGES_PER_PAGE
            self.locale = locale

            # Previous page button
            prev_button = Button(emoji="⬅️", style=discord.ButtonStyle.gray, disabled=page == 0)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)

            # Page counter button (disabled, just for display)
            self.page_counter = Button(
                label=tanjunLocalizer.localize(
                    locale,
                    "commands.utility.listscheduled.pagination.page_counter",
                    current=page + 1,
                    total=self.max_pages + 1,
                ),
                style=discord.ButtonStyle.gray,
                disabled=True,
            )
            self.add_item(self.page_counter)

            # Next page button
            next_button = Button(
                emoji="➡️",
                style=discord.ButtonStyle.gray,
                disabled=page == self.max_pages,
            )
            next_button.callback = self.next_page
            self.add_item(next_button)

        def truncate_content(self, content: str) -> str:
            """Truncate content and add ellipsis if necessary"""
            if len(content) <= MAX_CONTENT_LENGTH:
                return content
            return content[: MAX_CONTENT_LENGTH - 3] + "..."

        def get_embed(self):
            start_idx = self.page * MESSAGES_PER_PAGE
            page_messages = self.messages[start_idx : start_idx + MESSAGES_PER_PAGE]

            embed = utility.tanjunEmbed(title=tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.title"))

            current_length = len(embed.title)

            for msg in page_messages:
                # Truncate content
                content = self.truncate_content(msg[4])

                # Calculate field lengths
                field_name = tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.message_id", id=msg[0])

                field_value = tanjunLocalizer.localize(
                    self.locale,
                    "commands.utility.listscheduled.message_details",
                    content=content,
                    time=utility.date_time_to_timestamp(msg[5]),
                    channel=(
                        "<#" + str(msg[2]) + ">"
                        if msg[2]
                        else tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.direct_message")
                    ),
                    repeat=msg[6] or tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.no_repeat"),
                )

                # Check if adding this field would exceed the limit
                field_length = len(field_name) + len(field_value)
                if current_length + field_length > MAX_EMBED_LENGTH:
                    # Add a note about truncation
                    embed.add_field(
                        name=tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.truncated.title",
                        ),
                        value=tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.truncated.description",
                        ),
                        inline=False,
                    )
                    break

                embed.add_field(name=field_name, value=field_value, inline=False)
                current_length += field_length

            return embed

        async def previous_page(self, interaction: discord.Interaction):
            if interaction.user != commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.locale,
                        "commands.utility.listscheduled.error.not_authorized",
                    ),
                    ephemeral=True,
                )
                return

            self.page = max(0, self.page - 1)
            await self.update_message(interaction)

        async def next_page(self, interaction: discord.Interaction):
            if interaction.user != commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.locale,
                        "commands.utility.listscheduled.error.not_authorized",
                    ),
                    ephemeral=True,
                )
                return

            self.page = min(self.max_pages, self.page + 1)
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction):
            self.page_counter.label = tanjunLocalizer.localize(
                self.locale,
                "commands.utility.listscheduled.pagination.page_counter",
                current=self.page + 1,
                total=self.max_pages + 1,
            )

            for child in self.children:
                if isinstance(child, Button):
                    if child.emoji == "⬅️":
                        child.disabled = self.page == 0
                    elif child.emoji == "➡️":
                        child.disabled = self.page == self.max_pages

            await interaction.response.edit_message(
                embed=self.get_embed(),
                view=PaginationView(self.messages, self.locale, self.page),
            )

        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            if self.message:
                await self.message.edit(view=discord.ui.View())

    messages = await get_scheduled_messages(commandInfo.user.id)

    if not messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.listscheduled.no_messages.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.listscheduled.no_messages.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    view = PaginationView(messages, commandInfo.locale)
    view.user = commandInfo.user
    view.message = await commandInfo.reply(
        embed=view.get_embed(),
        view=view if len(messages) > MESSAGES_PER_PAGE else discord.ui.View(),
    )
