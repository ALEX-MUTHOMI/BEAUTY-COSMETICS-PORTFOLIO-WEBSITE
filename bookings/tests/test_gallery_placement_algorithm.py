import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant, GallerySubcategory
from bookings.services.gallery_public import (
    get_homepage_gallery,
    get_public_category_gallery,
    get_public_subcategory_gallery,
)
from bookings.tests.test_staff_auth_helpers import make_staff


def _published_image(
    category, staff, *, subcategory=None, title="Image", featured=False, homepage=False, sensitive=False
):
    image = GalleryImage.objects.create(
        category=category,
        subcategory=subcategory,
        uploaded_by=staff,
        title=title,
        status=GalleryImage.Status.PUBLISHED,
        is_featured=featured,
        show_on_homepage=homepage,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED if sensitive else GalleryImage.Sensitivity.NORMAL,
        requires_warning=sensitive,
        sort_order=1,
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key=f"gallery/variants/{image.public_id}/mobile.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=1234,
        sha256_hash="a" * 64,
        is_public=True,
    )
    return image


@pytest.mark.django_db
def test_gallery_placement_is_deterministic_and_excludes_non_public_states(settings):
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 2
    staff = make_staff()
    makeup = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    massage = GalleryCategory.objects.create(name="Massage", slug="massage")
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    glam = GallerySubcategory.objects.create(category=makeup, name="Soft glam", slug="soft-glam")
    _published_image(makeup, staff, subcategory=glam, title="Homepage makeup", featured=True, homepage=True)
    _published_image(massage, staff, title="Massage", homepage=False)
    _published_image(waxing, staff, title="Waxing", featured=True, homepage=True, sensitive=True)
    GalleryImage.objects.create(category=makeup, uploaded_by=staff, title="Draft", status=GalleryImage.Status.DRAFT)

    homepage = get_homepage_gallery()["images"]
    assert [item["title"] for item in homepage] == ["Homepage makeup"]
    assert [item["title"] for item in get_public_category_gallery("massage")["images"]] == ["Massage"]
    assert [item["title"] for item in get_public_subcategory_gallery("makeup", "soft-glam")["images"]] == [
        "Homepage makeup"
    ]
