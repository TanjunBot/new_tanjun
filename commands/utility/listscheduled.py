from collections.abc import Callable, Coroutine
from typing import Any

import discord
from discord.ui import Button, Modal, TextInput, View

import utility
from localizer import tanjunLocalizer
from models import ScheduledMessageModel
from services.scheduled_message_service import ScheduledMessageService

MESSAGES_PER_PAGE = 1
MAX_CONTENT_LENGTH = 1000  # Maximum length for message content preview
MAX_EMBED_LENGTH = 6000  # Discord's maximum embed length


class EditContentModal(Modal):
    """Modal for editing the content of a scheduled message."""

    new_content: TextInput[Any] = TextInput(
        style=discord.TextStyle.paragraph,
        max_length=2000,
        required=True,
    )

    def __init__(self, message_id: int, current_content: str, locale: str, view: View) -> None:
        self.locale = locale
        super().__init__(
            title=tanjunLocalizer.localize(
                locale,
                "commands.utility.listscheduled.edit_modal.title",
            ),
            timeout=300,
        )
        self.message_id = message_id
        self.view = view
        self.new_content.label = tanjunLocalizer.localize(
            locale,
            "commands.utility.listscheduled.edit_modal.content_label",
        )
        self.new_content.default = current_content

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await ScheduledMessageService.update_content(self.message_id, self.new_content.value)

        # Update the in-memory model
        for msg in self.view.messages:
            if msg.message_id == self.message_id:
                msg.content = self.new_content.value
                break

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.locale,
                "commands.utility.listscheduled.edit_success.title",
            ),
            description=tanjunLocalizer.localize(
                self.locale,
                "commands.utility.listscheduled.edit_success.description",
                id=self.message_id,
            ),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def list_scheduled_messages(command_info: utility.CommandInfo) -> None:
    class PaginationView(View):
        def __init__(self, messages: list[ScheduledMessageModel], locale: str, page: int = 0) -> None:
            super().__init__(timeout=300)  # 5 minute timeout
            self.messages = messages
            self.page = page
            self.max_pages = (len(messages) - 1) // MESSAGES_PER_PAGE
            self.locale = locale

            prev_button: Button[Any] = Button(emoji="⬅️", style=discord.ButtonStyle.gray, disabled=page == 0)
            prev_button.callback = self.previous_page  # type: ignore[method-assign]
            self.add_item(prev_button)

            # Page counter button (disabled, just for display)
            self.page_counter: Button[Any] = Button(
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
            next_button: Button[Any] = Button(
                emoji="➡️",
                style=discord.ButtonStyle.gray,
                disabled=page == self.max_pages,
            )
            next_button.callback = self.next_page  # type: ignore[method-assign]
            self.add_item(next_button)

            # Edit and cancel buttons for the current page's message
            self._add_action_buttons()

        def _add_action_buttons(self) -> None:
            """Add edit and cancel buttons for the message on the current page."""
            start_idx = self.page * MESSAGES_PER_PAGE
            page_messages = self.messages[start_idx : start_idx + MESSAGES_PER_PAGE]

            for msg in page_messages:
                edit_button: Button[Any] = Button(
                    label=tanjunLocalizer.localize(
                        self.locale,
                        "commands.utility.listscheduled.edit_button",
                    ),
                    style=discord.ButtonStyle.primary,
                    emoji="✏️",
                    row=1,
                )
                edit_button.callback = self._make_edit_callback(msg)  # type: ignore[method-assign]
                self.add_item(edit_button)

                cancel_button: Button[Any] = Button(
                    label=tanjunLocalizer.localize(
                        self.locale,
                        "commands.utility.listscheduled.cancel_button",
                    ),
                    style=discord.ButtonStyle.danger,
                    emoji="🗑️",
                    row=1,
                )
                cancel_button.callback = self._make_cancel_callback(msg)  # type: ignore[method-assign]
                self.add_item(cancel_button)

        def _make_edit_callback(
            self, msg: ScheduledMessageModel
        ) -> Callable[[discord.Interaction], Coroutine[Any, Any, None]]:
            """Create a closure that opens the edit modal for *msg*."""

            async def _edit(interaction: discord.Interaction) -> None:
                if interaction.user != command_info.user:
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.error.not_authorized",
                        ),
                        ephemeral=True,
                    )
                    return
                modal = EditContentModal(
                    message_id=msg.message_id,
                    current_content=msg.content,
                    locale=self.locale,
                    view=self,
                )
                await interaction.response.send_modal(modal)

            return _edit

        def _make_cancel_callback(
            self, msg: ScheduledMessageModel
        ) -> Callable[[discord.Interaction], Coroutine[Any, Any, None]]:
            """Create a closure that cancels *msg*."""

            async def _cancel(interaction: discord.Interaction) -> None:
                if interaction.user != command_info.user:
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.error.not_authorized",
                        ),
                        ephemeral=True,
                    )
                    return

                await ScheduledMessageService.cancel(msg.message_id)

                # Remove the message from the local list
                self.messages = [m for m in self.messages if m.message_id != msg.message_id]
                self.max_pages = (len(self.messages) - 1) // MESSAGES_PER_PAGE if self.messages else 0
                if self.page > self.max_pages:
                    self.page = self.max_pages

                if not self.messages:
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.no_messages.title",
                        ),
                        description=tanjunLocalizer.localize(
                            self.locale,
                            "commands.utility.listscheduled.no_messages.description",
                        ),
                    )
                    await interaction.response.edit_message(embed=embed, view=discord.ui.View())
                    return

                await self.update_message(interaction)

            return _cancel

        def truncate_content(self, content: str) -> str:
            """Truncate content and add ellipsis if necessary"""
            if len(content) <= MAX_CONTENT_LENGTH:
                return content
            return content[: MAX_CONTENT_LENGTH - 3] + "..."

        def get_embed(self) -> discord.Embed:
            start_idx = self.page * MESSAGES_PER_PAGE
            page_messages = self.messages[start_idx : start_idx + MESSAGES_PER_PAGE]

            embed = utility.tanjunEmbed(title=tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.title"))

            current_length = len(embed.title) if embed.title else 0

            for msg in page_messages:
                # Truncate content
                content = self.truncate_content(msg.content)

                # Calculate field lengths
                field_name = tanjunLocalizer.localize(
                    self.locale, "commands.utility.listscheduled.message_id", id=msg.message_id
                )

                field_value = tanjunLocalizer.localize(
                    self.locale,
                    "commands.utility.listscheduled.message_details",
                    content=content,
                    time=utility.date_time_to_timestamp(msg.send_time),
                    channel=(
                        "<#" + str(msg.channel_id) + ">"
                        if msg.channel_id
                        else tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.direct_message")
                    ),
                    repeat=msg.repeat_interval
                    or tanjunLocalizer.localize(self.locale, "commands.utility.listscheduled.no_repeat"),
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

        async def previous_page(self, interaction: discord.Interaction) -> None:
            if interaction.user != command_info.user:
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

        async def next_page(self, interaction: discord.Interaction) -> None:
            if interaction.user != command_info.user:
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

        async def update_message(self, interaction: discord.Interaction) -> None:
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

        def set_message(self, message: discord.Message) -> None:
            self.message = message

        async def on_timeout(self) -> None:
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            if self.message is not None:
                await self.message.edit(view=discord.ui.View())

    messages = await ScheduledMessageService.get_user_messages(str(command_info.user.id))

    if not messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.listscheduled.no_messages.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.listscheduled.no_messages.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    view = PaginationView(messages, command_info.locale)
    view.set_message(
        await command_info.reply(
            embed=view.get_embed(),
            view=view,
        )
    )
