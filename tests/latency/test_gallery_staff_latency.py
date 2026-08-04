import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from bookings.models import GalleryCategory
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_invalid_gallery_file_fails_before_heavy_processing(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("bad.jpg", b"not-image", content_type="image/jpeg"),
        },
        secure=True,
    )

    assert response.status_code == 400
