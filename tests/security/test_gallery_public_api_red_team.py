import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_public_api_red_team_rejects_internal_field_leakage():
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    GalleryImage.objects.create(
        category=category,
        uploaded_by=make_staff(),
        status=GalleryImage.Status.PUBLISHED,
        original_private_key="gallery/originals-private/raw",  # pragma: allowlist secret
        quarantine_key="gallery/quarantine/raw",  # pragma: allowlist secret
    )

    payload = Client().get("/api/gallery/public/categories/makeup/", secure=True).json()
    rendered = str(payload).lower()
    assert "original" not in rendered
    assert "quarantine" not in rendered
    assert "uploaded_by" not in rendered
    assert "staff" not in rendered
