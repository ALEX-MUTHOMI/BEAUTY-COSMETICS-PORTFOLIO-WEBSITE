import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant, GallerySubcategory
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_category_and_subcategory_outputs_are_scoped_and_capped(settings):
    settings.GALLERY_PUBLIC_SUBCATEGORY_LIMIT = 1
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    glam = GallerySubcategory.objects.create(category=category, name="Soft glam", slug="soft-glam")
    bold = GallerySubcategory.objects.create(category=category, name="Bold glam", slug="bold-glam")
    for subcategory in [glam, bold]:
        image = GalleryImage.objects.create(
            category=category,
            subcategory=subcategory,
            uploaded_by=staff,
            title=subcategory.name,
            status=GalleryImage.Status.PUBLISHED,
        )
        GalleryImageVariant.objects.create(
            gallery_image=image,
            variant_type=GalleryImageVariant.VariantType.MOBILE,
            storage_key=f"gallery/variants/{subcategory.slug}.webp",
            width=640,
            height=480,
            format="webp",
            size_bytes=1000,
            sha256_hash="d" * 64,
            is_public=True,
        )

    payload = Client().get("/api/gallery/public/categories/makeup/soft-glam/", secure=True).json()

    assert len(payload["images"]) == 1
    assert payload["images"][0]["subcategory"]["slug"] == "soft-glam"
