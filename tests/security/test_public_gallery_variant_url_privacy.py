import base64
import uuid
from urllib.parse import quote, urlparse

import pytest
from django.test import Client

from bookings.infrastructure.gallery_storage import GalleryObjectStorage, GalleryStorageError, public_variant_url
from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


def _variant(*, status=GalleryImage.Status.PUBLISHED, is_public=True, storage_key=None, staff=None):
    staff = staff or make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug=f"makeup-{uuid.uuid4().hex[:8]}")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        status=status,
        show_on_homepage=True,
        title="Published gallery image",
    )
    return GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key=storage_key or f"gallery/variants/private-segment/{uuid.uuid4()}/mobile.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=16,
        sha256_hash="a" * 64,
        is_public=is_public,
    )


def _path_from_url(url):
    return urlparse(url).path


def _assert_url_hides_key(url, raw_key):
    reversible_forms = {
        raw_key,
        base64.b64encode(raw_key.encode()).decode(),
        base64.urlsafe_b64encode(raw_key.encode()).decode().rstrip("="),
        raw_key.encode().hex(),
        quote(raw_key, safe=""),
        raw_key.replace("/", "_"),
        raw_key.replace("/", "-"),
        raw_key.rsplit("/", 1)[-1],
    }
    lowered = url.lower()
    assert all(value.lower() not in lowered for value in reversible_forms)
    assert all(marker not in lowered for marker in {"quarantine", "private", "draft", "original", "uploads", "source"})


@pytest.mark.django_db
def test_public_variant_url_accepts_only_random_variant_public_identifier_and_hides_storage_structure():
    variant = _variant(storage_key="gallery/quarantine/private-source/customer-99/original.webp")

    url = public_variant_url(variant.public_id, variant.format)

    assert url.startswith("/media/public/")
    assert url.endswith(".webp")
    _assert_url_hides_key(url, variant.storage_key)
    with pytest.raises(GalleryStorageError):
        public_variant_url(variant.storage_key, variant.format)


@pytest.mark.django_db
def test_public_variant_url_is_stable_for_one_variant_and_unique_across_variants():
    first = _variant()
    second = _variant(
        staff=first.gallery_image.uploaded_by,
        storage_key=f"gallery/variants/private-segment/{uuid.uuid4()}/mobile.webp",
    )

    first_url = public_variant_url(first.public_id, first.format)
    assert first_url == public_variant_url(first.public_id, first.format)
    assert first_url != public_variant_url(second.public_id, second.format)


@pytest.mark.django_db
def test_public_media_resolver_serves_only_published_public_variant_and_never_reflects_storage_key(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    variant = _variant()
    storage = GalleryObjectStorage()
    storage.put(variant.storage_key, b"safe-webp-bytes")
    url = public_variant_url(variant.public_id, variant.format)

    response = Client().get(_path_from_url(url), secure=True)

    assert response.status_code == 200
    assert response["Content-Type"] == "image/webp"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["Cache-Control"] == "public, max-age=300"
    assert variant.storage_key not in b"".join(response.streaming_content).decode("latin-1", errors="ignore")
    assert "private-segment" not in response.headers.get("Content-Disposition", "")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "is_public"),
    [
        (GalleryImage.Status.DRAFT, True),
        (GalleryImage.Status.QUARANTINED, True),
        (GalleryImage.Status.FAILED, True),
        (GalleryImage.Status.PUBLISHED, False),
    ],
)
def test_non_public_variant_handle_is_not_resolvable_or_emitted_in_public_gallery(
    status, is_public, tmp_path, settings
):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    variant = _variant(status=status, is_public=is_public)
    GalleryObjectStorage().put(variant.storage_key, b"private-variant-bytes")
    url = public_variant_url(variant.public_id, variant.format)

    direct = Client().get(_path_from_url(url), secure=True)
    homepage = Client().get("/api/gallery/public/homepage/", secure=True)

    assert direct.status_code == 404
    assert str(variant.public_id) not in homepage.content.decode("utf-8")
    assert variant.storage_key not in homepage.content.decode("utf-8")


@pytest.mark.django_db
def test_public_gallery_api_emits_stable_opaque_variant_url_that_resolves(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    variant = _variant()
    GalleryObjectStorage().put(variant.storage_key, b"safe-webp-bytes")
    client = Client()

    first = client.get("/api/gallery/public/homepage/", secure=True)
    second = client.get("/api/gallery/public/homepage/", secure=True)

    assert first.status_code == second.status_code == 200
    first_url = first.json()["images"][0]["variants"][variant.variant_type]["url"]
    second_url = second.json()["images"][0]["variants"][variant.variant_type]["url"]
    assert first_url == second_url
    _assert_url_hides_key(first_url, variant.storage_key)
    assert client.get(_path_from_url(first_url), secure=True).status_code == 200


@pytest.mark.django_db
def test_malformed_or_unknown_public_handle_is_generic_not_found():
    client = Client()

    malformed = client.get("/media/public/not-a-uuid.webp", secure=True)
    unknown = client.get("/media/public/11111111-1111-4111-8111-111111111111.webp", secure=True)

    assert malformed.status_code == unknown.status_code == 404
