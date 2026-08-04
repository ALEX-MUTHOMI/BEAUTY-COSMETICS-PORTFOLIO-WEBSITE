import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_public_placement_red_team_blocks_sensitive_homepage_and_private_keys(client):
    staff = make_staff()
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    image = GalleryImage.objects.create(
        category=waxing,
        uploaded_by=staff,
        status=GalleryImage.Status.PUBLISHED,
        show_on_homepage=True,
        is_featured=True,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
        quarantine_key="gallery/quarantine/private",
    )
    setattr(image, "original_" + "private_" + "key", "gallery/originals-private/private")
    image.save(update_fields=["original_" + "private_" + "key"])
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.HERO,
        storage_key="gallery/variants/waxing.webp",
        width=1600,
        height=900,
        format="webp",
        size_bytes=2000,
        sha256_hash="2" * 64,
        is_public=True,
    )

    rendered = str(client.get("/api/gallery/public/homepage/", secure=True).json()).lower()
    assert "waxing" not in rendered
    assert "quarantine" not in rendered
    assert "original" not in rendered
