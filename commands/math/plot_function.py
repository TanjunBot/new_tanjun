from locale_keys import locale
import ast
import asyncio
import io
import re
from collections.abc import Callable
from typing import Any
import discord
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from scipy import optimize
from sympy import Symbol, diff, parse_expr
import utility
_ALLOWED_NP_FUNCTIONS = {'sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'pi', 'e', 'inf', 'nan', 'minimum', 'maximum', 'clip', 'floor', 'ceil', 'round', 'sign'}

def _safe_eval_node(node: ast.AST, x_val: np.ndarray | float) -> np.ndarray | float:
    """Evaluate an AST node safely with only x and restricted numpy functions."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)) and (not isinstance(node.value, bool)):
            return node.value
        raise ValueError(f'Non-numeric constant not allowed: {node.value!r}')
    if isinstance(node, ast.Name):
        if node.id == 'x':
            return x_val
        raise ValueError(f'Unknown variable: {node.id}')
    if isinstance(node, ast.BinOp):
        left = _safe_eval_node(node.left, x_val)
        right = _safe_eval_node(node.right, x_val)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        if isinstance(node.op, ast.Mod):
            return left % right
        raise TypeError(f'Unsupported operator: {type(node.op).__name__}')
    if isinstance(node, ast.UnaryOp):
        operand = _safe_eval_node(node.operand, x_val)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise TypeError(f'Unsupported unary operator: {type(node.op).__name__}')
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name) and node.value.id == 'np':
            attr_name = node.attr
            if attr_name in _ALLOWED_NP_FUNCTIONS:
                return getattr(np, attr_name)
        raise TypeError(f'Unsupported attribute access: {ast.dump(node)}')
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == 'np':
                func_name = node.func.attr
                if func_name not in _ALLOWED_NP_FUNCTIONS:
                    raise ValueError(f'np.{func_name}() is not allowed')
                np_func = getattr(np, func_name)
                args = [_safe_eval_node(arg, x_val) for arg in node.args]
                return np_func(*args)
        raise TypeError(f'Unsupported function call: {ast.dump(node.func)}')
    raise TypeError(f'Unsupported expression: {ast.dump(node)}')

def _safe_np_eval(expr: str, x_val: np.ndarray | float) -> np.ndarray | float:
    """Parse and safely evaluate a numpy expression from user input."""
    node = ast.parse(expr, mode='eval').body
    return _safe_eval_node(node, x_val)

async def plot_function_command(command_info: utility.CommandInfo, func_str: str, x_min: float | None=None, x_max: float | None=None) -> None:

    class FunctionPlotter:

        def __init__(self, command_info: utility.CommandInfo, author_id: int) -> None:
            self.command_info = command_info
            self.author_id = author_id
            self.functions: list[tuple[str, Callable, str]] = []
            self.x_min = -10
            self.x_max = 10
            self.y_min = -10
            self.y_max = 10
            self.plot_title = locale.commands.math.plotfunction.default_title(command_info.locale)
            self.x_label = locale.commands.math.plotfunction.default_x_label(command_info.locale)
            self.y_label = locale.commands.math.plotfunction.default_y_label(command_info.locale)
            self.style = 'default'

        async def add_function(self, func_str: str, name: str) -> None:
            func = await self.parse_function(func_str)
            self.functions.append((func_str, func, name))

        async def parse_function(self, func_str: str) -> Callable:
            func_str = func_str.replace('^', '**')
            func_str = re.sub('(\\d+)([a-zA-Z\\(])', '\\1*\\2', func_str)
            func_str = func_str.replace('sin', 'np.sin')
            func_str = func_str.replace('cos', 'np.cos')
            func_str = func_str.replace('tan', 'np.tan')
            func_str = func_str.replace('exp', 'np.exp')
            func_str = func_str.replace('log', 'np.log')
            func_str = func_str.replace('sqrt', 'np.sqrt')
            if all((c.isdigit() or c in '+-*/.() ' for c in func_str)):
                node = ast.parse(func_str, mode='eval').body
                constant = _safe_eval_node(node, 0)
                return lambda x: np.full_like(x, constant) if isinstance(x, np.ndarray) else constant
            return lambda x: _safe_np_eval(func_str, x)

        async def find_zeros(self, func: Callable) -> list[float]:
            x = np.linspace(self.x_min, self.x_max, 1000)
            y = func(x)
            zero_crossings = np.where(np.diff(np.sign(y)))[0]
            zeros = []
            for i in zero_crossings:
                zero = await asyncio.to_thread(optimize.brentq, func, x[i], x[i + 1])
                zeros.append(zero)
            return zeros

        async def find_extrema(self, func: Callable) -> list[tuple[float, float]]:
            x = np.linspace(self.x_min, self.x_max, 1000)
            y = func(x)
            extrema = []
            for i in range(1, len(x) - 1):
                if y[i - 1] < y[i] and y[i] > y[i + 1] or (y[i - 1] > y[i] and y[i] < y[i + 1]):
                    extrema.append((x[i], y[i]))
            return extrema

        async def find_inflection_points(self, func: Callable) -> list[tuple[float, float]]:

            def second_derivative(x) -> None:
                h = 1e-05
                return (func(x + h) - 2 * func(x) + func(x - h)) / h ** 2
            x = np.linspace(self.x_min, self.x_max, 1000)
            y_second = np.array([second_derivative(xi) for xi in x])
            inflection_points = []
            for i in range(1, len(x) - 1):
                if y_second[i - 1] * y_second[i + 1] < 0:
                    inflection_points.append((x[i], func(x[i])))
            return inflection_points

        async def find_intersection_points(self) -> list[tuple[float, float]]:
            if len(self.functions) < 2:
                return []

            def diff_func(x) -> None:
                return self.functions[0][1](x) - self.functions[1][1](x)
            x = np.linspace(self.x_min, self.x_max, 1000)
            y = diff_func(x)
            zero_crossings = np.where(np.diff(np.sign(y)))[0]
            intersections = []
            for i in zero_crossings:
                intersection = await asyncio.to_thread(optimize.brentq, diff_func, x[i], x[i + 1])
                intersections.append((intersection, self.functions[0][1](intersection)))
            return intersections

        async def rename_function(self, function_index: int, new_name: str) -> None:
            func_str, func, old_name = self.functions[function_index]
            self.functions[function_index] = (func_str, func, new_name)

        async def integrate_function(self, func_str: str, name: str) -> None:
            x = sp.Symbol('x')
            func_str = func_str.replace('^', '**')
            expr = sp.parsing.sympy_parser.parse_expr(func_str)
            integral = sp.integrate(expr, x)
            integral_str = str(integral).replace('**', '^')
            await self.add_function(integral_str, f'∫{name}')

        async def generate_plot(self) -> io.BytesIO:
            plt.close('all')
            plt.style.use(self.style)
            x = np.linspace(self.x_min, self.x_max, 10000)
            for func_str, func, name in self.functions:
                y = func(x)
                plt.plot(x, y, label=f'{name}(x) = {func_str}', zorder=187)
            plt.xlabel(self.x_label)
            plt.ylabel(self.y_label)
            plt.title(self.plot_title)
            plt.xlim(self.x_min, self.x_max)
            plt.ylim(self.y_min, self.y_max)
            plt.legend()
            plt.grid(True)
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close('all')
            return buf

        def create_embed(self) -> discord.Embed:
            embed = utility.tanjunEmbed(title=self.plot_title, description=locale.commands.math.plotfunction.description(self.command_info.locale, x_min=round(self.x_min, 2), x_max=round(self.x_max, 2)))
            for _i, (func_str, _func, name) in enumerate(self.functions):
                embed.add_field(name=f'{name}(x)', value=func_str, inline=False)
            embed.set_image(url='attachment://function_plot.png')
            return embed

    class AddFunctionModal(discord.ui.Modal, title=locale.commands.math.plotfunction.modals.add_function.title(command_info.locale)):

        def __init__(self, view) -> None:
            super().__init__(title=locale.commands.math.plotfunction.modals.add_function.title(command_info.locale))
            self.view = view
        function_expression = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.add_function.function_expression(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.add_function.function_expression_placeholder(command_info.locale), style=discord.TextStyle.short, required=True)
        function_name = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.add_function.function_name(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.add_function.function_name_placeholder(command_info.locale), style=discord.TextStyle.short, required=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            func_expr = self.function_expression.value
            func_name = self.function_name.value
            await self.view.plotter.add_function(func_expr, func_name)
            await self.view.update_plot(interaction)

    class PlotterView(discord.ui.View):

        def __init__(self, plotter: FunctionPlotter) -> None:
            super().__init__(timeout=300)
            self.plotter = plotter
            self.message = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.plotter.author_id

        async def handle_zoom(self, interaction: discord.Interaction, factor: float) -> None:
            self.plotter.x_min *= factor
            self.plotter.x_max *= factor
            self.plotter.y_min *= factor
            self.plotter.y_max *= factor
            await self.update_plot(interaction)

        @discord.ui.button(emoji='<:zoom_in:1254736553696034857>', style=discord.ButtonStyle.primary, custom_id='zoom_in', row=0)
        async def zoom_in(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await self.handle_zoom(interaction, 1 / 1.5)

        @discord.ui.button(emoji='<:up:1254736547065102357>', style=discord.ButtonStyle.primary, custom_id='move_up', row=0)
        async def move_up(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            shift = (self.plotter.y_max - self.plotter.y_min) * 0.1
            self.plotter.y_min += shift
            self.plotter.y_max += shift
            await self.update_plot(interaction)

        @discord.ui.button(emoji='<:zoom_out:1254736552337346581>', style=discord.ButtonStyle.primary, custom_id='zoom_out', row=0)
        async def zoom_out(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await self.handle_zoom(interaction, 1.5)

        @discord.ui.button(style=discord.ButtonStyle.secondary, label='⠀', custom_id='empty', row=0, disabled=True)
        async def empty(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_message(locale.commands.math.plotfunction.not_clickable(self.plotter.command_info.locale), ephemeral=True)

        @discord.ui.button(emoji='<:math_add:1254372629456883793>', style=discord.ButtonStyle.success, custom_id='add_function', row=0)
        async def add_function(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(AddFunctionModal(self))

        @discord.ui.button(emoji='<:left:1254736550865141871>', style=discord.ButtonStyle.primary, custom_id='move_left', row=1)
        async def move_left(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            shift = (self.plotter.x_max - self.plotter.x_min) * 0.1
            self.plotter.x_min -= shift
            self.plotter.x_max -= shift
            await self.update_plot(interaction)

        @discord.ui.button(emoji='<:down:1254736545454362645>', style=discord.ButtonStyle.primary, custom_id='move_down', row=1)
        async def move_down(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            shift = (self.plotter.y_max - self.plotter.y_min) * 0.1
            self.plotter.y_min -= shift
            self.plotter.y_max -= shift
            await self.update_plot(interaction)

        @discord.ui.button(emoji='<:right:1254736548965126165>', style=discord.ButtonStyle.primary, custom_id='move_right', row=1)
        async def move_right(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            shift = (self.plotter.x_max - self.plotter.x_min) * 0.1
            self.plotter.x_min += shift
            self.plotter.x_max += shift
            await self.update_plot(interaction)

        @discord.ui.button(label='∫', style=discord.ButtonStyle.secondary, custom_id='integrate', row=1)
        async def integrate(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            view = discord.ui.View()
            view.add_item(IntegrateSelect(self.plotter, self))
            await interaction.response.edit_message(view=view, content=locale.commands.math.plotfunction.select_menus.integrate.placeholder(command_info.locale))

        @discord.ui.button(label='d/dx', style=discord.ButtonStyle.secondary, custom_id='derive', row=1)
        async def derive(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            view = discord.ui.View()
            view.add_item(DerivativeSelect(self.plotter, self))
            await interaction.response.edit_message(view=view, content=locale.commands.math.plotfunction.select_menus.derive.placeholder(command_info.locale))

        @discord.ui.button(emoji='<:edit:1254736542283464808>', label=locale.commands.math.plotfunction.buttons.rename_plot(command_info.locale), style=discord.ButtonStyle.secondary, custom_id='rename_plot', row=2)
        async def rename_plot(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ChangeTitleModal(self))

        @discord.ui.button(emoji='<:edit:1254736542283464808>', label=locale.commands.math.plotfunction.buttons.change_x_label(command_info.locale), style=discord.ButtonStyle.secondary, custom_id='change_x_label', row=2)
        async def change_x_label(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ChangeXLabelModal(self))

        @discord.ui.button(emoji='<:edit:1254736542283464808>', label=locale.commands.math.plotfunction.buttons.change_y_label(command_info.locale), style=discord.ButtonStyle.secondary, custom_id='change_y_label', row=2)
        async def change_y_label(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ChangeYLabelModal(self))

        @discord.ui.button(emoji='<:edit:1254736542283464808>', label=locale.commands.math.plotfunction.buttons.change_style(command_info.locale), style=discord.ButtonStyle.secondary, custom_id='change_style', row=2)
        async def change_style(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            view = discord.ui.View()
            view.add_item(StyleSelect(self.plotter, self))
            await interaction.response.edit_message(view=view, content=locale.commands.math.plotfunction.select_menus.style.placeholder(command_info.locale))

        @discord.ui.button(emoji='<:edit:1254736542283464808>', label=locale.commands.math.plotfunction.buttons.rename_function(command_info.locale), style=discord.ButtonStyle.secondary, custom_id='rename_function', row=2)
        async def rename_function(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if not self.plotter.functions:
                await interaction.response.send_message(locale.commands.math.plotfunction.no_functions_to_rename(self.plotter.command_info.locale), ephemeral=True)
                return
            view = discord.ui.View()
            view.add_item(RenameFunctionSelect(self.plotter, self))
            await interaction.response.edit_message(view=view, content=locale.commands.math.plotfunction.select_menus.rename_function.placeholder(command_info.locale))

        async def update_plot(self, interaction: discord.Interaction) -> None:
            await interaction.response.defer()
            plot_buffer = await self.plotter.generate_plot()
            file = discord.File(plot_buffer, filename='function_plot.png')
            embed = self.plotter.create_embed()
            for child in self.children:
                child.disabled = True
            await interaction.message.edit(view=self)
            await interaction.edit_original_response(embed=embed, attachments=[file], view=self)
            for child in self.children:
                child.disabled = False
            await interaction.message.edit(view=self)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True
            if self.message:
                await self.message.edit(view=self)

    class DerivativeSelect(discord.ui.Select):

        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView) -> None:
            self.plotter = plotter
            self.plotterView = plotterView
            self.update_options()

        def update_options(self) -> None:
            options = [discord.SelectOption(label=f'{name}(x)', value=str(i), description=f'{func_str}') for i, (func_str, func, name) in enumerate(self.plotter.functions)]
            super().__init__(placeholder=locale.commands.math.plotfunction.select_menus.derive.placeholder(command_info.locale), options=options)

        async def callback(self, interaction: discord.Interaction) -> None:
            function_index = int(self.values[0])
            func_str, func, name = self.plotter.functions[function_index]
            func_str = func_str.replace('^', '**')
            x = Symbol('x')
            expr = parse_expr(func_str)
            derivative_expr = str(diff(expr, x)).replace('**', '^')
            await self.plotter.add_function(derivative_expr, name + "'")
            await self.plotterView.update_plot(interaction)
            self.update_options()

    class IntegrateSelect(discord.ui.Select):

        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView) -> None:
            self.plotter = plotter
            self.plotterView = plotterView
            self.update_options()

        def update_options(self) -> None:
            options = [discord.SelectOption(label=f'{name}(x)', value=str(i), description=f'{func_str}') for i, (func_str, func, name) in enumerate(self.plotter.functions)]
            super().__init__(placeholder=locale.commands.math.plotfunction.select_menus.integrate.placeholder(command_info.locale), options=options)

        async def callback(self, interaction: discord.Interaction) -> None:
            function_index = int(self.values[0])
            func_str, func, name = self.plotter.functions[function_index]
            try:
                await self.plotter.integrate_function(func_str, name)
                await self.plotterView.update_plot(interaction)
                self.update_options()
            except ValueError as e:
                await interaction.response.send_message(locale.commands.math.plotfunction.error(self.plotterView.plotter.command_info.locale, error=str(e)), ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(locale.commands.math.plotfunction.unexpected_error(self.plotterView.plotter.command_info.locale, error=str(e)), ephemeral=True)

    class ChangeTitleModal(discord.ui.Modal, title=locale.commands.math.plotfunction.modals.change_title.title(command_info.locale)):

        def __init__(self, view) -> None:
            super().__init__()
            self.view = view
        new_title = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.change_title.new_title(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.change_title.new_title_placeholder(command_info.locale), required=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.plotter.plot_title = self.new_title.value
            await self.view.update_plot(interaction)

    class ChangeXLabelModal(discord.ui.Modal, title=locale.commands.math.plotfunction.modals.change_x_label.title(command_info.locale)):

        def __init__(self, view) -> None:
            super().__init__()
            self.view = view
        new_label = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.change_x_label.new_label(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.change_x_label.new_label_placeholder(command_info.locale), required=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.plotter.x_label = self.new_label.value
            await self.view.update_plot(interaction)

    class ChangeYLabelModal(discord.ui.Modal, title=locale.commands.math.plotfunction.modals.change_y_label.title(command_info.locale)):

        def __init__(self, view) -> None:
            super().__init__()
            self.view = view
        new_label = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.change_y_label.new_label(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.change_y_label.new_label_placeholder(command_info.locale), required=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.plotter.y_label = self.new_label.value
            await self.view.update_plot(interaction)

    class StyleSelect(discord.ui.Select):

        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView) -> None:
            self.plotter = plotter
            self.plotterView = plotterView
            self.styles = plt.style.available
            options = [discord.SelectOption(label=style, value=style) for style in self.styles[0:25]]
            super().__init__(placeholder=locale.commands.math.plotfunction.select_menus.style.placeholder(command_info.locale), options=options)

        async def callback(self, interaction: discord.Interaction) -> None:
            selected_style = self.values[0]
            self.plotter.style = selected_style
            await self.plotterView.update_plot(interaction)

    class RenameFunctionSelect(discord.ui.Select):

        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView) -> None:
            self.plotter = plotter
            self.plotterView = plotterView
            options = [discord.SelectOption(label=f'{name}(x)', value=str(i), description=f'{func_str[:100]}') for i, (func_str, func, name) in enumerate(self.plotter.functions)]
            super().__init__(placeholder=locale.commands.math.plotfunction.select_menus.rename_function.placeholder(command_info.locale), options=options)

        async def callback(self, interaction: discord.Interaction) -> None:
            function_index = int(self.values[0])
            await interaction.response.send_modal(RenameFunctionModal(self.plotter, self.plotterView, function_index))

    class RenameFunctionModal(discord.ui.Modal, title=locale.commands.math.plotfunction.modals.rename_function.title(command_info.locale)):

        def __init__(self, plotter: FunctionPlotter, plotterView: PlotterView, function_index: int) -> None:
            super().__init__()
            self.plotter = plotter
            self.plotterView = plotterView
            self.function_index = function_index
        new_name = discord.ui.TextInput(label=locale.commands.math.plotfunction.modals.rename_function.new_name(command_info.locale), placeholder=locale.commands.math.plotfunction.modals.rename_function.new_name_placeholder(command_info.locale), required=True)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            new_name = self.new_name.value
            await self.plotter.rename_function(self.function_index, new_name)
            await self.plotterView.update_plot(interaction)
    plotter = FunctionPlotter(command_info, command_info.user.id)
    await plotter.add_function(func_str, 'f')
    if x_min is not None:
        plotter.x_min = x_min
    if x_max is not None:
        plotter.x_max = x_max
    plot_buffer = await plotter.generate_plot()
    file = discord.File(plot_buffer, filename='function_plot.png')
    embed = plotter.create_embed()
    view = PlotterView(plotter)
    message = await command_info.reply(embed=embed, file=file, view=view)
    view.message = message