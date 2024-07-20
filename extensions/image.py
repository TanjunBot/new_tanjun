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
        name="blur",
        description="Blur a image"
    )
    @app_commands.describe(
        image="The image you want blur",
        type="The type of blur",
        radius="The radius of the blur"
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="gussian", value="gussian"),
            app_commands.Choice(name="box blurr", value="boxblurr")
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
        name="contour",
        description="Contour a image"
    )
    @app_commands.describe(
        image="The image you want contour"
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
        name="detail",
        description="Detail a image"
    )
    @app_commands.describe(
        image="The image you want detail"
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
        name="edgeenhance",
        description="Edge enhance a image"
    )
    @app_commands.describe(
        image="The image you want edge enhance"
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
        name="emboss",
        description="Emboss a image"
    )
    @app_commands.describe(
        image="The image you want emboss"
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
        name="findedges",
        description="Find edges in a image"
    )
    @app_commands.describe(
        image="The image you want find edges"
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
        name="sharpen",
        description="Sharpen a image"
    )
    @app_commands.describe(
        image="The image you want sharpen"
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
        name="smooth",
        description="Smooth a image"
    )
    @app_commands.describe(
        image="The image you want smooth"
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
        name="resize",
        description="Resize a image"
    )
    @app_commands.describe(
        image="The image you want resize",
        width="The width of the image",
        height="The height of the image"
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
        name="rescale",
        description="Rescale a image"
    )
    @app_commands.describe(
        image="The image you want rescale",
        factor="The factor you want rescale"
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
        name="mirror",
        description="Mirror a image"
    )
    @app_commands.describe(
        image="The image you want mirror",
        direction="The direction you want mirror"
    )
    @app_commands.choices(
        direction=[
            app_commands.Choice(name="horizontal", value="x"),
            app_commands.Choice(name="vertical", value="y")
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
        name="compress",
        description="Compress a image"
    )
    @app_commands.describe(
        image="The image you want compress",
        quality="The quality of the image"
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
        aicmds = ImageCommands(name="image", description="Image commands")
        self.bot.tree.add_command(aicmds)

async def setup(bot):
    await bot.add_cog(ImageCog(bot))
