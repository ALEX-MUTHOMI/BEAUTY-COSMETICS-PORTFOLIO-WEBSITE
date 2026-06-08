import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_homepage_carousel_endpoint_outputs_only_optimized_public_variants(settings):
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 1
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        title="Featured",
        status=GalleryImage.Status.PUBLISHED,
        is_featured=True,
        show_on_homepage=True,
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.HERO,
        storage_key="gallery/variants/hero.webp",
        width=1600,
        height=1200,
        format="webp",
        size_bytes=1000,
        sha256_hash="b" * 64,
        is_public=True,
    )

    payload = Client().get("/api/gallery/public/homepage/", secure=True).json()

    assert len(payload["images"]) == 1
    assert payload["images"][0]["variants"]["hero"]["url"].endswith(".webp")
    assert "original" not in str(payload).lower()
    assert "quarantine" not in str(payload).lower()
