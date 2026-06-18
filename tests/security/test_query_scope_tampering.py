import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from bookings.models import GalleryCategory, GalleryImage
from bookings.tests.test_staff_auth_helpers import make_staff

User = get_user_model()


@pytest.mark.django_db
def test_public_gallery_query_scope_cannot_include_private_or_storage_fields():
    category = GalleryCategory.objects.create(name="Braids", slug="braids")
    GalleryImage.objects.create(
        category=category,
        uploaded_by=make_staff(email="gallery-scope-staff@example.com"),
        status=GalleryImage.Status.QUARANTINED,
        title="Private draft",
        original_private_key="gallery/private/original-key",  # pragma: allowlist secret
        quarantine_key="gallery/quarantine/private-key",  # pragma: allowlist secret
    )

    response = Client().get(
        "/api/gallery/public/categories/braids/?include_private=true&scope=all&owner_id=1",
        secure=True,
    )

    assert response.status_code == 200
    body = response.content.decode("utf-8", errors="replace").lower()
    assert "private draft" not in body
    assert "original" not in body
    assert "quarantine" not in body
    assert "storage_key" not in body
    assert "uploaded_by" not in body


@pytest.mark.django_db
def test_staff_schedule_query_scope_tampering_does_not_bypass_authentication():
    customer = User.objects.create_user(email="query-scope@example.com", phone_number="+254700660001")
    client = Client()
    client.force_login(customer)

    response = client.get(
        "/api/staff/bookings/schedule/?date=2026-06-08&customer_id=1&include_private=true&scope=all",
        secure=True,
    )

    assert response.status_code == 403
    body = response.content.decode("utf-8", errors="replace")
    assert "appointments" not in body
    assert "customer_display_name_safe" not in body
