import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_upload_intent_pressure_is_bounded_by_caps(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    settings.GALLERY_MAX_DAILY_UPLOADS = 30
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    statuses = []
    for index in range(35):
        response = client.post(
            "/api/staff/gallery/images/",
            {
                "category_public_id": str(category.public_id),
                "image": SimpleUploadedFile(
                    f"{index}.jpg", make_test_image_bytes(size=(640, 480)), content_type="image/jpeg"
                ),
            },
            secure=True,
        )
        statuses.append(response.status_code)

    assert statuses.count(202) == 30
    assert statuses.count(429) == 5
    assert GalleryImage.objects.count() == 30
