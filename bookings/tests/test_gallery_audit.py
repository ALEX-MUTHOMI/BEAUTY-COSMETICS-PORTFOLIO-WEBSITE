import pytest

from bookings.models import GalleryAuditLog, GalleryCategory
from bookings.services.gallery_images import audit_gallery_event
from bookings.tests.test_staff_auth_helpers import make_staff


@pytest.mark.django_db
def test_gallery_audit_redacts_ip_and_user_agent():
    staff = make_staff()
    category = GalleryCategory.objects.create(name="Makeup", slug="makeup")

    event = audit_gallery_event(
        GalleryAuditLog.EventType.UPLOAD_INTENT_CREATED,
        staff_user=staff,
        metadata={"category": category.slug},
        ip_address="10.1.2.3",
        user_agent="Mozilla raw agent",
    )

    assert event.ip_hash_hmac
    assert event.user_agent_hash_hmac
    assert "10.1.2.3" not in str(event.__dict__)
    assert "Mozilla raw agent" not in str(event.__dict__)
