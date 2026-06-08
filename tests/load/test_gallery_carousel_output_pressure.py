import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.services.gallery_public import get_homepage_gallery
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_carousel_output_pressure_is_capped(settings):
    settings.GALLERY_HOMEPAGE_FEATURED_LIMIT = 12
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    for index in range(100):
        image = GalleryImage.objects.create(
            category=category,
            uploaded_by=staff,
            status=GalleryImage.Status.PUBLISHED,
            show_on_homepage=True,
            is_featured=True,
            sort_order=index,
        )
        GalleryImageVariant.objects.create(
            gallery_image=image,
            variant_type=GalleryImageVariant.VariantType.THUMBNAIL,
            storage_key=f"gallery/variants/{index}.webp",
            width=320,
            height=240,
            format="webp",
            size_bytes=500,
            sha256_hash=f"{index:064x}"[-64:],
            is_public=True,
        )

    assert len(get_homepage_gallery()["images"]) == 12
