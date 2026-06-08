import pytest

from bookings.services.gallery_public import get_homepage_gallery


@pytest.mark.django_db
@pytest.mark.latency
def test_gallery_carousel_empty_latency_path_is_small():
    assert get_homepage_gallery() == {"images": []}
