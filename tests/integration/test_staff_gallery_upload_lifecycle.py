import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant
from bookings.services.gallery_images import process_gallery_image_now, publish_gallery_image
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_staff_gallery_upload_process_publish_lifecycle(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile(
                "studio.jpg", make_test_image_bytes(size=(1600, 1200)), content_type="image/jpeg"
            ),
        },
        secure=True,
    )
    assert response.status_code == 202
    image = GalleryImage.objects.get()
    process_gallery_image_now(str(image.public_id))
    image.refresh_from_db()
    publish_gallery_image(image, staff_user=staff)

    assert GalleryImageVariant.objects.filter(gallery_image=image, is_public=True).exists()
    assert GalleryImage.objects.get(pk=image.pk).status == GalleryImage.Status.PUBLISHED
