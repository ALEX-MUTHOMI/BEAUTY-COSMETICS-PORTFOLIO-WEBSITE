import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings

from bookings.models import GalleryCategory, GalleryImage, GalleryUploadBatch
from bookings.tests.gallery_test_helpers import make_staff_session, make_test_image_bytes
from bookings.tests.test_staff_auth_helpers import make_customer, make_staff


@pytest.mark.django_db
def test_staff_can_create_upload_batch_and_image_enters_quarantine(settings, tmp_path):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)
    upload = SimpleUploadedFile("phone.jpg", make_test_image_bytes(), content_type="image/jpeg")

    response = client.post(
        "/api/staff/gallery/images/",
        {"category_public_id": str(category.public_id), "title": "Soft glam", "image": upload},
        secure=True,
    )

    assert response.status_code == 202
    image = GalleryImage.objects.get()
    batch = GalleryUploadBatch.objects.get()
    assert image.upload_batch == batch
    assert image.status == GalleryImage.Status.QUARANTINED
    assert image.quarantine_key.startswith("gallery/quarantine/")
    assert "phone.jpg" not in image.quarantine_key
    assert "quarantine_key" not in response.json()["image"]


@pytest.mark.django_db
def test_anonymous_and_customer_uploads_are_blocked(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    payload = {"category_public_id": str(category.public_id), "image": SimpleUploadedFile("x.jpg", b"x")}

    assert Client(enforce_csrf_checks=False).post("/api/staff/gallery/images/", payload, secure=True).status_code == 403

    customer = make_customer()
    customer_client = Client(enforce_csrf_checks=False)
    customer_client.force_login(customer)
    assert customer_client.post("/api/staff/gallery/images/", payload, secure=True).status_code == 403


@pytest.mark.django_db
@override_settings(GALLERY_MAX_DAILY_UPLOADS=1)
def test_batch_cap_rejects_forged_over_limit_upload_intent(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.QUARANTINED)
    client = make_staff_session(Client(enforce_csrf_checks=False), staff)

    response = client.post(
        "/api/staff/gallery/images/",
        {
            "category_public_id": str(category.public_id),
            "image": SimpleUploadedFile("another.jpg", make_test_image_bytes(), content_type="image/jpeg"),
        },
        secure=True,
    )

    assert response.status_code == 429
    assert GalleryImage.objects.count() == 1
