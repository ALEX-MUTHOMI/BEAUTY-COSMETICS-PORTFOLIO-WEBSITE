import pytest
from django.core.exceptions import ValidationError

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant, GallerySubcategory, GalleryUploadBatch
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_models_use_public_ids_and_never_need_raw_storage_keys_publicly():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    subcategory = GallerySubcategory.objects.create(category=category, name="Soft glam", slug="soft-glam")
    batch = GalleryUploadBatch.objects.create(staff_user=staff, image_count=1, total_size_bytes=1024)
    image = GalleryImage.objects.create(
        upload_batch=batch,
        category=category,
        subcategory=subcategory,
        uploaded_by=staff,
        title="Client-safe title",
        quarantine_key="gallery/quarantine/private-original",  # pragma: allowlist secret
        original_private_key="gallery/originals-private/private-original",  # pragma: allowlist secret
        status=GalleryImage.Status.READY,
    )
    variant = GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/variants/mobile.webp",  # pragma: allowlist secret
        width=640,
        height=480,
        format="webp",
        size_bytes=2048,
        sha256_hash="a" * 64,
        is_public=True,
    )

    assert image.public_id
    assert batch.public_id
    assert variant.public_id
    assert str(image.public_id) != str(image.pk)
    assert image.public_payload()["public_id"] == str(image.public_id)
    assert "quarantine_key" not in image.public_payload()
    assert "original_private_key" not in image.public_payload()


@pytest.mark.django_db
def test_gallery_subcategory_must_belong_to_selected_category():
    makeup = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing")
    subcategory = GallerySubcategory.objects.create(category=waxing, name="Bikini", slug="bikini")
    image = GalleryImage(category=makeup, subcategory=subcategory, uploaded_by=make_staff())

    with pytest.raises(ValidationError):
        image.full_clean()
