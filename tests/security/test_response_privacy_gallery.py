import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff
from bookings.tests.test_staff_portal_helpers import staff_login
from tests.security.response_privacy_helpers import (
    AUTH_KEY_MARKERS,
    INTERNAL_DEBUG_KEY_MARKERS,
    PAYMENT_PROVIDER_KEY_MARKERS,
    STORAGE_KEY_MARKERS,
    assert_response_excludes_categories,
)


def _published_image():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        title="<script>alert(1)</script> Soft glam",
        description="Client safe display",
        status=GalleryImage.Status.PUBLISHED,
        is_featured=True,
        show_on_homepage=True,
        quarantine_key="gallery/quarantine/private-path",
        original_private_key="gallery/originals/private-path",  # pragma: allowlist secret
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/private-storage/mobile.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=1000,
        sha256_hash="a" * 64,
        is_public=True,
    )
    GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        title="Draft private",
        status=GalleryImage.Status.DRAFT,
        quarantine_key="gallery/quarantine/draft-private",
    )
    return image


@pytest.mark.django_db
def test_public_gallery_response_exposes_only_public_display_data():
    image = _published_image()

    response = Client().get("/api/gallery/public/homepage/?include_private=true&owner_id=1", secure=True)

    assert response.status_code == 200
    payload = assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        allowed_keys={"public_id"},
        forbidden_values={
            "gallery/quarantine/private-path",
            "gallery/originals/private-path",
            "gallery/private-storage/mobile.webp",
            str(image.id),
            "Draft private",
            "<script>",
            "alert",
        },
    )
    assert len(payload["images"]) == 1
    assert "variants" in payload["images"][0]


@pytest.mark.django_db
def test_public_gallery_missing_category_response_does_not_leak_storage_or_owner_state():
    response = Client().get("/api/gallery/public/categories/does-not-exist/?include_private=true", secure=True)

    assert response.status_code == 404
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        forbidden_values={"does-not-exist", "private", "owner"},
    )


@pytest.mark.django_db
def test_staff_gallery_categories_do_not_expose_upload_storage_internals():
    _published_image()
    client = Client()
    staff_login(client)

    response = client.get("/api/staff/gallery/categories/", secure=True)

    assert response.status_code == 200
    assert_response_excludes_categories(
        response,
        categories=(
            AUTH_KEY_MARKERS,
            PAYMENT_PROVIDER_KEY_MARKERS,
            STORAGE_KEY_MARKERS,
            INTERNAL_DEBUG_KEY_MARKERS,
        ),
        allowed_keys={"public_id"},
        forbidden_values={"gallery/quarantine", "gallery/originals", "gallery/private-storage"},
    )
