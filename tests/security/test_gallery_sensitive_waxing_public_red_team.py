import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_sensitive_waxing_public_endpoint_contains_warning_metadata_not_backend_jargon(client):
    staff = make_staff()
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    image = GalleryImage.objects.create(
        category=waxing,
        uploaded_by=staff,
        status=GalleryImage.Status.PUBLISHED,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/variants/sensitive.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=1000,
        sha256_hash="3" * 64,
        is_public=True,
    )

    payload = client.get("/api/gallery/public/categories/waxing/", secure=True).json()

    assert payload["category"]["requires_warning"] is True
    assert payload["images"][0]["requires_warning"] is True
    assert "storage" not in str(payload).lower()
