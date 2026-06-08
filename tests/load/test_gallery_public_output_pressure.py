import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_public_output_pressure_stays_capped(settings):
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 12
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    for index in range(100):
        GalleryImage.objects.create(
            category=category,
            uploaded_by=staff,
            title=f"Image {index}",
            status=GalleryImage.Status.PUBLISHED,
            show_on_homepage=True,
            is_featured=True,
        )

    for _ in range(100):
        response = Client().get("/api/gallery/public/homepage/", secure=True)
        assert response.status_code == 200
        assert len(response.json()["images"]) == 12
