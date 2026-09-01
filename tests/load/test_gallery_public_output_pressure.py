import copy

import pytest
from django.test import Client, override_settings

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_public_output_pressure_stays_capped(settings):
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 12
    rest_framework = copy.deepcopy(settings.REST_FRAMEWORK)
    rest_framework["DEFAULT_THROTTLE_RATES"]["public_gallery"] = "200/min"
    with override_settings(REST_FRAMEWORK=rest_framework):
        staff = make_staff()
        category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
        for index in range(100):
            image = GalleryImage.objects.create(
                category=category,
                uploaded_by=staff,
                title=f"Image {index}",
                status=GalleryImage.Status.PUBLISHED,
                show_on_homepage=True,
                is_featured=True,
            )
            GalleryImageVariant.objects.create(
                gallery_image=image,
                variant_type=GalleryImageVariant.VariantType.HERO,
                storage_key=f"gallery/variants/hero_{index}.webp",
                width=1600,
                height=1200,
                format="webp",
                size_bytes=1000,
                sha256_hash="b" * 64,
                is_public=True,
            )

        for _ in range(100):
            response = Client().get("/api/gallery/public/homepage/", secure=True)
            assert response.status_code == 200
            assert len(response.json()["images"]) == 12

    assert settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["public_gallery"] == "60/min"
