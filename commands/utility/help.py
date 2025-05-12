import discord
from discord import app_commands

import utility
from localizer import tanjunLocalizer
from typing import Any


async def help(commandInfo: utility.commandInfo) -> None:
    class HelpSelect(discord.ui.Select):
        cash: set[str] = set()

        def __init__(self, client: discord.ext.commands.Bot, options: list[discord.SelectOption]):
            self.client = client
            super().__init__(
                placeholder=tanjunLocalizer.localize(str(commandInfo.locale), "commands.help.select.placeholder"),
                max_values=1,
                min_values=1,
                options=options,
            )

        @classmethod
        def get_locale(self, key: str, locale: str, **kwargs: Any) -> str:
            key = key.replace("_", ".")
            if key in self.cash:
                return key

            localized = tanjunLocalizer.localize(locale, key, **kwargs)
            self.cash.add(localized)
            return localized

        async def callback(self, interaction: discord.Interaction) -> None:
            texts = [""]
            current_index = 0
            total_length = 0
            locale = str(interaction.locale)
            char_limit = 750

            group_name_locale = self.get_locale(
                str(self.values[0]).replace("_", "."),
                locale,
            )

            for group in self.client.tree.walk_commands():
                if group.name == self.values[0]:
                    command_text = ""

                    if isinstance(group, app_commands.Group):
                        try:
                            group_desc = self.get_locale(
                                group.description,
                                locale,
                            )
                            command_text += f"{group_desc}\n\n"
                        except Exception:
                            command_text += self.get_locale(
                                "commands.utility.help.noDescriptionAvailable",
                                commandInfo.locale,
                                group_name=group.name,
                            )

                        # Process each subcommand
                        for cmd in group.commands:
                            cmd_name_locale = self.get_locale(
                                cmd.name,
                                locale,
                            )
                            # Check if the command is a subcommand group
                            if isinstance(cmd, app_commands.Group):
                                command_text += f"### /{group_name_locale} {cmd_name_locale}\n"
                                try:
                                    cmd_desc = self.get_locale(
                                        cmd.description,
                                        locale,
                                    )
                                    command_text += f"{cmd_desc}\n\n"
                                except Exception:
                                    command_text += tanjunLocalizer.localize(
                                        commandInfo.locale,
                                        "commands.utility.help.noDescriptionAvailable",
                                        group_name=cmd.name,
                                    )

                                for subcmd in cmd.commands:
                                    subcmd_name_locale = self.get_locale(
                                        subcmd.name,
                                        locale,
                                    )
                                    command_text += f"### /{group_name_locale} {cmd_name_locale} {subcmd_name_locale}\n"
                                    try:
                                        subcmd_desc = self.get_locale(
                                            subcmd.description,
                                            locale,
                                        )
                                        command_text += f"{subcmd_desc}\n\n"
                                    except Exception:
                                        command_text += "\n"

                                    if hasattr(subcmd, "parameters") and subcmd.parameters:
                                        command_text += tanjunLocalizer.localize(
                                            commandInfo.locale,
                                            "commands.utility.help.parameters",
                                        )
                                        for param in subcmd.parameters:
                                            try:
                                                param_name = self.get_locale(
                                                    param.name,
                                                    locale,
                                                )
                                                param_desc = self.get_locale(
                                                    param.description,
                                                    locale,
                                                )
                                                command_text += f"- **{param_name}**: {param_desc}\n"
                                            except Exception:
                                                command_text += tanjunLocalizer.localize(
                                                    commandInfo.locale,
                                                    "commands.utility.help.noDescriptionAvailable",
                                                    group_name=param.name,
                                                )
                                        command_text += "\n"

                                    if len(texts[current_index] + command_text) > char_limit:
                                        current_index += 1
                                        texts.append("")
                                        texts[current_index] += command_text
                                        command_text = ""
                                        total_length = len(texts[current_index])
                            else:
                                command_text += f"### /{self.get_locale(str(group.name).replace('_', '.'), locale)} {self.get_locale(str(cmd.name).replace('_', '.'), locale)}\n"
                                try:
                                    cmd_desc = self.get_locale(
                                        cmd.description,
                                        locale,
                                    )
                                    command_text += f"{cmd_desc}\n\n"
                                except Exception:
                                    command_text += tanjunLocalizer.localize(
                                        commandInfo.locale,
                                        "commands.utility.help.noDescriptionAvailable",
                                        group_name=cmd.name,
                                    )

                                # Process parameters only if they exist
                                if hasattr(cmd, "parameters") and cmd.parameters:
                                    command_text += "**Parameters:**\n"
                                    for param in cmd.parameters:
                                        try:
                                            param_name = self.get_locale(
                                                param.name,
                                                locale,
                                            )
                                            param_desc = self.get_locale(
                                                param.description,
                                                locale,
                                            )
                                            command_text += f"- **{param_name}**: {param_desc}\n"
                                        except Exception:
                                            command_text += tanjunLocalizer.localize(
                                                commandInfo.locale,
                                                "commands.utility.help.noDescriptionAvailable",
                                                group_name=param.name,
                                            )
                                    command_text += "\n"

                                if len(texts[current_index] + command_text) > char_limit:
                                    current_index += 1
                                    texts.append("")
                                    total_length = len(texts[current_index])

                                texts[current_index] += command_text
                                command_text = ""
                                total_length += len(command_text)

            texts[current_index] += command_text
            command_text = ""
            total_length += len(command_text)

            # Create embeds
            embeds = []
            overall_length = 0
            for i, text in enumerate(texts, 1):
                overall_length += len(text)
                if text.strip():
                    if len(texts) > 1:
                        embed = discord.Embed(
                            title=tanjunLocalizer.localize(
                                commandInfo.locale,
                                "commands.utility.help.title",
                                group_name=group_name_locale,
                                page=i,
                                total_pages=len(texts),
                            ),
                            description=text,
                            color=0xCB33F5,
                        )
                    else:
                        embed = discord.Embed(
                            title=tanjunLocalizer.localize(
                                commandInfo.locale,
                                "commands.utility.help.titleNoPages",
                                group_name=group_name_locale,
                            ),
                            description=text,
                            color=0xCB33F5,
                        )
                    embeds.append(embed)

            view = PaginatedHelpView(self.client, embeds) if len(embeds) > 1 else HelpView(self.client)
            await interaction.response.edit_message(embeds=[embeds[0]], view=view)

        @classmethod
        def generate_options(self, client: discord.ext.commands.Bot) -> list[discord.SelectOption]:
            options = []
            groups = []
            for cmd in client.tree.walk_commands():
                if cmd.parent is not None:
                    if cmd.parent.qualified_name not in groups:
                        groups.append(cmd.parent.qualified_name)
                        if " " not in cmd.parent.qualified_name:
                            options.append(
                                discord.SelectOption(
                                    label=tanjunLocalizer.localize(
                                        commandInfo.locale,
                                        str(cmd.parent.name).replace("_", "."),
                                    ),
                                    description=tanjunLocalizer.localize(
                                        commandInfo.locale,
                                        str(cmd.parent.description).replace("_", "."),
                                    ),
                                    value=cmd.parent.qualified_name,
                                )
                            )
            if not options:
                options.append(
                    discord.SelectOption(
                        label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.help.noCommands.label"),
                        description=tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.utility.help.noCommands.description",
                        ),
                        value="no_commands",
                    )
                )
            return options[:25]

    class PaginatedHelpView(discord.ui.View):
        def __init__(self, client: discord.ext.commands.Bot, embeds: list[discord.Embed]):
            super().__init__(timeout=3600)
            self.embeds = embeds
            self.current_page = 0

            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.help.buttons.previous"),
            style=discord.ButtonStyle.gray,
        )
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            self.current_page = (self.current_page - 1) % len(self.embeds)
            await interaction.response.edit_message(embeds=[self.embeds[self.current_page]])

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.help.buttons.next"),
            style=discord.ButtonStyle.gray,
        )
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            self.current_page = (self.current_page + 1) % len(self.embeds)
            await interaction.response.edit_message(embeds=[self.embeds[self.current_page]])

    class HelpView(discord.ui.View):
        def __init__(self, client: discord.ext.commands.Bot, timeout: int=3600):
            super().__init__(timeout=timeout)
            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.help.select.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.help.select.description"),
    )
    if commandInfo.bot is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "errors.unexspected.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "errors.unexspected.description"),
        )
        await commandInfo.reply(embed = embed)
        return
    await commandInfo.reply(embed=embed, view=HelpView(commandInfo.bot))
