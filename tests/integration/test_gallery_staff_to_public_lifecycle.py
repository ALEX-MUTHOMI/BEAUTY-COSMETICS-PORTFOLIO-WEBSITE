import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from bookings.models import GalleryCategory, GalleryImage
from bookings.services.gallery_images import process_gallery_image_now, publish_gallery_image
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_staff_upload_processed_image_reaches_public_category(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("upload.jpg", make_test_image_bytes(), content_type="image/jpeg"),
        },
        secure=True,
    )
    assert response.status_code == 202
    image = GalleryImage.objects.get()
    process_gallery_image_now(str(image.public_id))
    image.refresh_from_db()
    publish_gallery_image(image, staff_user=staff)

    public = client.get("/api/gallery/public/categories/makeup/", secure=True)
    assert public.status_code == 200
    assert public.json()["images"][0]["variants"]["mobile"]["url"].endswith(".webp")
