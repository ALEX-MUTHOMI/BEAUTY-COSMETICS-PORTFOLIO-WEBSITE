import pytest
from django.core.exceptions import ValidationError

from bookings.models import GalleryCategory, GalleryImage, GallerySubcategory
from bookings.services.gallery_images import publish_gallery_image
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_sensitive_waxing_requires_confirmation_warning_and_consent_before_publish():
    staff = make_staff()
    waxing = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    bikini = GallerySubcategory.objects.create(
        category=waxing,
        name="Bikini waxing",
        slug="bikini",
        sensitivity_default=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning_default=True,
    )
    image = GalleryImage.objects.create(
        category=waxing,
        subcategory=bikini,
        uploaded_by=staff,
        status=GalleryImage.Status.READY,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
        consent_status=GalleryImage.ConsentStatus.REQUIRED_PENDING,
        is_identifiable=True,
    )

    with pytest.raises(ValidationError):
        publish_gallery_image(image, staff_user=staff)

    image.sensitive_publish_confirmed = True
    image.consent_status = GalleryImage.ConsentStatus.CONFIRMED
    image.show_on_homepage = True
    with pytest.raises(ValidationError):
        publish_gallery_image(image, staff_user=staff)

    image.show_on_homepage = False
    publish_gallery_image(image, staff_user=staff)
    image.refresh_from_db()
    assert image.status == GalleryImage.Status.PUBLISHED
