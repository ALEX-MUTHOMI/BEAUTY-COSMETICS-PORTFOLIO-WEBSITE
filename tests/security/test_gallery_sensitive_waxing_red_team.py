import pytest

from bookings.models import GalleryCategory, GalleryImage, GallerySubcategory
from bookings.services.gallery_public import get_homepage_gallery
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_sensitive_waxing_red_team_never_reaches_homepage():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Waxing", slug="waxing", is_sensitive_default=True)
    subcategory = GallerySubcategory.objects.create(
        category=category,
        name="Brazilian",
        slug="brazilian",
        sensitivity_default=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning_default=True,
    )
    GalleryImage.objects.create(
        category=category,
        subcategory=subcategory,
        uploaded_by=staff,
        status=GalleryImage.Status.PUBLISHED,
        show_on_homepage=True,
        sensitivity_level=GalleryImage.Sensitivity.RESTRICTED,
        requires_warning=True,
    )

    assert get_homepage_gallery()["images"] == []
