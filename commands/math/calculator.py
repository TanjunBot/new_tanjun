import discord
from discord import ui
from typing import List, Dict, Optional
import utility
from localizer import tanjunLocalizer

ADDEMOJI = "math_add:1254372629456883793"
SUBSTRACTEMOJI = "math_substract:1254372627766837248"
MULTIPLYEMOJI = "math_multiply:1254372798319558768"
DIVIDEEMOJI = "math_divide:1254373636224323644"
BACKSPACEEMOJI = "math_backspace:1254371946695757854"


class CalculatorButton(ui.Button):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        custom_id: str,
        row: int,
        emoji: Optional[str] = None,
        disabled: bool = False,
    ):
        super().__init__(
            label=label,
            style=style,
            custom_id=custom_id,
            row=row,
            emoji=emoji,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: CalculatorView = self.view
        await view.button_callback(interaction, self.custom_id)


class CalculatorView(ui.View):
    def __init__(self, command_info: utility.commandInfo, initial_equation: str = ""):
        super().__init__(timeout=300)
        self.command_info = command_info
        self.display_equation = initial_equation
        self.equation = initial_equation
        self.result = ""
        self.history: List[str] = []
        self.variables: Dict[str, float] = {}
        self.current_page = 0
        self.create_buttons()
        self.nsp = utility.NumericStringParser()

    def set_message(self, message: discord.Message):
        self.message = message

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale, "commands.math.calculator.unauthorizedUser"
                ),
                ephemeral=True,
            )
            return False
        return True

    def create_buttons(self):
        self.clear_items()
        if self.current_page == 0:
            buttons = [
                ("7", discord.ButtonStyle.secondary, "7", 0, None),
                ("8", discord.ButtonStyle.secondary, "8", 0, None),
                ("9", discord.ButtonStyle.secondary, "9", 0, None),
                (
                    "",
                    discord.ButtonStyle.danger,
                    "backspace",
                    0,
                    BACKSPACEEMOJI,
                ),
                ("AC", discord.ButtonStyle.danger, "clear", 0, None),
                ("4", discord.ButtonStyle.secondary, "4", 1, None),
                ("5", discord.ButtonStyle.secondary, "5", 1, None),
                ("6", discord.ButtonStyle.secondary, "6", 1, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "multiply",
                    1,
                    MULTIPLYEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "divide",
                    1,
                    DIVIDEEMOJI,
                ),
                ("1", discord.ButtonStyle.secondary, "1", 2, None),
                ("2", discord.ButtonStyle.secondary, "2", 2, None),
                ("3", discord.ButtonStyle.secondary, "3", 2, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "add",
                    2,
                    ADDEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "subtract",
                    2,
                    SUBSTRACTEMOJI,
                ),
                ("0", discord.ButtonStyle.secondary, "0", 3, None),
                (".", discord.ButtonStyle.secondary, "decimal", 3, None),
                ("%", discord.ButtonStyle.secondary, "modulo", 3, None),
                ("(", discord.ButtonStyle.secondary, "left_paren", 3, None),
                (")", discord.ButtonStyle.secondary, "right_paren", 3, None),
                ("🠜", discord.ButtonStyle.primary, "prev_page", 4, None),
                ("🠞", discord.ButtonStyle.primary, "next_page", 4, None),
                ("π", discord.ButtonStyle.secondary, "pi", 4, None),
                ("e", discord.ButtonStyle.secondary, "e", 4, None),
                ("=", discord.ButtonStyle.success, "equals", 4, None),
            ]
        elif self.current_page == 1:
            buttons = [
                ("sin", discord.ButtonStyle.secondary, "sin", 0, None),
                ("cos", discord.ButtonStyle.secondary, "cos", 0, None),
                ("tan", discord.ButtonStyle.secondary, "tan", 0, None),
                (
                    "",
                    discord.ButtonStyle.danger,
                    "backspace",
                    0,
                    BACKSPACEEMOJI,
                ),
                ("AC", discord.ButtonStyle.danger, "clear", 0, None),
                ("x²", discord.ButtonStyle.secondary, "square", 1, None),
                ("xʸ", discord.ButtonStyle.secondary, "power", 1, None),
                ("√", discord.ButtonStyle.secondary, "sqrt", 1, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "multiply",
                    1,
                    MULTIPLYEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "divide",
                    1,
                    DIVIDEEMOJI,
                ),
                ("asin", discord.ButtonStyle.secondary, "asin", 2, None),
                ("acos", discord.ButtonStyle.secondary, "acos", 2, None),
                ("atan", discord.ButtonStyle.secondary, "atan", 2, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "add",
                    2,
                    ADDEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "subtract",
                    2,
                    SUBSTRACTEMOJI,
                ),
                ("X", discord.ButtonStyle.secondary, "x", 3, None),
                ("Y", discord.ButtonStyle.secondary, "y", 3, None),
                ("A", discord.ButtonStyle.secondary, "a", 3, None),
                ("B", discord.ButtonStyle.secondary, "b", 3, None),
                ("C", discord.ButtonStyle.secondary, "c", 3, None),
                ("🠜", discord.ButtonStyle.primary, "prev_page", 4, None),
                ("🠞", discord.ButtonStyle.primary, "next_page", 4, None),
                (":=", discord.ButtonStyle.secondary, "assign", 4, None),
                ("ⁿ√", discord.ButtonStyle.secondary, "nthroot", 4, None),
                ("=", discord.ButtonStyle.success, "equals", 4, None),
            ]
        elif self.current_page == 2:
            buttons = [
                ("log₂", discord.ButtonStyle.secondary, "log2", 0, None),
                ("ln", discord.ButtonStyle.secondary, "ln", 0, None),
                ("log₁₀", discord.ButtonStyle.secondary, "log10", 0, None),
                (
                    "",
                    discord.ButtonStyle.danger,
                    "backspace",
                    0,
                    BACKSPACEEMOJI,
                ),
                ("AC", discord.ButtonStyle.danger, "clear", 0, None),
                ("⌊", discord.ButtonStyle.secondary, "left_floor", 1, None),
                ("⌋", discord.ButtonStyle.secondary, "right_floor", 1, None),
                ("⠀", discord.ButtonStyle.secondary, "empty1", 1, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "multiply",
                    1,
                    MULTIPLYEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "divide",
                    1,
                    DIVIDEEMOJI,
                ),
                ("⌈", discord.ButtonStyle.secondary, "left_ceil", 2, None),
                ("⌉", discord.ButtonStyle.secondary, "right_ceil", 2, None),
                ("⠀", discord.ButtonStyle.secondary, "empty2", 2, None),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "add",
                    2,
                    ADDEMOJI,
                ),
                (
                    "",
                    discord.ButtonStyle.primary,
                    "subtract",
                    2,
                    SUBSTRACTEMOJI,
                ),
                ("⠀", discord.ButtonStyle.secondary, "empty3", 3, None),
                ("⠀", discord.ButtonStyle.secondary, "empty4", 3, None),
                ("⠀", discord.ButtonStyle.secondary, "empty5", 3, None),
                ("⠀", discord.ButtonStyle.secondary, "empty6", 3, None),
                ("⠀", discord.ButtonStyle.secondary, "empty7", 3, None),
                ("🠜", discord.ButtonStyle.primary, "prev_page", 4, None),
                ("🠞", discord.ButtonStyle.primary, "next_page", 4, None),
                ("⠀", discord.ButtonStyle.secondary, "empty8", 4, None),
                ("⠀", discord.ButtonStyle.secondary, "empty9", 4, None),
                ("=", discord.ButtonStyle.success, "equals", 4, None),
            ]

        for label, style, custom_id, row, emoji in buttons:
            self.add_item(
                CalculatorButton(
                    label=label,
                    style=style,
                    custom_id=custom_id,
                    row=row,
                    emoji=emoji,
                    disabled="empty" in custom_id,
                )
            )

    async def button_callback(self, interaction: discord.Interaction, button_id: str):
        if button_id == "clear":
            self.display_equation = ""
            self.equation = ""
            self.result = ""
        elif button_id == "equals":
            try:
                self.result = str(round(self.nsp.eval(self.equation), 5))
                self.history.append(f"{self.display_equation} = {self.result}")
                self.variables["ans"] = float(self.result)
                self.display_equation = self.result
                self.equation = self.result
            except Exception as e:
                self.result = tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.math.calculator.error",
                    error=str(e),
                )
        elif button_id == "backspace":
            if self.equation[-5:] in ("asin(", "acos(", "atan(", "sqrt(", "log2("):
                self.display_equation = self.display_equation[:-5]
                self.equation = self.equation[:-5]
            elif self.equation[-4:] in ("sin(", "cos(", "tan("):
                self.display_equation = self.display_equation[:-4]
                self.equation = self.equation[:-4]
            elif self.equation[-3:] in ("log", "ln(", "log"):
                self.display_equation = self.display_equation[:-3]
                self.equation = self.equation[:-3]
            elif self.equation[-4:] in ("log2", "log10"):
                self.display_equation = self.display_equation[:-4]
                self.equation = self.equation[:-4]
            elif self.equation[-3:] in (
                "abs",
                "sin",
                "cos",
                "tan",
                "log",
                "log",
                "ln",
                "nth",
                "sqrt",
                "ceil",
                "floor",
                "Rand",
            ):
                self.display_equation = self.display_equation[:-3]
                self.equation = self.equation[:-3]
            elif self.equation[-2:] in ("pi"):
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-2]
            elif self.equation[-4:] in ("^(2)"):
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-4]
            elif self.equation[-6:] in ("log10("):
                self.display_equation = self.display_equation[:-6]
                self.equation = self.equation[:-6]
            elif self.equation[-6:] in ("floor("):
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-6]
            elif self.equation[-5:] in ("ceil("):
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-5]
            elif self.equation[-4:] in ("abs("):
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-4]
            else:
                self.display_equation = self.display_equation[:-1]
                self.equation = self.equation[:-1]

        elif button_id in ("prev_page", "next_page"):
            self.current_page = (
                (self.current_page + 1) % 3
                if button_id == "next_page"
                else (self.current_page - 1) % 3
            )
            self.create_buttons()
        elif button_id == "assign":
            parts = self.equation.split(":=")
            if len(parts) == 2:
                var_name, var_value = parts
                try:
                    self.variables[var_name.strip()] = self.nsp.eval(var_value.strip())
                    self.result = f"{var_name} = {self.variables[var_name]}"
                except Exception as e:
                    self.result = tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.math.calculator.error",
                        error=str(e),
                    )
            else:
                self.result = tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.math.calculator.invalid_assignment",
                )
            self.display_equation = ""
            self.equation = ""
        else:
            if self.result and button_id not in (
                "add",
                "subtract",
                "multiply",
                "divide",
                "left_paren",
                "right_paren",
            ):
                self.display_equation = ""
                self.equation = ""
            if button_id in (
                "sin",
                "cos",
                "tan",
                "asin",
                "acos",
                "atan",
                "log2",
                "ln",
                "log10",
                "sqrt",
                "nthroot",
            ):
                self.display_equation += button_id + "("
                self.equation += button_id + "("
            elif button_id == "pi":
                self.display_equation += "π"
                self.equation += "pi"
            elif button_id == "e":
                self.display_equation += "e"
                self.equation += "e"
            elif button_id in ("x", "y", "a", "b", "c", "ans"):
                self.display_equation += button_id
                self.equation += button_id
            elif button_id == "square":
                self.display_equation += "²"
                self.equation += "^(2)"
            elif button_id == "power":
                self.display_equation += "^"
                self.equation += "^"
            elif button_id == "rand":
                self.display_equation += "Rand("
                self.equation += "rand("
            elif button_id == "left_floor":
                self.display_equation += "⌊"
                self.equation += "floor("
            elif button_id == "left_ceil":
                self.display_equation += "⌈"
                self.equation += "ceil("
            elif button_id == "left_paren":
                self.display_equation += "("
                self.equation += "("
            elif button_id == "right_paren":
                self.display_equation += ")"
                self.equation += ")"
            elif button_id == "right_floor":
                self.display_equation += "⌋"
                self.equation += ")"
            elif button_id == "right_ceil":
                self.display_equation += "⌉"
                self.equation += ")"
            elif button_id == "decimal":
                self.display_equation += "." if self.display_equation else "0."
                self.equation += "." if self.equation else "0."
            elif button_id == "modulo":
                self.display_equation += "%"
                self.equation += "%"
            else:
                self.display_equation += (
                    button_id
                    if button_id not in ("multiply", "divide", "add", "subtract")
                    else {"multiply": "*", "divide": "/", "add": "+", "subtract": "-"}[
                        button_id
                    ]
                )
                self.equation += (
                    button_id
                    if button_id not in ("multiply", "divide", "add", "subtract")
                    else {"multiply": "*", "divide": "/", "add": "+", "subtract": "-"}[
                        button_id
                    ]
                )
            self.result = ""

        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.command_info.locale, "commands.math.calculator.title"
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.command_info.locale, "commands.math.calculator.equation"
            ),
            value=f"```\n{self.display_equation or '0'}\n```",
            inline=False,
        )
        if self.result:
            embed.add_field(
                name=tanjunLocalizer.localize(
                    self.command_info.locale, "commands.math.calculator.result"
                ),
                value=f"```\n{self.result}\n```",
                inline=False,
            )
        if self.history:
            history_text = "\n".join(self.history[-5:])
            embed.add_field(
                name=tanjunLocalizer.localize(
                    self.command_info.locale, "commands.math.calculator.history"
                ),
                value=f"```\n{history_text}\n```",
                inline=False,
            )
        await interaction.response.edit_message(embed=embed, view=self)


async def calculator_command(
    command_info: utility.commandInfo, initial_equation: str = ""
):
    view = CalculatorView(command_info, initial_equation)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale, "commands.math.calculator.title"
        ),
    )
    embed.add_field(
        name=tanjunLocalizer.localize(
            command_info.locale, "commands.math.calculator.equation"
        ),
        value=f"```\n{initial_equation or '0'}\n```",
        inline=False,
    )
    message = await command_info.reply(embed=embed, view=view)
    view.set_message(message)
