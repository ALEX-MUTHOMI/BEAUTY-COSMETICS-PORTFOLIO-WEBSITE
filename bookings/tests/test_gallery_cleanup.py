import pytest
from django.utils import timezone

from bookings.models import GalleryCategory, GalleryImage
from bookings.services.gallery_cleanup import cleanup_gallery_quarantine
from bookings.services.gallery_storage import GalleryObjectStorage
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_cleanup_deletes_old_quarantine_without_touching_published_variants(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    old = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=GalleryImage.Status.FAILED,
        quarantine_key="gallery/quarantine/old/original",
        delete_after=timezone.now(),
    )
    storage = GalleryObjectStorage()
    storage.put(old.quarantine_key, b"old")

    result = cleanup_gallery_quarantine()

    old.refresh_from_db()
    assert result["deleted"] == 1
    assert old.quarantine_key == ""
    assert not storage.exists("gallery/quarantine/old/original")
