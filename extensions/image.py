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
    return utility.CommandInfo(
        user=interaction.user,
        channel=cast(discord.abc.GuildChannel, interaction.channel),
        guild=interaction.guild,
        command=interaction.command,
        locale=interaction.locale,  # type: ignore[arg-type]
        message=interaction.message,
        permissions=interaction.permissions,
        reply=interaction.followup.send,
        client=interaction.client,
    )


class ImageCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("image_blur_name"),
        description=app_commands.locale_str("image_blur_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_blur_params_image_description"),
        type=app_commands.locale_str("image_blur_params_type_description"),
        radius=app_commands.locale_str("image_blur_params_radius_description"),
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(
                name=app_commands.locale_str("image_blur_params_type_gaussian"),
                value="gussian",
            ),
            app_commands.Choice(
                name=app_commands.locale_str("image_blur_params_type_boxblurr"),
                value="boxblurr",
            ),
        ]
    )
    async def blurimage(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        type: str = "gaussian",
        radius: app_commands.Range[int, 1, 10] = 3,
    ) -> None:
        await interaction.response.defer()
        filter_name = "gaussian_blur" if type == "gaussian" else "box_blur"
        await apply_filter(
            _make_command_info(interaction),
            image,
            filter_name,
            error_locale_key="image.blur",
            success_locale_key="image.blur",
            radius=radius,
        )

    @app_commands.command(
        name=app_commands.locale_str("image_contour_name"),
        description=app_commands.locale_str("image_contour_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_contour_params_image_description"))
    async def contourimage(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "contour")

    @app_commands.command(
        name=app_commands.locale_str("image_detail_name"),
        description=app_commands.locale_str("image_detail_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_detail_params_image_description"))
    async def detailimage(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "detail")

    @app_commands.command(
        name=app_commands.locale_str("image_edgeenhance_name"),
        description=app_commands.locale_str("image_edgeenhance_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_edgeenhance_params_image_description"))
    async def edgeenhance(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "edge_enhance", success_locale_key="image.edgeenhance")

    @app_commands.command(
        name=app_commands.locale_str("image_emboss_name"),
        description=app_commands.locale_str("image_emboss_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_emboss_params_image_description"))
    async def emboss(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "emboss")

    @app_commands.command(
        name=app_commands.locale_str("image_findedges_name"),
        description=app_commands.locale_str("image_findedges_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_findedges_params_image_description"))
    async def findedges(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "find_edges", success_locale_key="image.findedges")

    @app_commands.command(
        name=app_commands.locale_str("image_sharpen_name"),
        description=app_commands.locale_str("image_sharpen_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_sharpen_params_image_description"))
    async def sharpen(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "sharpen")

    @app_commands.command(
        name=app_commands.locale_str("image_smooth_name"),
        description=app_commands.locale_str("image_smooth_description"),
    )
    @app_commands.describe(image=app_commands.locale_str("image_smooth_params_image_description"))
    async def smooth(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await apply_filter(_make_command_info(interaction), image, "smooth")

    @app_commands.command(
        name=app_commands.locale_str("image_resize_name"),
        description=app_commands.locale_str("image_resize_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_resize_params_image_description"),
        width=app_commands.locale_str("image_resize_params_width_description"),
        height=app_commands.locale_str("image_resize_params_height_description"),
    )
    async def resize(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        width: app_commands.Range[int, 5, 15000],
        height: app_commands.Range[int, 5, 15000],
    ) -> None:
        await interaction.response.defer()
        await resize(commandInfo=_make_command_info(interaction), image=image, width=width, height=height)

    @app_commands.command(
        name=app_commands.locale_str("image_rescale_name"),
        description=app_commands.locale_str("image_rescale_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_rescale_params_image_description"),
        factor=app_commands.locale_str("image_rescale_params_factor_description"),
    )
    async def rescale(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        factor: app_commands.Range[float, 0.1, 10.0],
    ) -> None:
        await interaction.response.defer()
        await rescale(commandInfo=_make_command_info(interaction), image=image, factor=factor)

    @app_commands.command(
        name=app_commands.locale_str("image_mirror_name"),
        description=app_commands.locale_str("image_mirror_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_mirror_params_image_description"),
        direction=app_commands.locale_str("image_mirror_params_direction_description"),
    )
    @app_commands.choices(
        direction=[
            app_commands.Choice(
                name=app_commands.locale_str("image_mirror_params_direction_horizontal"),
                value="x",
            ),
            app_commands.Choice(
                name=app_commands.locale_str("image_mirror_params_direction_vertical"),
                value="y",
            ),
        ]
    )
    async def mirror(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        direction: str = "x",
    ) -> None:
        await interaction.response.defer()
        await mirror(commandInfo=_make_command_info(interaction), image=image, axis=direction)

    @app_commands.command(
        name=app_commands.locale_str("image_compress_name"),
        description=app_commands.locale_str("image_compress_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_compress_params_image_description"),
        quality=app_commands.locale_str("image_compress_params_quality_description"),
    )
    async def compress(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        quality: app_commands.Range[int, 1, 100],
    ) -> None:
        await interaction.response.defer()
        await compress(commandInfo=_make_command_info(interaction), image=image, quality=quality)

    @app_commands.command(
        name=app_commands.locale_str("image_background_name"),
        description=app_commands.locale_str("image_background_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("image_background_params_image_description"),
    )
    async def background(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        await background(commandInfo=_make_command_info(interaction), image=image)


class ImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        imgcmds = ImageCommands(
            name=app_commands.locale_str("image_name"),
            description=app_commands.locale_str("image_description"),
        )
        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(imgcmds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ImageCog(bot))
