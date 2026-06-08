import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_red_team_blocks_svg_xss_and_private_key_leakage(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("xss.svg", b"<svg onload=alert(1)>", content_type="image/svg+xml"),
        },
        secure=True,
    )

    assert response.status_code == 400
    assert GalleryImage.objects.count() == 0
    assert "quarantine" not in str(response.json()).lower()
