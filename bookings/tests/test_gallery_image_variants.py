import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.services.gallery_images import process_gallery_image_now
from bookings.services.gallery_storage import GalleryObjectStorage
from bookings.tests.gallery_test_helpers import make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_processing_generates_webp_variants_strips_metadata_and_marks_ready(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=GalleryImage.Status.QUARANTINED,
        quarantine_key="gallery/quarantine/test/original",
    )
    GalleryObjectStorage().put(image.quarantine_key, make_test_image_bytes(size=(1800, 1200)))

    process_gallery_image_now(str(image.public_id))
    image.refresh_from_db()

    assert image.status == GalleryImage.Status.READY
    assert image.source_profile in {"phone_standard", "unknown", "high_res_camera"}
    variants = GalleryImageVariant.objects.filter(gallery_image=image)
    assert variants.count() >= 5
    assert set(variants.values_list("format", flat=True)) == {"webp"}
    assert all(v.width > 0 and v.height > 0 and v.size_bytes > 0 and len(v.sha256_hash) == 64 for v in variants)
    assert all(v.is_public for v in variants)
