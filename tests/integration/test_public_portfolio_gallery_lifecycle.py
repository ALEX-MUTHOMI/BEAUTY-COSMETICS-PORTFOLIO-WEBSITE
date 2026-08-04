import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_public_portfolio_endpoint_serves_only_safe_published_gallery_items():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=GalleryImage.Status.PUBLISHED,
        show_on_homepage=True,
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.THUMBNAIL,
        storage_key="gallery/variants/public.webp",
        width=320,
        height=240,
        format="webp",
        size_bytes=128,
        sha256_hash="d" * 64,
        is_public=True,
    )

    from django.test import Client

    response = Client().get("/api/gallery/public/homepage/", secure=True)
    assert response.status_code == 200
    assert response.json()["images"][0]["variants"]["thumbnail"]["url"].endswith(".webp")
    assert "storage_key" not in str(response.json())
