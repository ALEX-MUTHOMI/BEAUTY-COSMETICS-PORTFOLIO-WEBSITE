from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError

from bookings.services.staff_auth import STAFF_PORTAL_PERMISSION_CODES, validate_staff_password


class Command(BaseCommand):
    help = (
        "Create an ops-provisioned staff portal user (is_staff=True) with portal permissions. "
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

    def handle(self, *args, **options):
        email = str(options["email"] or "").strip().lower()
        password = str(options["password"] or "")
        display_name = str(options.get("display_name") or "").strip()
        phone = options.get("phone")

        if not email or "@" not in email:
            raise CommandError("A valid --email is required.")

        try:
            validate_staff_password(password, email=email, display_name=display_name)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise CommandError("A user with that email already exists.")

        user = User.objects.create_user(
            email=email,
            phone_number=phone,
            password=password,
            is_staff=True,
            is_active=True,
        )
        for codename in sorted(STAFF_PORTAL_PERMISSION_CODES):
            permission = Permission.objects.filter(codename=codename, content_type__app_label="bookings").first()
            if permission is None:
                raise CommandError(f"Missing bookings permission: {codename}. Run migrations first.")
            user.user_permissions.add(permission)

        self.stdout.write(self.style.SUCCESS(f"Created staff user {email}"))
        self.stdout.write("Sign in at /staff/login")
        self.stdout.write("Post-login landing: /staff/dashboard")
        self.stdout.write("Bookings spreadsheet view: /staff/bookings")
