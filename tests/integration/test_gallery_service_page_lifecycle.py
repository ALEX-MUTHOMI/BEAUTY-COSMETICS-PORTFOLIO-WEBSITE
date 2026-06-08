import pytest

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_service_page_gallery_contract_is_public_safe(client):
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Facial / Skincare", slug="facial")
    image = GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.PUBLISHED)
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.TABLET,
        storage_key="gallery/variants/facial.webp",
        width=960,
        height=720,
        format="webp",
        size_bytes=1000,
        sha256_hash="1" * 64,
        is_public=True,
    )

    rendered = str(client.get("/api/gallery/public/services/facial/", secure=True).json()).lower()
    assert "facial" in rendered
    assert "original" not in rendered
    assert "quarantine" not in rendered
