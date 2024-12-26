import discord
from discord import app_commands
import utility
from localizer import tanjunLocalizer


async def help(commandInfo, ctx):

    class HelpSelect(discord.ui.Select):

        options = []

        def __init__(self, client, options):
            self.client = client
            super().__init__(
                placeholder=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.help.select.placeholder"
                ),
                max_values=1,
                min_values=1,
                options=options,
            )

        async def callback(self, interaction):
            texts = [""]
            current_index = 0
            total_length = 0
            locale = interaction.locale
            char_limit = 3500

            for group in interaction.client.tree.walk_commands():
                if group.name == self.values[0]:
                    command_text = ""

                    # Handle command group
                    if isinstance(group, app_commands.Group):
                        try:
                            group_desc = tanjunLocalizer.localize(
                                locale, f"{str(group.description)}"
                            )
                            command_text += f"{group_desc}\n\n"
                        except Exception:
                            command_text += (
                                f"*No description available for {group.name}*\n\n"
                            )

                        # Process each subcommand
                        for cmd in group.commands:
                            # Check if the command is a subcommand group
                            if isinstance(cmd, app_commands.Group):
                                command_text += f"### /{group.name} {tanjunLocalizer.localize(locale, str(cmd.name).replace('_', '.'))}\n"
                                try:
                                    cmd_desc = tanjunLocalizer.localize(
                                        locale,
                                        f"{str(cmd.description).replace('_', '.')}",
                                    )
                                    command_text += f"{cmd_desc}\n\n"
                                except Exception:
                                    command_text += (
                                        f"*No description available for {cmd.name}*\n\n"
                                    )

                                # Process subcommands within the subcommand group
                                for subcmd in cmd.commands:
                                    command_text += f"### /{group.name} {tanjunLocalizer.localize(locale, str(cmd.name).replace('_', '.'))} {tanjunLocalizer.localize(locale, str(subcmd.name).replace('_', '.'))}\n"
                                    try:
                                        subcmd_desc = tanjunLocalizer.localize(
                                            locale,
                                            f"{str(subcmd.description).replace('_', '.')}",
                                        )
                                        command_text += f"{subcmd_desc}\n\n"
                                    except Exception:
                                        command_text += "\n"

                                    # Process parameters for subcommands
                                    if (
                                        hasattr(subcmd, "parameters")
                                        and subcmd.parameters
                                    ):
                                        command_text += "**Parameters:**\n"
                                        for param in subcmd.parameters:
                                            try:
                                                param_name = tanjunLocalizer.localize(
                                                    locale,
                                                    f"{param.name.replace('_', '.')}",
                                                )
                                                param_desc = tanjunLocalizer.localize(
                                                    locale,
                                                    f"{param.description.replace('_', '.')}",
                                                )
                                                command_text += f"- **{param_name}**: {param_desc}\n"
                                            except Exception:
                                                command_text += f"- **{param.name}**: *No description available*\n"
                                        command_text += "\n"

                                    if (
                                        len(texts[current_index] + command_text)
                                        > char_limit
                                    ):
                                        current_index += 1
                                        texts.append("")
                                        texts[current_index] += command_text
                                        command_text = ""
                                        total_length = len(texts[current_index])
                            else:
                                # Original code for regular commands
                                command_text += f"### /{group.name} {tanjunLocalizer.localize(locale, str(cmd.name).replace('_', '.'))}\n"
                                try:
                                    cmd_desc = tanjunLocalizer.localize(
                                        locale,
                                        f"{str(cmd.description).replace('_', '.')}",
                                    )
                                    command_text += f"{cmd_desc}\n\n"
                                except Exception:
                                    command_text += (
                                        f"*No description available for {cmd.name}*\n\n"
                                    )

                                # Process parameters only if they exist
                                if hasattr(cmd, "parameters") and cmd.parameters:
                                    command_text += "**Parameters:**\n"
                                    for param in cmd.parameters:
                                        try:
                                            param_name = tanjunLocalizer.localize(
                                                locale,
                                                f"{param.name.replace('_', '.')}",
                                            )
                                            param_desc = tanjunLocalizer.localize(
                                                locale,
                                                f"{param.description.replace('_', '.')}",
                                            )
                                            command_text += (
                                                f"- **{param_name}**: {param_desc}\n"
                                            )
                                        except Exception:
                                            command_text += f"- **{param.name}**: *No description available*\n"
                                    command_text += "\n"

                                if (
                                    len(texts[current_index] + command_text)
                                    > char_limit
                                ):
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
                    embed = discord.Embed(
                        title=(
                            f"{self.values[0]}"
                            + (f" - Page {i}/{len(texts)}" if len(texts) > 1 else "")
                            if len(texts) > 1
                            else None
                        ),
                        description=text,
                        color=0xCB33F5,
                    )
                    embeds.append(embed)

            view = (
                PaginatedHelpView(self.client, embeds)
                if len(embeds) > 1
                else HelpView(self.client)
            )
            await interaction.response.edit_message(embeds=[embeds[0]], view=view)

        @classmethod
        def generate_options(self, client):
            options = []
            groups = []
            for cmd in client.tree.walk_commands():
                if cmd.parent is not None:
                    if cmd.parent.qualified_name not in groups:
                        groups.append(cmd.parent.qualified_name)
                        if " " not in cmd.parent.qualified_name:
                            options.append(
                                discord.SelectOption(
                                    label=cmd.parent.qualified_name,
                                    description=cmd.parent.description,
                                    value=cmd.parent.qualified_name,
                                )
                            )
            if not options:
                options.append(
                    discord.SelectOption(
                        label="No Commands",
                        description="No commands available",
                        value="no_commands",
                    )
                )
            return options[:25]

    class PaginatedHelpView(discord.ui.View):
        def __init__(self, client, embeds):
            super().__init__(timeout=3600)
            self.embeds = embeds
            self.current_page = 0

            # Add the select menu
            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.help.buttons.previous"
            ),
            style=discord.ButtonStyle.gray,
        )
        async def previous_button(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.current_page = (self.current_page - 1) % len(self.embeds)
            await interaction.response.edit_message(
                embeds=[self.embeds[self.current_page]]
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.help.buttons.next"
            ),
            style=discord.ButtonStyle.gray,
        )
        async def next_button(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.current_page = (self.current_page + 1) % len(self.embeds)
            await interaction.response.edit_message(
                embeds=[self.embeds[self.current_page]]
            )

    class HelpView(discord.ui.View):
        def __init__(self, client, timeout=3600):
            super().__init__(timeout=timeout)
            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.help.select.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.help.select.description"
        ),
    )
    await commandInfo.reply(embed=embed, view=HelpView(commandInfo.client))
