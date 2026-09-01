from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

_IMAGE_COMMANDS = (
    "image_background_name",
    "image_blur_name",
    "image_compress_name",
    "image_contour_name",
    "image_detail_name",
    "image_edgeenhance_name",
    "image_emboss_name",
    "image_findedges_name",
    "image_mirror_name",
    "image_rescale_name",
    "image_resize_name",
    "image_sharpen_name",
    "image_smooth_name",
)

OVERRIDES = {
    f"image_name {name}": case(f"image_name {name}")
    for name in _IMAGE_COMMANDS
}
