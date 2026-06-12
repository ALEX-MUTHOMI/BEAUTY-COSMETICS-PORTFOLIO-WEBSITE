import pytest
from django.core.exceptions import ValidationError

from bookings.gallery.selectors.public_gallery import get_homepage_gallery
from bookings.models import GalleryCategory, GalleryImage
from bookings.services import gallery_images
from bookings.services.gallery_images import process_gallery_image_now
from bookings.services.gallery_storage import GalleryObjectStorage
from bookings.tests.gallery_test_helpers import make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_failed_gallery_processing_never_publishes_and_can_retry_when_storage_recovers():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=GalleryImage.Status.QUARANTINED,
        quarantine_key="gallery/quarantine/retry/original",
    )

    with pytest.raises(ValidationError):
        process_gallery_image_now(str(image.public_id))
    image.refresh_from_db()
    assert image.status == GalleryImage.Status.FAILED
    assert get_homepage_gallery()["images"] == []

    GalleryObjectStorage().put(image.quarantine_key, make_test_image_bytes())
    retry_failed_gallery_image = getattr(gallery_images, "retry_failed_gallery_image", None)
    assert retry_failed_gallery_image is not None
    retry_failed_gallery_image(image, staff_user=staff)
    image.refresh_from_db()
    assert image.status == GalleryImage.Status.READY
