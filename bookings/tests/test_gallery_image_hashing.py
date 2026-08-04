import hashlib

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.services.gallery_images import process_gallery_image_now
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_upload_stores_raw_sha256_before_publication(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    content = make_test_image_bytes()

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "title": "Soft glam",
            "image": SimpleUploadedFile("soft-glam.jpg", content, content_type="image/jpeg"),
        },
        secure=True,
    )

    assert response.status_code == 202
    image = GalleryImage.objects.get()
    assert image.raw_original_sha256 == hashlib.sha256(content).hexdigest()
    assert image.status == GalleryImage.Status.QUARANTINED
    assert "raw_original_sha256" not in response.json()["image"]


@pytest.mark.django_db
def test_gallery_processing_stores_variant_hashes_and_keeps_hashes_private():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    content = make_test_image_bytes()
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=GalleryImage.Status.QUARANTINED,
        quarantine_key="gallery/quarantine/hash/original",
        raw_original_sha256=hashlib.sha256(content).hexdigest(),
    )
    from bookings.services.gallery_storage import GalleryObjectStorage

    GalleryObjectStorage().put(image.quarantine_key, content)

    process_gallery_image_now(str(image.public_id))

    variants = list(GalleryImageVariant.objects.filter(gallery_image=image))
    assert variants
    for variant in variants:
        stored = GalleryObjectStorage().get(variant.storage_key)
        assert variant.sha256_hash == hashlib.sha256(stored).hexdigest()
    payload = image.public_payload()
    assert "raw_original_sha256" not in str(payload)
    assert "sha256" not in str(payload).lower()


@pytest.mark.django_db
def test_same_bytes_have_same_hash_independent_of_filename(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    content = make_test_image_bytes(color=(30, 40, 50))

    first = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("client-a.jpg", content, content_type="image/jpeg"),
        },
        secure=True,
    )
    second = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("renamed.png", content, content_type="image/png"),
        },
        secure=True,
    )

    assert first.status_code == 202
    assert second.status_code == 409
    assert GalleryImage.objects.count() == 1
