import discord
from discord.ext import commands
from discord import app_commands
import utility
from typing import List

from commands.image.blur_image import blur_image
from commands.image.contour import contour_image
from commands.image.detail import detail_image
from commands.image.edge_enhance import edge_enhance
from commands.image.emboss import emboss
from commands.image.find_edges import find_edges
from commands.image.sharpen import sharpen
from commands.image.smooth import smooth
from commands.image.resize import resize
from commands.image.rescale import rescale
from commands.image.mirror import mirror
from commands.image.compress import compress

class ImageCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("image_blur_name"),
        description=app_commands.locale_str("image_blur_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_blur_params_image_description"),
        type=app_commands.locale_str("image_blur_params_type_description"),
        radius=app_commands.locale_str("image_blur_params_radius_description")
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name=app_commands.locale_str("image_blur_params_type_gaussian"), value="gussian"),
            app_commands.Choice(name=app_commands.locale_str("image_blur_params_type_boxblurr"), value="boxblurr")
        ]
    )
    async def blurimage(self, interaction: discord.Interaction, image: discord.Attachment, type: str = "gaussian", radius: int = 3):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await blur_image(
            commandInfo=commandInfo,
            image=image,
            type=type,
            radius=radius
        )

    @app_commands.command(
        name=app_commands.locale_str("image_contour_name"),
        description=app_commands.locale_str("image_contour_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_contour_params_image_description")
    )
    async def contourimage(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await contour_image(
            commandInfo=commandInfo,
            image=image
        )

    @app_commands.command(
        name=app_commands.locale_str("image_detail_name"),
        description=app_commands.locale_str("image_detail_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_detail_params_image_description")
    )
    async def detailimage(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await detail_image(
            commandInfo=commandInfo,
            image=image
        )

    @app_commands.command(
        name=app_commands.locale_str("image_edgeenhance_name"),
        description=app_commands.locale_str("image_edgeenhance_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_edgeenhance_params_image_description")
    )
    async def edgeenhance(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await edge_enhance(
            commandInfo=commandInfo,
            image=image
        )
    
    @app_commands.command(
        name=app_commands.locale_str("image_emboss_name"),
        description=app_commands.locale_str("image_emboss_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_emboss_params_image_description")
    )
    async def emboss(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await emboss(
            commandInfo=commandInfo,
            image=image
        )

    @app_commands.command(
        name=app_commands.locale_str("image_findedges_name"),
        description=app_commands.locale_str("image_findedges_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_findedges_params_image_description")
    )
    async def findedges(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await find_edges(
            commandInfo=commandInfo,
            image=image
        )
    
    @app_commands.command(
        name=app_commands.locale_str("image_sharpen_name"),
        description=app_commands.locale_str("image_sharpen_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_sharpen_params_image_description")
    )
    async def sharpen(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await sharpen(
            commandInfo=commandInfo,
            image=image
        )

    @app_commands.command(
        name=app_commands.locale_str("image_smooth_name"),
        description=app_commands.locale_str("image_smooth_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_smooth_params_image_description")
    )
    async def smooth(self, interaction: discord.Interaction, image: discord.Attachment):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await smooth(
            commandInfo=commandInfo,
            image=image
        )

    @app_commands.command(
        name=app_commands.locale_str("image_resize_name"),
        description=app_commands.locale_str("image_resize_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_resize_params_image_description"),
        width=app_commands.locale_str("image_resize_params_width_description"),
        height=app_commands.locale_str("image_resize_params_height_description")
    )
    async def resize(self, interaction: discord.Interaction, image: discord.Attachment, width: app_commands.Range[int, 5, 15000], height: app_commands.Range[int, 5, 15000]):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await resize(
            commandInfo=commandInfo,
            image=image,
            width=width,
            height=height
        )

    @app_commands.command(
        name=app_commands.locale_str("image_rescale_name"),
        description=app_commands.locale_str("image_rescale_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_rescale_params_image_description"),
        factor=app_commands.locale_str("image_rescale_params_factor_description")
    )
    async def rescale(self, interaction: discord.Interaction, image: discord.Attachment, factor: app_commands.Range[float, 0.1, 10.0]):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await rescale(
            commandInfo=commandInfo,
            image=image,
            factor=factor
        )

    @app_commands.command(
        name=app_commands.locale_str("image_mirror_name"),
        description=app_commands.locale_str("image_mirror_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_mirror_params_image_description"),
        direction=app_commands.locale_str("image_mirror_params_direction_description")
    )
    @app_commands.choices(
        direction=[
            app_commands.Choice(name=app_commands.locale_str("image_mirror_params_direction_horizontal"), value="x"),
            app_commands.Choice(name=app_commands.locale_str("image_mirror_params_direction_vertical"), value="y")
        ]
    )
    async def mirror(self, interaction: discord.Interaction, image: discord.Attachment, direction: str = "x"):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await mirror(
            commandInfo=commandInfo,
            image=image,
            axis=direction
        )

    @app_commands.command(
        name=app_commands.locale_str("image_compress_name"),
        description=app_commands.locale_str("image_compress_description")
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_compress_params_image_description"),
        quality=app_commands.locale_str("image_compress_params_quality_description")
    )
    async def compress(self, interaction: discord.Interaction, image: discord.Attachment, quality: app_commands.Range[int, 1, 100]):
        await interaction.response.defer()
        commandInfo = utility.commandInfo(
            user=interaction.user,
            channel=interaction.channel,
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await compress(
            commandInfo=commandInfo,
            image=image,
            quality=quality
        )

class ImageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        imgcmds = ImageCommands(name=app_commands.locale_str("image_name"), description=app_commands.locale_str("image_description"))
        self.bot.tree.add_command(imgcmds)

async def setup(bot):
    await bot.add_cog(ImageCog(bot))
