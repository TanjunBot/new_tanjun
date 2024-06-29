import discord
import io
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize, integrate
import utility
from localizer import tanjunLocalizer
from utility import NumericStringParser
import re
import asyncio
from typing import List, Tuple, Callable
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from sympy import Symbol, diff, parse_expr
import sympy as sp


async def plot_function_command(
    commandInfo: utility.commandInfo,
    func_str: str,
    x_min: float = None,
    x_max: float = None,
):

    class FunctionPlotter:
        def __init__(self, commandInfo: utility.commandInfo, author_id: int):
            self.commandInfo = commandInfo
            self.author_id = author_id
            self.functions: List[Tuple[str, Callable]] = []
            self.x_min = -10
            self.x_max = 10
            self.y_min = -10
            self.y_max = 10
            self.plot_title = tanjunLocalizer.localize(
                locale = commandInfo.locale, key = "commands.math.plotfunction.default_title"
            )
            self.x_label = tanjunLocalizer.localize(
                locale = commandInfo.locale, key = "commands.math.plotfunction.default_x_label"
            )
            self.y_label = tanjunLocalizer.localize(
                locale = commandInfo.locale, key = "commands.math.plotfunction.default_y_label"
            )
            self.style = "default"

        async def add_function(self, func_str: str, name: str):
            func = await self.parse_function(func_str)
            self.functions.append((func_str, func, name))

        async def parse_function(self, func_str: str) -> Callable:
            func_str = func_str.replace("^", "**")
            func_str = re.sub(r"(\d+)([a-zA-Z\(])", r"\1*\2", func_str)
            func_str = func_str.replace("sin", "np.sin")
            func_str = func_str.replace("cos", "np.cos")
            func_str = func_str.replace("tan", "np.tan")
            func_str = func_str.replace("exp", "np.exp")
            func_str = func_str.replace("log", "np.log")
            func_str = func_str.replace("sqrt", "np.sqrt")

            return lambda x: eval(func_str, {"x": x, "np": np})

        async def find_zeros(self, func: Callable) -> List[float]:
            x = np.linspace(self.x_min, self.x_max, 1000)
            y = func(x)
            zero_crossings = np.where(np.diff(np.sign(y)))[0]
            zeros = []
            for i in zero_crossings:
                zero = await asyncio.to_thread(optimize.brentq, func, x[i], x[i + 1])
                zeros.append(zero)
            return zeros

        async def find_extrema(self, func: Callable) -> List[Tuple[float, float]]:
            x = np.linspace(self.x_min, self.x_max, 1000)
            y = func(x)
            extrema = []
            for i in range(1, len(x) - 1):
                if (y[i - 1] < y[i] and y[i] > y[i + 1]) or (
                    y[i - 1] > y[i] and y[i] < y[i + 1]
                ):
                    extrema.append((x[i], y[i]))
            return extrema

        async def find_inflection_points(
            self, func: Callable
        ) -> List[Tuple[float, float]]:
            def second_derivative(x):
                h = 1e-5
                return (func(x + h) - 2 * func(x) + func(x - h)) / (h**2)

            x = np.linspace(self.x_min, self.x_max, 1000)
            y_second = np.array([second_derivative(xi) for xi in x])
            inflection_points = []
            for i in range(1, len(x) - 1):
                if y_second[i - 1] * y_second[i + 1] < 0:
                    inflection_points.append((x[i], func(x[i])))
            return inflection_points

        async def find_intersection_points(self) -> List[Tuple[float, float]]:
            if len(self.functions) < 2:
                return []

            def diff_func(x):
                return self.functions[0][1](x) - self.functions[1][1](x)

            x = np.linspace(self.x_min, self.x_max, 1000)
            y = diff_func(x)
            zero_crossings = np.where(np.diff(np.sign(y)))[0]
            intersections = []
            for i in zero_crossings:
                intersection = await asyncio.to_thread(
                    optimize.brentq, diff_func, x[i], x[i + 1]
                )
                intersections.append((intersection, self.functions[0][1](intersection)))
            return intersections

        async def rename_function(self, function_index: int, new_name: str):
            func_str, func, old_name = self.functions[function_index]
            self.functions[function_index] = (func_str, func, new_name)

        async def integrate_function(self, func_str: str, name: str):
            x = sp.Symbol("x")
            # Replace ^ with ** for exponentiation
            func_str = func_str.replace("^", "**")
            expr = sp.parsing.sympy_parser.parse_expr(func_str)
            integral = sp.integrate(expr, x)
            integral_str = str(integral).replace("**", "^")
            await self.add_function(integral_str, f"∫{name}")

        async def generate_plot(self) -> io.BytesIO:
            plt.close("all")

            plt.style.use(self.style)

            x = np.linspace(self.x_min, self.x_max, 10000)
            for func_str, func, name in self.functions:
                y = func(x)
                plt.plot(x, y, label=f"{name}(x) = {func_str}", zorder=187)

            plt.xlabel(self.x_label)
            plt.ylabel(self.y_label)
            plt.title(self.plot_title)
            plt.xlim(self.x_min, self.x_max)
            plt.ylim(self.y_min, self.y_max)
            plt.legend()
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.close("all")

            return buf

        def create_embed(self) -> discord.Embed:
            embed = utility.tanjunEmbed(
                title=self.plot_title,
                description=tanjunLocalizer.localize(
                    locale = self.commandInfo.locale,
                    key = "commands.math.plotfunction.description",
                    x_min=self.x_min,
                    x_max=self.x_max,
                ),
            )

            for i, (func_str, func, name) in enumerate(self.functions):
                embed.add_field(name=f"{name}(x)", value=func_str, inline=False)

            embed.set_image(url="attachment://function_plot.png")
            return embed

    class AddFunctionModal(
        discord.ui.Modal,
        title=tanjunLocalizer.localize(
            locale = commandInfo.locale, key = "commands.math.plotfunction.modals.title"
        ),
    ):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    locale = commandInfo.locale, key = "commands.math.plotfunction.modals.title"
                )
            )
            self.view = view  # Store the view in the modal

        # Text input for the function expression
        function_expression = discord.ui.TextInput(
            label=tanjunLocalizer.localize(
            locale = commandInfo.locale, key = "commands.math.plotfunction.modals.function_expression"
        ),
            placeholder=tanjunLocalizer.localize(
            locale = commandInfo.locale, key = "commands.math.plotfunction.modals.function_expression_placeholder"
        ),
            style=discord.TextStyle.short,
            required=True,
        )

        # Optional: Text input for naming the function
        function_name = discord.ui.TextInput(
            label=tanjunLocalizer.localize(
            locale = commandInfo.locale, key = "commands.math.plotfunction.modals.function_name"
        ),
            placeholder=tanjunLocalizer.localize(
            locale = commandInfo.locale, key = "commands.math.plotfunction.modals.function_name_placeholder"
        ),
            style=discord.TextStyle.short,
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            func_expr = self.function_expression.value
            func_name = self.function_name.value

            # Now self.view is available and can be used to access the plotter
            await self.view.plotter.add_function(func_expr, func_name)

            # Update the plot with the new function
            await self.view.update_plot(interaction)

    class PlotterView(discord.ui.View):
        def __init__(self, plotter: FunctionPlotter):
            super().__init__(timeout=300)  # Adjust timeout as needed
            self.plotter = plotter
            self.message = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.plotter.author_id

        async def on_error(
            self,
            interaction: discord.Interaction,
            error: Exception,
            item: discord.ui.Item,
        ):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    locale = self.plotter.commandInfo.locale,
                    key = "commands.math.plotfunction.error.title"
                ),
                description=tanjunLocalizer.localize(
                    locale = self.plotter.commandInfo.locale,
                    key = "commands.math.plotfunction.error.description",
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        # Zoom and move controls
        async def handle_zoom(self, interaction: discord.Interaction, factor: float):
            self.plotter.x_min *= factor
            self.plotter.x_max *= factor
            self.plotter.y_min *= factor
            self.plotter.y_max *= factor
            await self.update_plot(interaction)

        @discord.ui.button(
            emoji="<:zoom_in:1254736553696034857>",
            style=discord.ButtonStyle.primary,
            custom_id="zoom_in",
            row=0,
        )
        async def zoom_in(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await self.handle_zoom(interaction, 1 / 1.5)

        @discord.ui.button(
            emoji="<:up:1254736547065102357>",
            style=discord.ButtonStyle.primary,
            custom_id="move_up",
            row=0,
        )
        async def move_up(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            shift = (self.plotter.y_max - self.plotter.y_min) * 0.1
            self.plotter.y_min += shift
            self.plotter.y_max += shift
            await self.update_plot(interaction)

        @discord.ui.button(
            emoji="<:zoom_out:1254736552337346581>",
            style=discord.ButtonStyle.primary,
            custom_id="zoom_out",
            row=0,
        )
        async def zoom_out(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await self.handle_zoom(interaction, 1.5)

        @discord.ui.button(
            style=discord.ButtonStyle.secondary,
            label="⠀",
            custom_id="empty",
            row=0,
            disabled=True,
        )
        async def add_function(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_message(
                "this should not be clickable??", ephemeral=True
            )

        @discord.ui.button(
            emoji="<:math_add:1254372629456883793>",
            style=discord.ButtonStyle.success,
            custom_id="add_function",
            row=0,
        )
        async def add_function(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(AddFunctionModal(self))

        @discord.ui.button(
            emoji="<:left:1254736550865141871>",
            style=discord.ButtonStyle.primary,
            custom_id="move_left",
            row=1,
        )
        async def move_left(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            shift = (self.plotter.x_max - self.plotter.x_min) * 0.1
            self.plotter.x_min -= shift
            self.plotter.x_max -= shift
            await self.update_plot(interaction)

        @discord.ui.button(
            emoji="<:down:1254736545454362645>",
            style=discord.ButtonStyle.primary,
            custom_id="move_down",
            row=1,
        )
        async def move_down(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            shift = (self.plotter.y_max - self.plotter.y_min) * 0.1
            self.plotter.y_min -= shift
            self.plotter.y_max -= shift
            await self.update_plot(interaction)

        @discord.ui.button(
            emoji="<:right:1254736548965126165>",
            style=discord.ButtonStyle.primary,
            custom_id="move_right",
            row=1,
        )
        async def move_right(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            shift = (self.plotter.x_max - self.plotter.x_min) * 0.1
            self.plotter.x_min += shift
            self.plotter.x_max += shift
            await self.update_plot(interaction)

        @discord.ui.button(
            label="∫", style=discord.ButtonStyle.secondary, custom_id="integrate", row=1
        )
        async def integrate(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            view = discord.ui.View()
            view.add_item(IntegrateSelect(self.plotter, self))
            await interaction.response.edit_message(
                view=view, content=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.integrate.placeholder")
            )

        @discord.ui.button(
            label="d/dx", style=discord.ButtonStyle.secondary, custom_id="derive", row=1
        )
        async def derive(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            view = discord.ui.View()
            view.add_item(derativeSelect(self.plotter, self))
            await interaction.response.edit_message(
                view=view, content=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.derive.placeholder")
            )

        @discord.ui.button(
            emoji="<:edit:1254736542283464808>",
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.buttons.rename_plot"),
            style=discord.ButtonStyle.secondary,
            custom_id="rename_plot",
            row=2,
        )
        async def rename_plot(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ChangeTitleModal(self))

        @discord.ui.button(
            emoji="<:edit:1254736542283464808>",
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.buttons.change_x_label"),
            style=discord.ButtonStyle.secondary,
            custom_id="change_x_label",
            row=2,
        )
        async def change_x_label(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ChangeXLabelModal(self))

        @discord.ui.button(
            emoji="<:edit:1254736542283464808>",
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.buttons.change_y_label"),
            style=discord.ButtonStyle.secondary,
            custom_id="change_y_label",
            row=2,
        )
        async def change_y_label(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ChangeYLabelModal(self))

        @discord.ui.button(
            emoji="<:edit:1254736542283464808>",
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.buttons.change_style"),
            style=discord.ButtonStyle.secondary,
            custom_id="change_style",
            row=2,
        )
        async def change_style(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            view = discord.ui.View()
            view.add_item(StyleSelect(self.plotter, self))
            await interaction.response.edit_message(
                view=view, content=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.style.placeholder")
            )

        @discord.ui.button(
            emoji="<:edit:1254736542283464808>",
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.buttons.rename_function"),
            style=discord.ButtonStyle.secondary,
            custom_id="rename_function",
            row=2,
        )
        async def rename_function(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if not self.plotter.functions:
                await interaction.response.send_message(
                    "There are no functions to rename.", ephemeral=True
                )
                return

            view = discord.ui.View()
            view.add_item(RenameFunctionSelect(self.plotter, self))
            await interaction.response.edit_message(
                view=view, content=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.rename_function.placeholder")
            )

        async def update_plot(self, interaction: discord.Interaction):
            await interaction.response.defer()

            plot_buffer = await self.plotter.generate_plot()
            file = discord.File(plot_buffer, filename="function_plot.png")
            embed = self.plotter.create_embed()

            for child in self.children:
                child.disabled = True
            await interaction.message.edit(
                view=self
            )  # Update the view to disable buttons

            await interaction.edit_original_response(
                embed=embed, attachments=[file], view=self
            )

            for child in self.children:
                child.disabled = False
            await interaction.message.edit(view=self)

        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            if self.message:
                await self.message.edit(view=self)

    class derativeSelect(discord.ui.Select):
        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView):
            self.plotter = plotter
            self.plotterView = plotterView
            self.update_options()

        def update_options(self):
            options = [
                discord.SelectOption(
                    label=f"{name}(x)", value=str(i), description=f"{func_str}"
                )
                for i, (func_str, func, name) in enumerate(self.plotter.functions)
                if utility.get_highest_exponent(func_str) > 1
            ]
            super().__init__(placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.derive.placeholder"), options=options)

        async def callback(self, interaction: discord.Interaction):
            function_index = int(self.values[0])
            func_str, func, name = self.plotter.functions[function_index]

            func_str = func_str.replace("^", "**")

            # Create a sympy symbol for the variable 'x'
            x = Symbol("x")

            # Parse the function string into a sympy expression
            expr = parse_expr(func_str)

            # Calculate the derivative of the expression with respect to 'x'
            derivative_expr = str(diff(expr, x)).replace("**", "^")

            # Add the derivative function to the plotter
            await self.plotter.add_function(derivative_expr, name + "'")

            await self.plotterView.update_plot(interaction)
            self.update_options()

    class IntegrateSelect(discord.ui.Select):
        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView):
            self.plotter = plotter
            self.plotterView = plotterView
            self.update_options()

        def update_options(self):
            options = [
                discord.SelectOption(
                    label=f"{name}(x)", value=str(i), description=f"{func_str}"
                )
                for i, (func_str, func, name) in enumerate(self.plotter.functions)
            ]
            super().__init__(placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.integrate.placeholder"), options=options)

        async def callback(self, interaction: discord.Interaction):
            function_index = int(self.values[0])
            func_str, func, name = self.plotter.functions[function_index]

            try:
                await self.plotter.integrate_function(func_str, name)
                await self.plotterView.update_plot(interaction)
                self.update_options()
            except ValueError as e:
                await interaction.response.send_message(
                    f"Error: {str(e)}", ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"An unexpected error occurred: {str(e)}", ephemeral=True
                )

    class ChangeTitleModal(discord.ui.Modal, title=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_title.title")):
        def __init__(self, view):
            super().__init__()
            self.view = view

        new_title = discord.ui.TextInput(
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_title.new_title"),
            placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_title.new_title_placeholder"),
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            self.view.plotter.plot_title = self.new_title.value
            await self.view.update_plot(interaction)

    class ChangeXLabelModal(discord.ui.Modal, title=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_x_label.title")):
        def __init__(self, view):
            super().__init__()
            self.view = view

        new_label = discord.ui.TextInput(
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_x_label.new_label"),
            placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_x_label.new_label_placeholder"),
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            self.view.plotter.x_label = self.new_label.value
            await self.view.update_plot(interaction)

    class ChangeYLabelModal(discord.ui.Modal, title=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_y_label.title")):
        def __init__(self, view):
            super().__init__()
            self.view = view

        new_label = discord.ui.TextInput(
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_y_label.new_label"),
            placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.change_y_label.new_label_placeholder"),
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            self.view.plotter.y_label = self.new_label.value
            await self.view.update_plot(interaction)

    class StyleSelect(discord.ui.Select):
        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView):
            self.plotter = plotter
            self.plotterView = plotterView

            # Use only available styles
            self.styles = plt.style.available

            options = [
                discord.SelectOption(label=style, value=style)
                for style in self.styles[0:25]
            ]
            super().__init__(placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.style.placeholder"), options=options)

        async def callback(self, interaction: discord.Interaction):
            selected_style = self.values[0]
            self.plotter.style = selected_style

            await self.plotterView.update_plot(interaction)

    class RenameFunctionSelect(discord.ui.Select):
        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView):
            self.plotter = plotter
            self.plotterView = plotterView

            options = [
                discord.SelectOption(
                    label=f"{name}(x)", value=str(i), description=f"{func_str[:100]}"
                )
                for i, (func_str, func, name) in enumerate(self.plotter.functions)
            ]
            super().__init__(placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.select_menus.rename_function.placeholder"), options=options)

        async def callback(self, interaction: discord.Interaction):
            function_index = int(self.values[0])
            await interaction.response.send_modal(
                RenameFunctionModal(self.plotter, self.plotterView, function_index)
            )

    class RenameFunctionModal(discord.ui.Modal, title=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.rename_function.title")):
        def __init__(
            self,
            plotter: FunctionPlotter,
            plotterView: PlotterView,
            function_index: int,
        ):
            super().__init__()
            self.plotter = plotter
            self.plotterView = plotterView
            self.function_index = function_index

        new_name = discord.ui.TextInput(
            label=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.rename_function.new_name"),
            placeholder=tanjunLocalizer.localize(locale = commandInfo.locale, key = "commands.math.plotfunction.modals.rename_function.new_name_placeholder"),
            required=True,
        )

        async def on_submit(self, interaction: discord.Interaction):
            new_name = self.new_name.value
            await self.plotter.rename_function(self.function_index, new_name)
            await self.plotterView.update_plot(interaction)

    # Instantiate the FunctionPlotter
    plotter = FunctionPlotter(commandInfo, commandInfo.user.id)
    await plotter.add_function(func_str, "f")

    if x_min is not None:
        plotter.x_min = x_min
    if x_max is not None:
        plotter.x_max = x_max

    # Generate the initial plot
    plot_buffer = await plotter.generate_plot()
    file = discord.File(plot_buffer, filename="function_plot.png")
    embed = plotter.create_embed()

    # Instantiate PlotterView with the plotter instance
    view = PlotterView(plotter)

    # Send the plot with the interactive view
    message = await commandInfo.reply(embed=embed, file=file, view=view)
    view.message = message  # Store the message in the view for further interactions
