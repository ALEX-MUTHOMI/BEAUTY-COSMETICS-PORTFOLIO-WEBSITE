import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from bookings.models import GalleryAuditLog, GalleryCategory, GalleryImage
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_duplicate_gallery_upload_is_rejected_without_internal_hash_leak(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    content = make_test_image_bytes()

    payload = {
        "category_public_id": str(category.public_id),
        "image": SimpleUploadedFile("first.jpg", content, content_type="image/jpeg"),
    }
    assert client.post("/api/staff/gallery/images/", payload, secure=True).status_code == 202

    duplicate = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("second.jpg", content, content_type="image/jpeg"),
        },
        secure=True,
    )

    assert duplicate.status_code == 409
    rendered = duplicate.content.decode().lower()
    assert "sha" not in rendered
    assert "hash" not in rendered
    assert GalleryImage.objects.count() == 1
    assert GalleryAuditLog.objects.filter(event_type=GalleryAuditLog.EventType.DUPLICATE_REJECTED).exists()
