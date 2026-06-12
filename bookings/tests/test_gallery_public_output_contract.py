import pytest

from bookings.gallery.selectors.public_gallery import get_homepage_gallery, get_public_category_gallery
from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_public_gallery_returns_only_published_optimized_variants_and_no_private_fields():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    image = GalleryImage.objects.create(
        category=category,
        uploaded_by=staff,
        title="<script>alert(1)</script> Glow",
        status=GalleryImage.Status.PUBLISHED,
        is_featured=True,
        show_on_homepage=True,
        quarantine_key="gallery/quarantine/private",  # pragma: allowlist secret
        original_private_key="gallery/originals-private/private",  # pragma: allowlist secret
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/variants/mobile.webp",  # pragma: allowlist secret
        width=640,
        height=480,
        format="webp",
        size_bytes=1000,
        sha256_hash="b" * 64,
        is_public=True,
    )
    GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.DRAFT)

    payload = get_homepage_gallery()

    assert len(payload["images"]) == 1
    rendered = str(payload)
    assert "<" not in payload["images"][0]["title"]
    assert "alert" not in payload["images"][0]["title"].lower()
    assert "quarantine" not in rendered
    assert "originals-private" not in rendered
    assert "id" not in payload["images"][0]
    assert payload["images"][0]["variants"]["mobile"]["url"].endswith(".webp")


@pytest.mark.django_db
def test_public_category_output_is_capped_and_sensitive_homepage_excluded(settings):
    settings.GALLERY_PUBLIC_CATEGORY_LIMIT = 2
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 12
    staff = make_staff()
    makeup = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    for index in range(3):
        image = GalleryImage.objects.create(
            category=makeup,
            uploaded_by=staff,
            title=f"Makeup {index}",
            status=GalleryImage.Status.PUBLISHED,
            show_on_homepage=True,
        )
        GalleryImageVariant.objects.create(
            gallery_image=image,
            variant_type=GalleryImageVariant.VariantType.THUMBNAIL,
            storage_key=f"gallery/variants/{index}.webp",
            width=320,
            height=240,
            format="webp",
            size_bytes=100,
            sha256_hash="c" * 64,
            is_public=True,
        )
    GalleryImage.objects.create(
        category=waxing,
        uploaded_by=staff,
        status=GalleryImage.Status.PUBLISHED,
        show_on_homepage=True,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
    )

    assert len(get_public_category_gallery("makeup")["images"]) == 2
    assert all(item["category"]["slug"] != "waxing" for item in get_homepage_gallery()["images"])
