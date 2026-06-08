import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from bookings.models import GalleryAuditLog, GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_red_team_rejected_payload_has_no_public_artifacts(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("attack.jpg", b"<script>alert(1)</script>", content_type="image/jpeg"),
        },
        secure=True,
    )

    assert response.status_code == 400
    assert GalleryImage.objects.count() == 0
    assert GalleryImageVariant.objects.count() == 0
    assert GalleryAuditLog.objects.filter(event_type=GalleryAuditLog.EventType.REJECTED).exists()
