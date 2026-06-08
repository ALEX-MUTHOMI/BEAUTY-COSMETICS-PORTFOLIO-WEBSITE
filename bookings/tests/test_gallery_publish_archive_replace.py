import pytest

from bookings.models import GalleryAuditLog, GalleryCategory, GalleryImage
from bookings.services.gallery_images import archive_gallery_image, publish_gallery_image
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_publish_and_archive_are_audited_and_stateful():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.READY)

    publish_gallery_image(image, staff_user=staff)
    archive_gallery_image(image, staff_user=staff)
    image.refresh_from_db()

    assert image.status == GalleryImage.Status.ARCHIVED
    assert GalleryAuditLog.objects.filter(gallery_image=image, event_type=GalleryAuditLog.EventType.PUBLISHED).exists()
    assert GalleryAuditLog.objects.filter(gallery_image=image, event_type=GalleryAuditLog.EventType.ARCHIVED).exists()
