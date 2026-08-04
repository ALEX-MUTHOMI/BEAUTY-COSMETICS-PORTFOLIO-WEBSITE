"""Staff portal RBAC helpers — role → permission grants and booking scope."""

from django.contrib.auth.models import Permission

from bookings.models import StaffProfile

# Codename grants per role (bookings app). Superuser bypasses via Django.
ROLE_PERMISSION_CODES = {
    StaffProfile.Role.OWNER: {
        "view_staff_portal",
        "view_staff_booking",
        "view_staff_payment_summary",
        "view_staff_contact_details",
        "manage_staff_booking_notes",
        "confirm_staff_attendance",
        "assign_staff_booking",
        "download_staff_receipt",
        "view_staff_payments_desk",
    },
    StaffProfile.Role.RECEPTIONIST: {
        "view_staff_portal",
        "view_staff_booking",
        "view_staff_payment_summary",
        "view_staff_contact_details",
        "manage_staff_booking_notes",
        "confirm_staff_attendance",
        "assign_staff_booking",
    },
    StaffProfile.Role.BEAUTICIAN: {
        "view_staff_portal",
        "view_staff_booking",
        "view_staff_payment_summary",
    },
}


def permission_codes_for_role(role: str) -> set[str]:
    return set(ROLE_PERMISSION_CODES.get(role, ROLE_PERMISSION_CODES[StaffProfile.Role.RECEPTIONIST]))


def apply_role_permissions(user, role: str) -> StaffProfile:
    """Set StaffProfile.role and replace bookings staff portal permissions for the role."""
    codes = permission_codes_for_role(role)
    staff_perms = list(Permission.objects.filter(content_type__app_label="bookings", codename__in=codes))
    all_portal = list(
        Permission.objects.filter(
            content_type__app_label="bookings",
            codename__in=set().union(*ROLE_PERMISSION_CODES.values()),
        )
    )
    user.user_permissions.remove(*all_portal)
    user.user_permissions.add(*staff_perms)
    profile, _ = StaffProfile.objects.update_or_create(
        user=user,
        defaults={"role": role, "display_name": profile_display_name(user)},
    )
    return profile


def profile_display_name(user) -> str:
    email = str(getattr(user, "email", "") or "")
    local = email.split("@", 1)[0].replace(".", " ").replace("_", " ").strip()
    return (local[:80] or "Staff").title()


def get_staff_role(user) -> str | None:
    profile = getattr(user, "staff_profile", None)
    if profile is None:
        try:
            profile = StaffProfile.objects.filter(user_id=user.pk).first()
        except Exception:
            return None
    return profile.role if profile else None


def is_beautician(user) -> bool:
    return get_staff_role(user) == StaffProfile.Role.BEAUTICIAN


def scope_bookings_queryset(queryset, user):
    """Beauticians only see assigned bookings; owner/receptionist see all."""
    if is_beautician(user):
        return queryset.filter(assigned_staff_id=user.pk)
    return queryset
