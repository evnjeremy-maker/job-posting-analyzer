"""Decode bounded poster uploads and strip metadata before hosted recognition."""

import io
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

from .errors import InputError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_NORMALIZED_BYTES = 12 * 1024 * 1024
FORMATS = {"image/png": "PNG", "image/jpeg": "JPEG"}


def normalize_image(data: bytes, mime_type: str) -> tuple[bytes, str]:
    if mime_type not in FORMATS or not data or len(data) > MAX_IMAGE_BYTES:
        raise InputError("Choose a JPEG or PNG poster no larger than 8 MiB.")
    # Pillow verifies image chunks but can accept a truncated final IEND CRC.
    if mime_type == "image/png" and not data.endswith(b"\x00\x00\x00\x00IEND\xaeB\x60\x82"):
        raise InputError("The PNG poster is truncated or has an invalid ending.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as probe:
                if probe.format != FORMATS[mime_type] or probe.width * probe.height > MAX_PIXELS:
                    raise InputError("Image format is incorrect or exceeds 20 megapixels.")
                if getattr(probe, "n_frames", 1) != 1:
                    raise InputError("Animated images are not supported.")
                probe.verify()
            with Image.open(io.BytesIO(data)) as source:
                source.load()
                oriented = ImageOps.exif_transpose(source)
                has_alpha = "A" in oriented.getbands() or "transparency" in oriented.info
                mode = "RGBA" if mime_type == "image/png" and has_alpha else "RGB"
                converted = oriented.convert(mode)
                clean = Image.frombytes(mode, converted.size, converted.tobytes())
                output = io.BytesIO()
                clean.save(
                    output,
                    format=FORMATS[mime_type],
                    **({"quality": 95} if mime_type == "image/jpeg" else {}),
                )
                normalized = output.getvalue()
        if len(normalized) > MAX_NORMALIZED_BYTES:
            raise InputError("Normalized poster exceeds 12 MiB. Choose a smaller image.")
        return normalized, mime_type
    except InputError:
        raise
    except (
        OSError,
        ValueError,
        SyntaxError,
        UnidentifiedImageError,
        Image.DecompressionBombWarning,
        Image.DecompressionBombError,
    ):
        raise InputError(
            "The poster is corrupt, truncated or not a supported static image."
        ) from None
