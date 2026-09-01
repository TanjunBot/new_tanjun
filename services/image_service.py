"""ImageService: Consolidated image processing with typed operations."""
from __future__ import annotations
import io
from enum import Enum
from io import BytesIO
from typing import Any
from PIL import Image, UnidentifiedImageError
from PIL import ImageFilter as PILImageFilter
from locale_keys import locale
from locale_keys.nav import at

class ImageFilter(Enum):
    """Available PIL image filters for the ImageService."""
    CONTOUR = 'contour'
    DETAIL = 'detail'
    EDGE_ENHANCE = 'edge_enhance'
    EMBOSS = 'emboss'
    FIND_EDGES = 'find_edges'
    SHARPEN = 'sharpen'
    SMOOTH = 'smooth'
    GAUSSIAN_BLUR = 'gaussian_blur'
    BOX_BLUR = 'box_blur'

    def to_pil(self, radius: int=3) -> PILImageFilter:
        """Convert this filter enum value to a PIL ImageFilter instance."""
        mapping: dict[ImageFilter, Any] = {ImageFilter.CONTOUR: PILImageFilter.CONTOUR, ImageFilter.DETAIL: PILImageFilter.DETAIL, ImageFilter.EDGE_ENHANCE: PILImageFilter.EDGE_ENHANCE, ImageFilter.EMBOSS: PILImageFilter.EMBOSS, ImageFilter.FIND_EDGES: PILImageFilter.FIND_EDGES, ImageFilter.SHARPEN: PILImageFilter.SHARPEN, ImageFilter.SMOOTH: PILImageFilter.SMOOTH, ImageFilter.GAUSSIAN_BLUR: PILImageFilter.GaussianBlur(radius), ImageFilter.BOX_BLUR: PILImageFilter.BoxBlur(radius)}
        return mapping[self]

    @property
    def locale_key(self) -> str:
        """Return the locale key prefix for this filter."""
        return self.value

    def format_success_title(self, loc: str) -> str:
        """Localize the success title for this filter."""
        return at(f'commands.image.{self.locale_key}.success').title(loc)

    def format_success_description(self, loc: str) -> str:
        """Localize the success description for this filter."""
        return at(f'commands.image.{self.locale_key}.success').description(loc)

class ImageOperation:
    """Represents a single image processing operation.

    Parameters
    ----------
    filter_name : ImageFilter | None
        PIL filter to apply (blur, contour, detail, etc.).
    radius : int
        Radius for blur filters. Defaults to 3.
    resize : tuple[int, int] | None
        Target (width, height) for resize operations.
    scale : float | None
        Scale factor for rescale operations.
    mirror_axis : str | None
        Axis for mirror: "x" (horizontal) or "y" (vertical).
    compress_quality : int | None
        JPEG quality (1-100) for compress operations.
    remove_background : bool
        Whether to attempt background removal.
    """

    def __init__(self, filter_name: ImageFilter | None=None, radius: int=3, resize: tuple[int, int] | None=None, scale: float | None=None, mirror_axis: str | None=None, compress_quality: int | None=None, remove_background: bool=False) -> None:
        self.filter_name = filter_name
        self.radius = radius
        self.resize = resize
        self.scale = scale
        self.mirror_axis = mirror_axis
        self.compress_quality = compress_quality
        self.remove_background = remove_background

class ImageService:
    """Service for processing and uploading images.

    Consolidates image filter, resize, rescale, mirror, compress, and
    background-removal logic previously spread across multiple command files.
    """
    ALLOWED_EXTENSIONS = ('.png', '.jpg', '.jpeg')
    MAX_FILE_SIZE = 8 * 1024 * 1024

    @staticmethod
    def validate_attachment(image: object) -> str | None:
        """Validate a discord Attachment.

        Returns an error locale key prefix on failure, or None on success.
        """
        if hasattr(image, 'filename') and (not image.filename.lower().endswith(ImageService.ALLOWED_EXTENSIONS)):
            return 'typenotsupported'
        if hasattr(image, 'size') and image.size > ImageService.MAX_FILE_SIZE:
            return 'filesize'
        return None

    @staticmethod
    async def process(image_data: bytes, operation: ImageOperation) -> bytes:
        """Apply an ImageOperation to raw image bytes and return result bytes."""
        if operation.filter_name is None and operation.resize is None and (operation.scale is None) and (operation.mirror_axis is None) and (operation.compress_quality is None) and (not operation.remove_background):
            return image_data
        try:
            pil_image: Image.Image = Image.open(io.BytesIO(image_data))
        except (UnidentifiedImageError, OSError) as e:
            msg = f'Failed to open image: {e}'
            raise ValueError(msg) from e
        if operation.compress_quality is not None and pil_image.mode in ('RGBA', 'P'):
            pil_image = pil_image.convert('RGB')
        if operation.filter_name is not None:
            pil_image = pil_image.filter(operation.filter_name.to_pil(operation.radius))
        if operation.resize is not None:
            pil_image = pil_image.resize(operation.resize)
        if operation.scale is not None:
            new_size = (int(pil_image.width * operation.scale), int(pil_image.height * operation.scale))
            pil_image = pil_image.resize(new_size)
        if operation.mirror_axis == 'x':
            pil_image = pil_image.transpose(Image.FLIP_LEFT_RIGHT)
        elif operation.mirror_axis == 'y':
            pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
        if operation.compress_quality is not None:
            fmt = 'JPEG'
            save_kwargs: dict[str, Any] = {'format': fmt, 'quality': operation.compress_quality, 'optimize': True}
        else:
            fmt = 'PNG'
            save_kwargs = {'format': fmt}
        buffer = BytesIO()
        try:
            pil_image.save(buffer, **save_kwargs)
        except (OSError, ValueError) as e:
            msg = f'Failed to save image: {e}'
            raise ValueError(msg) from e
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def format_error_embed(loc: str, error_key: str, locale_prefix: str='image') -> object:
        """Build an error embed for image validation failures."""
        from utility import tanjunEmbed
        err = at(f'commands.{locale_prefix}.{error_key}')
        return tanjunEmbed(
            title=err.title(loc),
            description=err.description(loc),
        )
