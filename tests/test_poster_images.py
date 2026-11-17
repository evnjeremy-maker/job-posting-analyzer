import io

import pytest

from job_posting_analyzer.errors import InputError, ResponseError


def image_bytes(kind="PNG", **kwargs):
    from PIL import Image

    output = io.BytesIO()
    Image.new("RGB", (30, 20), "white").save(output, format=kind, **kwargs)
    return output.getvalue()


@pytest.mark.parametrize("kind,mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
def test_normalized_image_retains_dimensions_and_drops_metadata(kind, mime):
    from PIL import Image

    from job_posting_analyzer.images import normalize_image

    exif = Image.Exif()
    exif[270] = "private metadata"
    data, actual = normalize_image(image_bytes(kind, exif=exif), mime)
    image = Image.open(io.BytesIO(data))
    assert image.size == (30, 20)
    assert not image.getexif()
    assert actual == mime


def test_orientation_is_applied():
    from PIL import Image

    from job_posting_analyzer.images import normalize_image

    exif = Image.Exif()
    exif[274] = 6
    data, _ = normalize_image(image_bytes("JPEG", exif=exif), "image/jpeg")
    assert Image.open(io.BytesIO(data)).size == (20, 30)


def test_palette_transparency_is_preserved_without_metadata():
    from PIL import Image

    from job_posting_analyzer.images import normalize_image

    original = Image.new("P", (10, 10))
    original.putpalette([255, 0, 0] * 256)
    output = io.BytesIO()
    original.save(output, format="PNG", transparency=0)
    data, _ = normalize_image(output.getvalue(), "image/png")
    normalized = Image.open(io.BytesIO(data))
    assert normalized.mode == "RGBA"
    assert normalized.getpixel((0, 0)) == (255, 0, 0, 0)
    assert "transparency" not in normalized.info


@pytest.mark.parametrize(
    "data,mime", [(b"broken", "image/png"), (b"", "image/png"), (b"x", "image/gif")]
)
def test_invalid_images_fail(data, mime):
    from job_posting_analyzer.images import normalize_image

    with pytest.raises(InputError):
        normalize_image(data, mime)


def test_mislabeled_truncated_oversized_and_animation_rejected():
    from PIL import Image

    from job_posting_analyzer.images import normalize_image

    values = [
        (image_bytes(), "image/jpeg"),
        (image_bytes()[:-12], "image/png"),
        (b"x" * (8 * 1024 * 1024 + 1), "image/png"),
    ]
    output = io.BytesIO()
    Image.new("RGB", (10, 10)).save(
        output, format="PNG", save_all=True, append_images=[Image.new("RGB", (10, 10), "white")]
    )
    values.append((output.getvalue(), "image/png"))
    for data, mime in values:
        with pytest.raises(InputError):
            normalize_image(data, mime)


def test_pixel_and_normalized_limits(monkeypatch):
    from job_posting_analyzer import images

    monkeypatch.setattr(images, "MAX_PIXELS", 599)
    with pytest.raises(InputError):
        images.normalize_image(image_bytes(), "image/png")
    monkeypatch.setattr(images, "MAX_PIXELS", 20_000_000)
    monkeypatch.setattr(images, "MAX_NORMALIZED_BYTES", 1)
    with pytest.raises(InputError):
        images.normalize_image(image_bytes(), "image/png")


def test_png_missing_final_crc_byte_is_rejected():
    from job_posting_analyzer.images import normalize_image

    with pytest.raises(InputError):
        normalize_image(image_bytes()[:-1], "image/png")


@pytest.mark.parametrize(
    "text", ["", "   ", "[illegible]", "[illegible]\n[illegible]", "é" * 32769]
)
def test_unusable_transcription_rejected(text):
    from job_posting_analyzer.transcription import validate_transcription

    with pytest.raises(ResponseError):
        validate_transcription({"text": text, "warnings": []})


def test_valid_transcription_preserves_original_language_and_usage_separately():
    from job_posting_analyzer.transcription import validate_transcription

    result = validate_transcription({"text": "Dicari Python intern. Rp 3.000.000", "warnings": []})
    assert result.text == "Dicari Python intern. Rp 3.000.000"
