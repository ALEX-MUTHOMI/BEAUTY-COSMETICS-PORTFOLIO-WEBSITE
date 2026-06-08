from pathlib import Path

import pytest

from bookings.models import GalleryCategory, GallerySubcategory
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_staff_gallery_categories_endpoint_supports_upload_navigation(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    GallerySubcategory.objects.create(category=category, name="Soft glam", slug="soft-glam")

    response = client.get("/api/staff/gallery/categories/", secure=True)

    assert response.status_code == 200
    payload = response.json()
    assert payload["categories"][0]["name"] == "Makeup"
    assert payload["categories"][0]["subcategories"][0]["name"] == "Soft glam"
    rendered = str(payload).lower()
    assert "storage" not in rendered
    assert "quarantine" not in rendered


def test_staff_gallery_frontend_is_wired_to_upload_flow_without_backend_jargon():
    component = Path("frontend/src/staff/StaffGalleryWorkspace.vue").read_text(encoding="utf-8")

    assert "Uploads are disabled" not in component
    assert "Upload images unavailable" not in component
    assert "Checking image" in component
    assert "Preparing for website" in component
    assert "Ready to publish" in component
    assert "Could not use this image" in component
    assert "quarantine" not in component.lower()
    assert "storage key" not in component.lower()
