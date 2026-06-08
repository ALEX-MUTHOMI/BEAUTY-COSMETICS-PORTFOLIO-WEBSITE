import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_sensitive_waxing_category_requires_warning_and_is_never_homepage():
    staff = make_staff()
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    image = GalleryImage.objects.create(
        category=waxing,
        uploaded_by=staff,
        title="Waxing safe copy",
        status=GalleryImage.Status.PUBLISHED,
        show_on_homepage=True,
        is_featured=True,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/variants/waxing.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=1000,
        sha256_hash="e" * 64,
        is_public=True,
    )

    client = Client()
    assert client.get("/api/gallery/public/homepage/", secure=True).json()["images"] == []
    category_payload = client.get("/api/gallery/public/categories/waxing/", secure=True).json()
    assert category_payload["category"]["requires_warning"] is True
    assert category_payload["images"][0]["requires_warning"] is True
