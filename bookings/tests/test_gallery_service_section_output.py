import pytest
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_service_gallery_endpoint_maps_service_slug_to_category_output():
    staff = make_staff()
    massage = GalleryCategory.objects.create(name="Massage", slug="massage")
    image = GalleryImage.objects.create(
        category=massage, uploaded_by=staff, title="Calm room", status=GalleryImage.Status.PUBLISHED
    )
    GalleryImageVariant.objects.create(
        gallery_image=image,
        variant_type=GalleryImageVariant.VariantType.MOBILE,
        storage_key="gallery/variants/massage.webp",
        width=640,
        height=480,
        format="webp",
        size_bytes=1000,
        sha256_hash="c" * 64,
        is_public=True,
    )

    response = Client().get("/api/gallery/public/services/massage/", secure=True)

    assert response.status_code == 200
    assert response.json()["service"]["slug"] == "massage"
    assert response.json()["images"][0]["title"] == "Calm room"
