from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError

from bookings.models import StaffProfile
from bookings.services.staff_auth import STAFF_PORTAL_PERMISSION_CODES, validate_staff_password
from bookings.services.staff_roles import apply_role_permissions, permission_codes_for_role


class Command(BaseCommand):
    help = (
        "Create an ops-provisioned staff portal user (is_staff=True) with role-based permissions. "
        "There is no public staff signup — use this command or Django admin."
    )

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Staff login email (unique).")
        parser.add_argument("--password", required=True, help="Staff password (min 15 chars, policy-enforced).")
        parser.add_argument(
            "--display-name",
            default="",
            help="Optional display name used only for password-policy checks.",
        )
        parser.add_argument(
            "--phone",
            default=None,
            help="Optional phone number stored on the user record.",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Also set is_superuser=True (Django admin + full staff portal).",
        )
        parser.add_argument(
            "--role",
            choices=[c.value for c in StaffProfile.Role],
            default=StaffProfile.Role.OWNER,
            help="Staff portal role (default: owner). Maps to permission grants.",
        )

    def handle(self, *args, **options):
        email = str(options["email"] or "").strip().lower()
        password = str(options["password"] or "")
        display_name = str(options.get("display_name") or "").strip()
        phone = options.get("phone")
        as_superuser = bool(options.get("superuser"))
        role = str(options.get("role") or StaffProfile.Role.OWNER)

        if not email or "@" not in email:
            raise CommandError("A valid --email is required.")

        try:
            validate_staff_password(password, email=email, display_name=display_name)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("A user with that email already exists.")

        create = User.objects.create_superuser if as_superuser else User.objects.create_user
        kwargs = {"email": email, "phone_number": phone, "password": password}
        if not as_superuser:
            kwargs["is_staff"] = True
            kwargs["is_active"] = True
        user = create(**kwargs)

        # Ensure permission rows exist before grant.
        for codename in sorted(STAFF_PORTAL_PERMISSION_CODES):
            if not Permission.objects.filter(codename=codename, content_type__app_label="bookings").exists():
                raise CommandError(f"Missing bookings permission: {codename}. Run migrations first.")

        if as_superuser:
            # Superuser bypasses perms; still attach owner profile + all portal codes for /auth/me.
            apply_role_permissions(user, StaffProfile.Role.OWNER)
        else:
            apply_role_permissions(user, role)

        profile_role = StaffProfile.Role.OWNER if as_superuser else role
        granted = sorted(permission_codes_for_role(profile_role))
        label = "superuser" if as_superuser else f"staff ({profile_role})"
        self.stdout.write(self.style.SUCCESS(f"Created {label} user {email}"))
        self.stdout.write(f"Permissions: {', '.join(granted)}")
        self.stdout.write("Sign in at /staff/login")
        self.stdout.write("Post-login landing: /staff/dashboard")
        self.stdout.write("Bookings spreadsheet view: /staff/bookings")
