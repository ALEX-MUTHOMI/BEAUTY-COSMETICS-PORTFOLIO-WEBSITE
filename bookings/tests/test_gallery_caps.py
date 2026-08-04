import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from bookings.models import GalleryCategory, GalleryImage
from bookings.services.gallery_images import enforce_gallery_caps
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
@override_settings(GALLERY_MAX_PUBLISHED_IMAGES=1, GALLERY_MAX_DRAFT_IMAGES=1)
def test_gallery_caps_are_server_side_not_frontend_only():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")
    GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.PUBLISHED)
    with pytest.raises(ValidationError):
        enforce_gallery_caps(staff_user=staff, desired_status=GalleryImage.Status.PUBLISHED)

    GalleryImage.objects.create(category=category, uploaded_by=staff, status=GalleryImage.Status.DRAFT)
    with pytest.raises(ValidationError):
        enforce_gallery_caps(staff_user=staff, desired_status=GalleryImage.Status.DRAFT)
