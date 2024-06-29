import discord
from discord import ui
import utility
from utility import commandInfo, relativeTimeStrToDate, dateToRelativeTimeStr
from localizer import tanjunLocalizer
from typing import List, Optional
import asyncio
from commands.giveaway.utility import generateGiveawayEmbed, updateGiveawayMessage
from api import (
    get_giveaway,
    get_giveaway_role_requirements,
    get_giveaway_channel_requirements,
    update_giveaway,
)
import datetime
import commands.giveaway.start as start_giveaway


class GiveawayEditor(ui.View):
    def __init__(
        self,
        commandInfo,
        giveawayId,
    ):
        super().__init__(timeout=600)  # 10 minutes timeout
        self.commandInfo = commandInfo
        self.giveawayId = giveawayId
        self.giveaway_data = {}
        self.update_buttons()
        self.last_action = None
        self.generator_message = None

    async def load_giveaway_data(self):
        giveaway = await get_giveaway(self.giveawayId)
        if not giveaway:
            return False

        role_requirements = await get_giveaway_role_requirements(self.giveawayId)
        channel_requirements = await get_giveaway_channel_requirements(self.giveawayId)

        self.giveaway_data = {
            "title": giveaway[2],
            "description": giveaway[3],
            "winners": giveaway[4],
            "with_button": giveaway[5],
            "custom_name": giveaway[6],
            "sponsor": giveaway[7],
            "price": giveaway[8],
            "message": giveaway[9],
            "end_time": dateToRelativeTimeStr(giveaway[10]),
            "start_time": dateToRelativeTimeStr(giveaway[11]),
            "new_message_requirement": giveaway[14],
            "day_requirement": giveaway[15],
            "role_requirement": role_requirements,
            "voice_requirement": giveaway[16],
            "channel_requirements": channel_requirements,
            "target_channel": self.commandInfo.guild.get_channel(int(giveaway[18])),
        }
        return True

    def update_buttons(self):
        self.clear_items()

        # Add all the buttons
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.change_description",
                ),
                custom_id="change_description",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.change_winners.label",
                ),
                custom_id="change_winners",
                style=discord.ButtonStyle.primary,
            )
        )
        # self.add_item(    # Removed because of @2000Arion 😢 (he really hates fun :'c)
        #     GiveawayBuilderButton(
        #         label=tanjunLocalizer.localize(
        #             self.commandInfo.locale, "commands.giveaway.builder.with_button"
        #         ),
        #         custom_id="toggle_button",
        #         style=(
        #             discord.ButtonStyle.success
        #             if self.giveaway_data["with_button"]
        #             else discord.ButtonStyle.danger
        #         ),
        #     )
        # )
        # self.add_item(    # Removed because of @2000Arion 😢 (he really hates fun :'c)
        #     GiveawayBuilderButton(
        #         label=tanjunLocalizer.localize(
        #             self.commandInfo.locale, "commands.giveaway.builder.custom_name.label"
        #         ),
        #         custom_id="custom_name",
        #         style=discord.ButtonStyle.primary,
        #     )
        # )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.sponsor.label"
                ),
                custom_id="sponsor",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.price.label"
                ),
                custom_id="price",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.message.label"
                ),
                custom_id="message",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.end_time.label"
                ),
                custom_id="end_time",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.start_time.label",
                ),
                custom_id="start_time",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.new_message_requirement.label",
                ),
                custom_id="new_message_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.day_requirement.label",
                ),
                custom_id="day_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.role_requirement.label",
                ),
                custom_id="role_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.voice_requirement.label",
                ),
                custom_id="voice_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.add_channel_requirement.label",
                ),
                custom_id="add_channel_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        if "self.giveaway_data" in self.giveaway_data and self.giveaway_data["channel_requirements"]:
            self.add_item(
                start_giveaway.GiveawayBuilderButton(
                    label=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.giveaway.builder.remove_channel_requirement.label",
                    ),
                    custom_id="remove_channel_requirement",
                    style=discord.ButtonStyle.primary,
                )
            )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.preview"
                ),
                custom_id="preview",
                style=discord.ButtonStyle.secondary,
                row=3,
            )
        )
        self.add_item(
            start_giveaway.GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.confirm"
                ),
                custom_id="confirm",
                style=discord.ButtonStyle.success,
                row=3,
            )
        )

    async def update_embed(self, editmessage=None):
        self.update_buttons()
        embed = utility.tanjunEmbed(
            title=self.giveaway_data["title"],
            description=(f"## `{self.last_action}`\n\n" if self.last_action else "")
            + self.giveaway_data["description"],
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.winners"
            ),
            value=self.giveaway_data["winners"],
        )
        # embed.add_field(    # Removed because of @2000Arion 😢 (he really hates fun :'c)
        #     name=tanjunLocalizer.localize(
        #         self.commandInfo.locale, "commands.giveaway.builder.with_button"
        #     ),
        #     value=(
        #         tanjunLocalizer.localize(
        #             self.commandInfo.locale, "commands.giveaway.builder.true"
        #         )
        #         if self.giveaway_data["with_button"]
        #         else tanjunLocalizer.localize(
        #             self.commandInfo.locale, "commands.giveaway.builder.false"
        #         )
        #     ),
        # )
        # embed.add_field(   # Removed because of @2000Arion 😢 (he really hates fun :'c)
        #     name=tanjunLocalizer.localize(
        #         self.commandInfo.locale, "commands.giveaway.builder.custom_name.label"
        #     ),
        #     value=(
        #         self.giveaway_data["custom_name"]
        #         if self.giveaway_data["custom_name"]
        #         else tanjunLocalizer.localize(
        #             self.commandInfo.locale, "commands.giveaway.builder.none"
        #         )
        #     ),
        # )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.sponsor.label"
            ),
            value=(
                f"<@{self.giveaway_data['sponsor']}>"
                if self.giveaway_data["sponsor"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.price.label"
            ),
            value=(
                self.giveaway_data["price"]
                if self.giveaway_data["price"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.message.label"
            ),
            value=(
                self.giveaway_data["message"]
                if self.giveaway_data["message"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.end_time.label"
            ),
            value=(
                f"<t:{int(relativeTimeStrToDate(self.giveaway_data['end_time']).timestamp())}:R>"
                if self.giveaway_data["end_time"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.start_time.label"
            ),
            value=(
                f"<t:{int(relativeTimeStrToDate(self.giveaway_data['start_time']).timestamp())}:R>"
                if self.giveaway_data["start_time"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.new_message_requirement.label",
            ),
            value=(
                self.giveaway_data["new_message_requirement"]
                if self.giveaway_data["new_message_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.day_requirement.label",
            ),
            value=(
                self.giveaway_data["day_requirement"]
                if self.giveaway_data["day_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.role_requirement.label",
            ),
            value=(
                (
                    " ".join(
                        [
                            f"<@&{role}>"
                            for role in self.giveaway_data["role_requirement"]
                        ]
                    )
                )
                if self.giveaway_data["role_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.voice_requirement.label",
            ),
            value=(
                self.giveaway_data["voice_requirement"]
                if self.giveaway_data["voice_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.label",
            ),
            value=(
                "\n".join(
                    [
                        f"{self.commandInfo.guild.get_channel(int(channel_id)).mention}: {value}"
                        for channel_id, value in self.giveaway_data[
                            "channel_requirements"
                        ].items()
                    ]
                )
                if self.giveaway_data["channel_requirements"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        if not editmessage:
            await self.generator_message.edit(embed=embed, view=self, content="")
        else:
            await editmessage(embed=embed, view=self, content="")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.editor.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def button_callback(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if button.custom_id == "change_description":
            await self.change_description(interaction, button)
        elif button.custom_id == "change_winners":
            await self.change_winners(interaction, button)
        elif button.custom_id == "toggle_button":
            await self.toggle_button(interaction, button)
        elif button.custom_id == "custom_name":
            await self.custom_name(interaction, button)
        elif button.custom_id == "sponsor":
            await self.sponsor(interaction, button)
        elif button.custom_id == "price":
            await self.price(interaction, button)
        elif button.custom_id == "message":
            await self.message(interaction, button)
        elif button.custom_id == "end_time":
            await self.end_time(interaction, button)
        elif button.custom_id == "start_time":
            await self.start_time(interaction, button)
        elif button.custom_id == "new_message_requirement":
            await self.new_message_requirement(interaction, button)
        elif button.custom_id == "day_requirement":
            await self.day_requirement(interaction, button)
        elif button.custom_id == "role_requirement":
            await self.role_requirement(interaction, button)
        elif button.custom_id == "voice_requirement":
            await self.voice_requirement(interaction, button)
        elif button.custom_id == "add_channel_requirement":
            await self.add_channel_requirement(interaction, button)
        elif button.custom_id == "remove_channel_requirement":
            await self.remove_channel_requirement(interaction, button)
        elif button.custom_id == "preview":
            await self.preview(interaction, button)
        elif button.custom_id == "confirm":
            await self.confirm(interaction, button)

    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Update the giveaway in the database
        await update_giveaway(
            giveaway_id=self.giveawayId,
            guild_id=str(self.commandInfo.guild.id),
            title=self.giveaway_data["title"],
            description=self.giveaway_data["description"],
            winners=self.giveaway_data["winners"],
            with_button=self.giveaway_data["with_button"],
            custom_name=self.giveaway_data["custom_name"],
            sponsor=self.giveaway_data["sponsor"],
            price=self.giveaway_data["price"],
            message=self.giveaway_data["message"],
            endtime=relativeTimeStrToDate(self.giveaway_data["end_time"]),
            starttime=relativeTimeStrToDate(self.giveaway_data["start_time"]),
            new_message_requirement=self.giveaway_data["new_message_requirement"],
            day_requirement=self.giveaway_data["day_requirement"],
            channel_requirements=self.giveaway_data["channel_requirements"],
            role_requirement=self.giveaway_data["role_requirement"],
            voice_requirement=self.giveaway_data["voice_requirement"],
            channel_id=str(self.giveaway_data["target_channel"].id),
        )

        # Update the giveaway message
        await updateGiveawayMessage(self.giveawayId, self.commandInfo.client)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.editor.success.title"
            ),
            description=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.editor.success.description"
            ),
        )

        await interaction.response.edit_message(
            content=None, embed=embed, view=ui.View()
        )

    async def change_description(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_description"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.description.timeout"
            )
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data["description"] = message.content
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.description.updated"
            )
            await self.update_embed()

    async def change_winners(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        modal = start_giveaway.ChangeWinnersModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.change_winners.title",
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.change_winners.description",
            ),
        )

        await interaction.response.send_modal(modal)

    async def toggle_button(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        self.giveaway_data["with_button"] = not self.giveaway_data["with_button"]
        self.update_buttons()
        await self.update_embed(interaction.response.edit_message)

    async def custom_name(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = start_giveaway.CustomNameModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.custom_name.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.custom_name.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def sponsor(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        view = start_giveaway.SponsorView(self.commandInfo, self)
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.sponsor.select.placeholder",
            ),
            view=view,
            embed=None,
        )

    async def price(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_price"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.price.timeout"
            )
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data["price"] = message.content
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.price.updated"
            )
            await self.update_embed()

    async def message(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_message"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.message.timeout"
            )
            await self.update_embed()
        else:
            await message.delete()
            if len(message.content) > 128:
                self.last_action = tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.message.too_long",
                )
                await self.update_embed()
                return
            self.giveaway_data["message"] = message.content
            self.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.message.updated"
            )
            await self.update_embed()

    async def end_time(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        modal = start_giveaway.EndTimeModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.end_time.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.end_time.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def start_time(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = start_giveaway.StartTimeModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.start_time.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.start_time.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def new_message_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        modal = start_giveaway.MessageRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.new_message_requirement.title",
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.new_message_requirement.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def day_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = start_giveaway.DayRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.day_requirement.title",
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.day_requirement.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def role_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        view = start_giveaway.RoleRequirementView(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.role_requirement.title",
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.role_requirement.description",
            ),
        )
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.role_requirement.select",
            ),
            view=view,
            embed=None,
        )

    async def voice_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = start_giveaway.VoiceRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.voice_requirement.title",
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.voice_requirement.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def add_channel_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        view = start_giveaway.AddChannelRequirementView(self.commandInfo, self)

        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.select",
            ),
            embed=None,
            view=view,
        )

    async def preview(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        embed = await generateGiveawayEmbed(self.giveaway_data, self.commandInfo.locale)
        await interaction.response.send_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.preview"
            ),
            embed=embed,
            view=self,
        )

    async def remove_channel_requirement(
        self,
        interaction: discord.Interaction,
        button: start_giveaway.GiveawayBuilderButton,
    ):
        view = start_giveaway.RemoveChannelRequirementView(self.commandInfo, self)
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.remove_channel_requirement.select",
            ),
            embed=None,
            view=view,
        )


async def edit_giveaway(
    commandInfo,
    giveawayId,
):
    if not commandInfo.user.guild_permissions.manage_guild:
        await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale, "commands.giveaway.editor.no_permission"
            ),
        )
        return

    editor = GiveawayEditor(commandInfo, giveawayId)
    if not await editor.load_giveaway_data():
        await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale, "commands.giveaway.editor.not_found"
            ),
        )
        return

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.giveaway.editor.loading"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.giveaway.editor.loading"
        ),
    )
    message = await commandInfo.reply(embed=embed, view=editor)
    editor.generator_message = message
    await editor.update_embed()
