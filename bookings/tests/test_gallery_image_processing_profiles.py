from io import BytesIO

from PIL import Image

from bookings.services.gallery_images import classify_source_profile


def test_source_profile_classification_is_deterministic_not_security():
    assert (
        classify_source_profile(file_size=2_000_000, width=4032, height=3024, exif_make="Apple", exif_software="")
        == "phone_standard"
    )
    assert (
        classify_source_profile(file_size=18_000_000, width=7000, height=5000, exif_make="Canon", exif_software="")
        == "high_res_camera"
    )
    assert (
        classify_source_profile(file_size=1_200_000, width=1600, height=1600, exif_make="", exif_software="Lightroom")
        == "edited_export"
    )
    assert (
        classify_source_profile(file_size=90_000, width=1080, height=1080, exif_make="", exif_software="Instagram")
        == "compressed_social"
    )
    assert (
        classify_source_profile(file_size=900_000, width=1200, height=900, exif_make="", exif_software="") == "unknown"
    )


def test_spoofed_exif_cannot_make_non_image_valid():
    with BytesIO(b"Canon\x00not an image") as fake:
        try:
            Image.open(fake).verify()
            valid = True
        except Exception:
            valid = False
    assert valid is False
