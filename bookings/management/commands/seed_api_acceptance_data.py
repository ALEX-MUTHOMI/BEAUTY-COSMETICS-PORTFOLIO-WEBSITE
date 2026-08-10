from datetime import time
from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.redaction import hash_sensitive_value, redact_phone
from bookings.models import (
    BookableResource,
    Booking,
    BusinessHours,
    CustomerProfile,
    FullPackage,
    GalleryCategory,
    GalleryImage,
    GalleryImageVariant,
    GallerySubcategory,
    Service,
    ServiceCategory,
    ServiceSubcategory,
)
from bookings.services.legal import ensure_default_legal_documents
from checkout.models import CheckoutAttempt, CheckoutSession

LOCAL_STAFF_EMAIL = "api.staff@example.invalid"
LOCAL_STAFF_PASSWORD = "LocalApiAcceptancePassphrase!2026"
SEEDED_PAYMENT_BOOKING_PUBLIC_ID = UUID("11111111-1111-4111-8111-111111111111")
SEEDED_CHECKOUT_ID = UUID("22222222-2222-4222-8222-222222222222")
SEEDED_CALLBACK_ID = "fake_ws_CO_api_acceptance_seed_stk"


class Command(BaseCommand):
    help = "Seed deterministic fake data for local Postman/Newman API acceptance runs."

    def handle(self, *args, **options):
        ensure_default_legal_documents()
        staff = self._seed_staff()
        service = self._seed_service()
        package = self._seed_package()
        resource = self._seed_resource()
        gallery_category, gallery_subcategory = self._seed_gallery_taxonomy()
        self._seed_public_gallery_image(staff, gallery_category, gallery_subcategory)
        self._seed_payment_callback_flow(service, resource)
        self.stdout.write(
            "api_acceptance_data "
            f"staff_email={LOCAL_STAFF_EMAIL} "
            f"service_public_id={service.id} "
            f"full_package_public_id={package.public_id} "
            f"resource_public_id={resource.id} "
            f"seeded_payment_booking_public_id={SEEDED_PAYMENT_BOOKING_PUBLIC_ID} "
            f"gallery_category_slug={gallery_category.slug} "
            f"gallery_subcategory_slug={gallery_subcategory.slug}"
        )

    def _seed_staff(self):
        User = get_user_model()
        staff, _created = User.objects.get_or_create(
            email=LOCAL_STAFF_EMAIL,
            defaults={"is_staff": True, "is_superuser": True, "is_active": True},
        )
        staff.is_staff = True
        staff.is_superuser = True
        staff.is_active = True
        staff.set_password(LOCAL_STAFF_PASSWORD)
        staff.save(update_fields=["is_staff", "is_superuser", "is_active", "password", "updated_at"])
        return staff

    def _seed_service(self):
        category, _ = ServiceCategory.objects.get_or_create(
            slug="api-acceptance-hair",
            defaults={"name": "API Acceptance Hair", "sort_order": 1},
        )
        subcategory, _ = ServiceSubcategory.objects.get_or_create(
            category=category,
            slug="api-acceptance-braids",
            defaults={"name": "API Acceptance Braids", "sort_order": 1},
        )
        service, _ = Service.objects.get_or_create(
            slug="api-acceptance-braids",
            defaults={
                "name": "API Acceptance Braids",
                "category": "hair",
                "category_ref": category,
                "subcategory": subcategory,
                "duration_minutes": 60,
                "base_price": Decimal("2500.00"),
                "currency": "KES",
                "sort_order": 1,
            },
        )
        update_fields = []
        for field, value in {
            "is_active": True,
            "category_ref": category,
            "subcategory": subcategory,
            "duration_minutes": 60,
            "base_price": Decimal("2500.00"),
            "currency": "KES",
        }.items():
            if getattr(service, field) != value:
                setattr(service, field, value)
                update_fields.append(field)
        if update_fields:
            service.save(update_fields=[*update_fields, "updated_at"])
        return service

    def _seed_package(self):
        package, _ = FullPackage.objects.get_or_create(
            slug="api-acceptance-bridal-package",
            defaults={
                "name": "API Acceptance Bridal Package",
                "description": "Predefined local acceptance package.",
                "duration_minutes": 240,
                "price_amount": Decimal("12000.00"),
                "currency": "KES",
                "sort_order": 1,
                "is_active": True,
            },
        )
        if not package.is_active:
            package.is_active = True
            package.save(update_fields=["is_active", "updated_at"])
        return package

    def _seed_resource(self):
        resource, _ = BookableResource.objects.get_or_create(
            name="API Acceptance Chair",
            defaults={"resource_type": BookableResource.Type.CHAIR, "is_active": True},
        )
        if not resource.is_active:
            resource.is_active = True
            resource.save(update_fields=["is_active", "updated_at"])
        for weekday in BusinessHours.Weekday.values:
            BusinessHours.objects.get_or_create(
                resource=resource,
                weekday=weekday,
                defaults={
                    "opens_at": None if weekday == BusinessHours.Weekday.SUNDAY else time(7, 0),
                    "closes_at": None if weekday == BusinessHours.Weekday.SUNDAY else time(19, 0),
                    "is_closed": weekday == BusinessHours.Weekday.SUNDAY,
                },
            )
        return resource

    def _seed_gallery_taxonomy(self):
        category, _ = GalleryCategory.objects.get_or_create(
            slug="api-acceptance-gallery",
            defaults={"name": "API Acceptance Gallery", "sort_order": 1},
        )
        subcategory, _ = GallerySubcategory.objects.get_or_create(
            category=category,
            slug="api-acceptance-results",
            defaults={"name": "API Acceptance Results", "sort_order": 1},
        )
        return category, subcategory

    def _seed_public_gallery_image(self, staff, category, subcategory):
        image, _ = GalleryImage.objects.get_or_create(
            title="API Acceptance Result",
            category=category,
            subcategory=subcategory,
            defaults={
                "uploaded_by": staff,
                "status": GalleryImage.Status.PUBLISHED,
                "show_on_homepage": False,
                "is_featured": False,
                "published_at": timezone.now(),
                "raw_original_sha256": "a" * 64,
            },
        )
        if image.show_on_homepage:
            image.show_on_homepage = False
            image.is_featured = False
            image.save(update_fields=["show_on_homepage", "is_featured", "updated_at"])
        GalleryImageVariant.objects.get_or_create(
            gallery_image=image,
            variant_type=GalleryImageVariant.VariantType.HERO,
            defaults={
                "storage_key": "gallery/variants/api-acceptance-result.webp",
                "width": 1600,
                "height": 900,
                "format": "webp",
                "size_bytes": 2048,
                "sha256_hash": "b" * 64,
                "is_public": True,
            },
        )

    def _seed_payment_callback_flow(self, service, resource):
        User = get_user_model()
        customer_user, _ = User.objects.get_or_create(
            email="api.customer@example.invalid",
            defaults={"phone_number": "+254700000000", "is_active": True},
        )
        if not customer_user.phone_number:
            customer_user.phone_number = "+254700000000"
            customer_user.save(update_fields=["phone_number", "updated_at"])
        profile = CustomerProfile.create_from_plaintext(
            full_name="API Customer",
            email="api.customer@example.invalid",
            phone="+254700000000",
            reminder_consent=True,
        )
        starts_at = timezone.now().replace(minute=0, second=0, microsecond=0) + timezone.timedelta(days=10)
        booking, created = Booking.objects.get_or_create(
            public_id=SEEDED_PAYMENT_BOOKING_PUBLIC_ID,
            defaults={
                "customer_profile": profile,
                "service": service,
                "resource": resource,
                "starts_at": starts_at,
                "ends_at": starts_at + timezone.timedelta(minutes=service.duration_minutes),
                "status": Booking.Status.PAYMENT_PENDING,
                "idempotency_key": "api-acceptance-seeded-payment-booking",
                "privacy_policy_accepted_at": timezone.now(),
                "no_refund_policy_accepted_at": timezone.now(),
                "total_price_snapshot": service.base_price,
                "currency_snapshot": service.currency,
            },
        )
        if not created and booking.status not in {Booking.Status.CONFIRMED, Booking.Status.PAYMENT_PENDING}:
            booking.status = Booking.Status.PAYMENT_PENDING
            booking.save(update_fields=["status", "updated_at"])
        session, _ = CheckoutSession.objects.get_or_create(
            id=SEEDED_CHECKOUT_ID,
            defaults={
                "customer": customer_user,
                "amount_snapshot": service.base_price,
                "currency": service.currency,
                "description_snapshot": f"Booking {booking.public_id}",
                "purchasable_type": "booking",
                "purchasable_id": str(booking.id),
                "status": CheckoutSession.Status.STK_SENT,
                "idempotency_key": "api-acceptance-seeded-checkout",
                "expires_at": timezone.now() + timezone.timedelta(minutes=30),
            },
        )
        if session.status not in {CheckoutSession.Status.PAID, CheckoutSession.Status.STK_SENT}:
            session.status = CheckoutSession.Status.STK_SENT
            session.save(update_fields=["status", "updated_at"])
        if booking.checkout_session_id != str(session.id):
            booking.checkout_session_id = str(session.id)
            booking.save(update_fields=["checkout_session_id", "updated_at"])
        CheckoutAttempt.objects.get_or_create(
            provider_request_id=SEEDED_CALLBACK_ID,
            defaults={
                "checkout_session": session,
                "phone_number_hash": hash_sensitive_value("+254700000000"),
                "redacted_phone": redact_phone("+254700000000"),
                "merchant_request_id": "fake_merchant_api_acceptance_seed_stk",
                "idempotency_key": "api-acceptance-seeded-stk",
                "status": CheckoutAttempt.Status.SENT,
                "raw_request_hash": hash_sensitive_value("api-acceptance-seeded-stk"),
                "redacted_request_payload": {
                    "CheckoutRequestID": "[redacted]",
                    "MerchantRequestID": "[redacted]",
                    "PhoneNumber": "+2547***000",
                },
            },
        )
