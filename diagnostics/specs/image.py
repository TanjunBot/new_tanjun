from __future__ import annotations

from diagnostics.specs._helpers import default_image_kwargs, register_kwargs, register_defer_only

_IMAGE_METHODS = (
    "blurimage",
    "contourimage",
    "detailimage",
    "edgeenhance",
    "emboss",
    "findedges",
    "sharpen",
    "smooth",
    "resize",
    "rescale",
    "mirror",
    "compress",
    "background",
)


def register() -> None:
    for method in _IMAGE_METHODS:
        spec_id = f"image.ImageCommands.{method}"
        register_kwargs(spec_id, default_image_kwargs)
        register_defer_only(spec_id)
