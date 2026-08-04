import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("filename", "content", "content_type"),
    [
        ("payload.svg", b"<svg><script>alert(1)</script></svg>", "image/svg+xml"),
        ("payload.jpg", b"<html><script>alert(1)</script></html>", "image/jpeg"),
        ("payload.zip", b"PK\x03\x04not an image", "image/jpeg"),
        ("payload.jpg", b"\xff\xd8broken", "image/jpeg"),
    ],
)
def test_malicious_or_corrupt_uploads_fail_closed(filename, content, content_type, tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile(filename, content, content_type=content_type),
        },
        secure=True,
    )

    assert response.status_code == 400
    assert GalleryImage.objects.count() == 0
    assert "script" not in str(response.json()).lower()


@pytest.mark.django_db
def test_path_traversal_filename_is_not_used_in_storage_key(tmp_path, settings):
    from bookings.services.gallery_storage import build_quarantine_key

    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    key = build_quarantine_key("batch-public", "image-public", "../../evil.jpg")
    assert ".." not in key
    assert "evil.jpg" not in key
    assert key == "gallery/quarantine/batch-public/image-public/original"
