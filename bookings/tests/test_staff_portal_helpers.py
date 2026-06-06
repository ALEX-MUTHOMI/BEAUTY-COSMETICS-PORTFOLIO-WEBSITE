import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone

from bookings.models import Booking

User = get_user_model()


def make_staff_user(email="beautician@example.com", permissions=None, superuser=False):
    local, _, domain = email.partition("@")
    unique_email = f"{local}-{uuid.uuid4().hex[:8]}@{domain or 'example.com'}"
    user = User.objects.create_user(
        email=unique_email,
        phone_number="+254700000009",
        is_staff=True,
        is_superuser=superuser,
    )
    if permissions:
        for codename in permissions:
            user.user_permissions.add(Permission.objects.get(codename=codename))
    return user


def make_customer_user(email="customer-portal@example.com"):
    return User.objects.create_user(email=email, phone_number="+254700000010")


def staff_login(client, permissions=None, superuser=False):
    user = make_staff_user(permissions=permissions, superuser=superuser)
    client.force_login(user)
    session = client.session
    now = timezone.now().timestamp()
    session["staff_auth_at"] = now
    session["staff_last_activity_at"] = now
    session["staff_recent_auth_at"] = now
    session.save()
    return user


def staff_booking_url(booking):
    return f"/api/staff/bookings/{booking.public_id}/"


def staff_payment_url(booking):
    return f"/api/staff/bookings/{booking.public_id}/payment/"


def staff_contact_url(booking):
    return f"/api/staff/bookings/{booking.public_id}/contact-access/"


def mark_confirmed(booking):
    booking.status = Booking.Status.CONFIRMED
    booking.confirmed_at = booking.starts_at
    booking.save(update_fields=["status", "confirmed_at", "updated_at"])
    return booking
