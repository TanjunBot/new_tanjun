from locale_keys import locale as l10n
from locale_keys.types import LocalizedString
import discord
from discord import app_commands
import utility
from utility import EmbedColor

async def help(command_info, ctx):

    class HelpSelect(discord.ui.Select):
        options = []
        cash = set()

        def __init__(self, client, options):
            self.client = client
            super().__init__(placeholder=l10n.commands.help.select.placeholder(command_info.locale), max_values=1, min_values=1, options=options)

        @classmethod
        def get_locale(cls, key, locale, **kwargs):
            key = key.replace('_', '.')
            if key in cls.cash:
                return key
            localized = LocalizedString(key)(locale, **kwargs)
            cls.cash.add(localized)
            return localized

        async def callback(self, interaction):
            texts = ['']
            current_index = 0
            total_length = 0
            loc = str(interaction.locale)
            char_limit = 750
            group_name_locale = self.get_locale(str(self.values[0]).replace('_', '.'), loc)
            for group in interaction.client.tree.walk_commands():
                if group.name == self.values[0]:
                    command_text = ''
                    if isinstance(group, app_commands.Group):
                        try:
                            group_desc = self.get_locale(group.description, loc)
                            command_text += f'{group_desc}\n\n'
                        except Exception:
                            command_text += self.get_locale('commands.utility.help.noDescriptionAvailable', loc, group_name=group.name)
                        for cmd in group.commands:
                            cmd_name_locale = self.get_locale(cmd.name, loc)
                            if isinstance(cmd, app_commands.Group):
                                command_text += f'### /{group_name_locale} {cmd_name_locale}\n'
                                try:
                                    cmd_desc = self.get_locale(cmd.description, loc)
                                    command_text += f'{cmd_desc}\n\n'
                                except Exception:
                                    command_text += l10n.commands.utility.help.noDescriptionAvailable(loc, group_name=cmd.name)
                                for subcmd in cmd.commands:
                                    subcmd_name_locale = self.get_locale(subcmd.name, loc)
                                    command_text += f'### /{group_name_locale} {cmd_name_locale} {subcmd_name_locale}\n'
                                    try:
                                        subcmd_desc = self.get_locale(subcmd.description, loc)
                                        command_text += f'{subcmd_desc}\n\n'
                                    except Exception:
                                        command_text += '\n'
                                    if hasattr(subcmd, 'parameters') and subcmd.parameters:
                                        command_text += l10n.commands.utility.help.parameters(loc)
                                        for param in subcmd.parameters:
                                            try:
                                                param_name = self.get_locale(param.name, loc)
                                                param_desc = self.get_locale(param.description, loc)
                                                command_text += f'- **{param_name}**: {param_desc}\n'
                                            except Exception:
                                                command_text += l10n.commands.utility.help.noDescriptionAvailable(loc, group_name=param.name)
                                        command_text += '\n'
                                    if len(texts[current_index] + command_text) > char_limit:
                                        current_index += 1
                                        texts.append('')
                                        texts[current_index] += command_text
                                        command_text = ''
                                        total_length = len(texts[current_index])
                            else:
                                command_text += f"### /{self.get_locale(str(group.name).replace('_', '.'), loc)} {self.get_locale(str(cmd.name).replace('_', '.'), loc)}\n"
                                try:
                                    cmd_desc = self.get_locale(cmd.description, loc)
                                    command_text += f'{cmd_desc}\n\n'
                                except Exception:
                                    command_text += l10n.commands.utility.help.noDescriptionAvailable(loc, group_name=cmd.name)
                                if hasattr(cmd, 'parameters') and cmd.parameters:
                                    command_text += '**Parameters:**\n'
                                    for param in cmd.parameters:
                                        try:
                                            param_name = self.get_locale(param.name, loc)
                                            param_desc = self.get_locale(param.description, loc)
                                            command_text += f'- **{param_name}**: {param_desc}\n'
                                        except Exception:
                                            command_text += l10n.commands.utility.help.noDescriptionAvailable(loc, group_name=param.name)
                                    command_text += '\n'
                                if len(texts[current_index] + command_text) > char_limit:
                                    current_index += 1
                                    texts.append('')
                                    total_length = len(texts[current_index])
                                texts[current_index] += command_text
                                command_text = ''
                                total_length += len(command_text)
            texts[current_index] += command_text
            command_text = ''
            total_length += len(command_text)
            embeds = []
            overall_length = 0
            for i, text in enumerate(texts, 1):
                overall_length += len(text)
                if text.strip():
                    if len(texts) > 1:
                        embed = discord.Embed(title=l10n.commands.utility.help.title(loc, group_name=group_name_locale, page=i, total_pages=len(texts)), description=text, color=EmbedColor.BRAND)
                    else:
                        embed = discord.Embed(title=l10n.commands.utility.help.titleNoPages(loc, group_name=group_name_locale), description=text, color=EmbedColor.BRAND)
                    embeds.append(embed)
            view = PaginatedHelpView(self.client, embeds) if len(embeds) > 1 else HelpView(self.client)
            await interaction.response.edit_message(embeds=[embeds[0]], view=view)

        @classmethod
        def generate_options(cls, client):
            options = []
            groups = []
            for cmd in client.tree.walk_commands():
                if cmd.parent is not None and cmd.parent.qualified_name not in groups:
                    groups.append(cmd.parent.qualified_name)
                    if ' ' not in cmd.parent.qualified_name:
                        name_key = str(cmd.parent.name).replace('_', '.')
                        desc_key = str(cmd.parent.description).replace('_', '.')
                        options.append(discord.SelectOption(label=LocalizedString(name_key)(command_info.locale), description=LocalizedString(desc_key)(command_info.locale), value=cmd.parent.qualified_name))
            if not options:
                options.append(discord.SelectOption(label=l10n.commands.utility.help.noCommands.label(command_info.locale), description=l10n.commands.utility.help.noCommands.description(command_info.locale), value='no_commands'))
            return options[:25]

    class PaginatedHelpView(discord.ui.View):

        def __init__(self, client, embeds):
            super().__init__(timeout=3600)
            self.embeds = embeds
            self.current_page = 0
            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))

        @discord.ui.button(label=l10n.commands.help.buttons.previous(command_info.locale), style=discord.ButtonStyle.gray)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page - 1) % len(self.embeds)
            await interaction.response.edit_message(embeds=[self.embeds[self.current_page]])

        @discord.ui.button(label=l10n.commands.help.buttons.next(command_info.locale), style=discord.ButtonStyle.gray)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = (self.current_page + 1) % len(self.embeds)
            await interaction.response.edit_message(embeds=[self.embeds[self.current_page]])

    class HelpView(discord.ui.View):

        def __init__(self, client, timeout=3600):
            super().__init__(timeout=timeout)
            options = HelpSelect.generate_options(client)
            self.add_item(HelpSelect(client, options))
    embed = utility.tanjunEmbed(title=l10n.commands.help.select.title(command_info.locale), description=l10n.commands.help.select.description(command_info.locale))
    await command_info.reply(embed=embed, view=HelpView(command_info.client))