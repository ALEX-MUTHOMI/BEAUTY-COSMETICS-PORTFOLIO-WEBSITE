import pytest
from django.test import Client

from bookings.models import GalleryCategory


@pytest.mark.django_db
def test_empty_public_gallery_latency_path_is_fast_and_safe():
    GalleryCategory.objects.create(name="Makeup", slug="makeup")
    response = Client().get("/api/gallery/public/categories/makeup/", secure=True)
    assert response.status_code == 200
    assert response.json()["images"] == []
