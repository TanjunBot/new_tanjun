from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.image._filter import apply_filter
from commands.image.background import background
from commands.image.compress import compress
from commands.image.mirror import mirror
from commands.image.rescale import rescale
from commands.image.resize import resize

def _make_command_info(interaction: discord.Interaction) -> utility.CommandInfo:
    return utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)

class ImageCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.image.blur.name.discord_key, description=locale.image.blur.description.discord_key)
    @app_commands.describe(image=locale.image.blur.params.image.description.discord_key, type=locale.image.blur.params.type.description.discord_key, radius=locale.image.blur.params.radius.description.discord_key)
    @app_commands.choices(type=[app_commands.Choice(name=locale.image.blur.params.type.gaussian.discord_key, value='gaussian'), app_commands.Choice(name=locale.image.blur.params.type.boxblurr.discord_key, value='box_blur')])
    async def blurimage(self, interaction: discord.Interaction, image: discord.Attachment, type: str='gaussian', radius: app_commands.Range[int, 1, 10]=3) -> None:
        await interaction.response.defer()
        filter_name = 'gaussian_blur' if type == 'gaussian' else 'box_blur'
        await apply_filter(_make_command_info(interaction), image, filter_name, error_locale_key='image.blur', success_locale_key='image.blur', radius=radius)

    @app_commands.command(name=locale.image.contour.name.discord_key, description=locale.image.contour.description.discord_key)
    @app_commands.describe(image=locale.image.contour.params.image.description.discord_key)
    async def contourimage(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'contour')

    @app_commands.command(name=locale.image.detail.name.discord_key, description=locale.image.detail.description.discord_key)
    @app_commands.describe(image=locale.image.detail.params.image.description.discord_key)
    async def detailimage(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'detail')

    @app_commands.command(name=locale.image.edgeenhance.name.discord_key, description=locale.image.edgeenhance.description.discord_key)
    @app_commands.describe(image=locale.image.edgeenhance.params.image.description.discord_key)
    async def edgeenhance(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'edge_enhance', success_locale_key='image.edgeenhance')

    @app_commands.command(name=locale.image.emboss.name.discord_key, description=locale.image.emboss.description.discord_key)
    @app_commands.describe(image=locale.image.emboss.params.image.description.discord_key)
    async def emboss(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'emboss')

    @app_commands.command(name=locale.image.findedges.name.discord_key, description=locale.image.findedges.description.discord_key)
    @app_commands.describe(image=locale.image.findedges.params.image.description.discord_key)
    async def findedges(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'find_edges', success_locale_key='image.findedges')

    @app_commands.command(name=locale.image.sharpen.name.discord_key, description=locale.image.sharpen.description.discord_key)
    @app_commands.describe(image=locale.image.sharpen.params.image.description.discord_key)
    async def sharpen(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'sharpen')

    @app_commands.command(name=locale.image.smooth.name.discord_key, description=locale.image.smooth.description.discord_key)
    @app_commands.describe(image=locale.image.smooth.params.image.description.discord_key)
    async def smooth(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, 'smooth')

    @app_commands.command(name=locale.image.resize.name.discord_key, description=locale.image.resize.description.discord_key)
    @app_commands.describe(image=locale.image.resize.params.image.description.discord_key, width=locale.image.resize.params.width.description.discord_key, height=locale.image.resize.params.height.description.discord_key)
    async def resize(self, interaction: discord.Interaction, image: discord.Attachment, width: app_commands.Range[int, 5, 15000], height: app_commands.Range[int, 5, 15000]) -> None:
        await interaction.response.defer()
        await resize(command_info=_make_command_info(interaction), image=image, width=width, height=height)

    @app_commands.command(name=locale.image.rescale.name.discord_key, description=locale.image.rescale.description.discord_key)
    @app_commands.describe(image=locale.image.rescale.params.image.description.discord_key, factor=locale.image.rescale.params.factor.description.discord_key)
    async def rescale(self, interaction: discord.Interaction, image: discord.Attachment, factor: app_commands.Range[float, 0.1, 10.0]) -> None:
        await interaction.response.defer()
        await rescale(command_info=_make_command_info(interaction), image=image, factor=factor)

    @app_commands.command(name=locale.image.mirror.name.discord_key, description=locale.image.mirror.description.discord_key)
    @app_commands.describe(image=locale.image.mirror.params.image.description.discord_key, direction=locale.image.mirror.params.direction.description.discord_key)
    @app_commands.choices(direction=[app_commands.Choice(name=locale.image.mirror.params.direction.horizontal.discord_key, value='x'), app_commands.Choice(name=locale.image.mirror.params.direction.vertical.discord_key, value='y')])
    async def mirror(self, interaction: discord.Interaction, image: discord.Attachment, direction: str='x') -> None:
        await interaction.response.defer()
        await mirror(command_info=_make_command_info(interaction), image=image, axis=direction)

    @app_commands.command(name=locale.image.compress.name.discord_key, description=locale.image.compress.description.discord_key)
    @app_commands.describe(image=locale.image.compress.params.image.description.discord_key, quality=locale.image.compress.params.quality.description.discord_key)
    async def compress(self, interaction: discord.Interaction, image: discord.Attachment, quality: app_commands.Range[int, 1, 100]) -> None:
        await interaction.response.defer()
        await compress(command_info=_make_command_info(interaction), image=image, quality=quality)

    @app_commands.command(name=locale.image.background.name.discord_key, description=locale.image.background.description.discord_key)
    @app_commands.describe(image=locale.image.background.params.image.description.discord_key)
    async def background(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await background(command_info=_make_command_info(interaction), image=image)

class ImageCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        imgcmds = ImageCommands(name=locale.image.name.discord_key, description=locale.image.description.discord_key)
        if self.bot.tree:
            self.bot.tree.add_command(imgcmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ImageCog(bot))