import pytest
from django.core.exceptions import ValidationError

from bookings.models import GalleryCategory, GalleryImage
from bookings.services.gallery_images import process_gallery_image_now
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_missing_quarantine_object_fails_closed_without_publish(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    image = GalleryImage.objects.create(
        category=GalleryCategory.objects.create(name="Makeup", slug="makeup"),
        uploaded_by=make_staff(),
        status=GalleryImage.Status.QUARANTINED,
        quarantine_key="gallery/quarantine/missing/original",
    )

    with pytest.raises(ValidationError):
        process_gallery_image_now(str(image.public_id))

    image.refresh_from_db()
    assert image.status == GalleryImage.Status.FAILED
    assert image.processing_error_code == "storage_missing"
