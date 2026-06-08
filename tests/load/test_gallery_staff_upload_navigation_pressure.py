import pytest

from bookings.models import GalleryCategory, GallerySubcategory
from bookings.tests.gallery_test_helpers import make_staff_session
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_staff_navigation_pressure_is_bounded(client, django_assert_num_queries):
    staff = make_staff()
    make_staff_session(client, staff)
    for index in range(20):
        category = GalleryCategory.objects.create(name=f"Category {index}", slug=f"cat-{index}")
        for sub_index in range(3):
            GallerySubcategory.objects.create(category=category, name=f"Sub {sub_index}", slug=f"sub-{sub_index}")

    with django_assert_num_queries(7):
        response = client.get("/api/staff/gallery/categories/", secure=True)

    assert response.status_code == 200
    assert len(response.json()["categories"]) == 20
