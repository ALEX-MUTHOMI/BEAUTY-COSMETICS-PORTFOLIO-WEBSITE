import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_homepage_carousel_lifecycle_excludes_failed_and_sensitive(client):
    staff = make_staff()
    makeup = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    for category, status, sensitive in [
        (makeup, GalleryImage.Status.PUBLISHED, False),
        (makeup, GalleryImage.Status.FAILED, False),
        (waxing, GalleryImage.Status.PUBLISHED, True),
    ]:
        image = GalleryImage.objects.create(
            category=category,
            uploaded_by=staff,
            status=status,
            title=f"{category.slug}-{status}",
            show_on_homepage=True,
            is_featured=True,
            sensitivity_level=GalleryImage.Sensitivity.RESTRICTED if sensitive else GalleryImage.Sensitivity.NORMAL,
            requires_warning=sensitive,
        )
        GalleryImageVariant.objects.create(
            gallery_image=image,
            variant_type=GalleryImageVariant.VariantType.MOBILE,
            storage_key=f"gallery/variants/{image.public_id}/mobile.webp",
            width=640,
            height=480,
            format="webp",
            size_bytes=1000,
            sha256_hash="f" * 64,
            is_public=True,
        )

    assert [item["title"] for item in client.get("/api/gallery/public/homepage/", secure=True).json()["images"]] == [
        "makeup-published"
    ]
