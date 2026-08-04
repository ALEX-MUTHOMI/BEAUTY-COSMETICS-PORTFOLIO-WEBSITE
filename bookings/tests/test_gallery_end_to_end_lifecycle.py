import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from bookings.gallery.selectors.public_gallery import get_homepage_gallery
from bookings.models import GalleryCategory, GalleryImage
from bookings.services.gallery_images import archive_gallery_image, process_gallery_image_now, publish_gallery_image
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_upload_to_public_to_archive_lifecycle(client):
    staff = make_staff()
    make_staff_session(client, staff)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "title": "Lifecycle",
            "image": SimpleUploadedFile("lifecycle.jpg", make_test_image_bytes(), content_type="image/jpeg"),
        },
        secure=True,
    )
    assert response.status_code == 202
    image = GalleryImage.objects.get()
    process_gallery_image_now(str(image.public_id))
    image.refresh_from_db()
    image.show_on_homepage = True
    image.is_featured = True
    image.save(update_fields=["show_on_homepage", "is_featured", "updated_at"])
    publish_gallery_image(image, staff_user=staff)
    assert get_homepage_gallery()["images"][0]["title"] == "Lifecycle"
    archive_gallery_image(image, staff_user=staff)
    assert get_homepage_gallery()["images"] == []
