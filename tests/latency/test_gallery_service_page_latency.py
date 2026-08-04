import pytest

from bookings.models import GalleryCategory


@pytest.mark.django_db
@pytest.mark.latency
def test_gallery_service_page_missing_category_is_generic(client):
    response = client.get("/api/gallery/public/services/unknown/", secure=True)
    assert response.status_code == 404
    assert "traceback" not in response.content.decode().lower()
    GalleryCategory.objects.create(name="Makeup", slug="makeup")
    assert client.get("/api/gallery/public/services/makeup/", secure=True).status_code == 200
