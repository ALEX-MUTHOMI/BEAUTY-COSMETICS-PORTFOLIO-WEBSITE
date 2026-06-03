from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.redaction import hash_sensitive_value
from bookings.models import Booking, BookingPolicyAcceptance, LegalDocument

POLICY_ACCEPTANCE_TEXT = (
    "I agree to the Terms of Service, Privacy Policy, and Booking Policy. I understand that paid bookings are "
    "non-refundable and may only be rescheduled according to the Booking Policy."
)
NO_REFUND_NOTICE = (
    "Paid bookings are non-refundable. Rescheduling may be available according to the Booking Policy. Nothing in "
    "this policy limits rights that cannot legally be excluded under applicable law."
)
REQUIRED_DOCUMENT_TYPES = (
    LegalDocument.DocumentType.TERMS,
    LegalDocument.DocumentType.PRIVACY,
    LegalDocument.DocumentType.BOOKING_POLICY,
)
OPTIONAL_DOCUMENT_TYPES = (
    LegalDocument.DocumentType.COOKIE_NOTICE,
    LegalDocument.DocumentType.DATA_RETENTION,
)
GENERIC_POLICY_ERROR = "Required booking policies must be accepted before checkout."


@dataclass(frozen=True)
class AcceptedPolicyDocuments:
    terms: LegalDocument
    privacy: LegalDocument
    booking_policy: LegalDocument
    cookie_notice: LegalDocument | None = None


DEFAULT_DOCUMENTS = {
    LegalDocument.DocumentType.TERMS: (
        "Terms of Service",
        "v2026.06-draft",
        "Draft for legal review before production. Paid bookings are non-refundable and all appointment times are "
        "Africa/Nairobi.",
        True,
    ),
    LegalDocument.DocumentType.PRIVACY: (
        "Privacy Policy",
        "v2026.06-draft",
        "Draft for legal review before production. Customer data is minimized, encrypted, HMACed, and redacted for "
        "booking, payment, receipt, reminder, and support purposes.",
        True,
    ),
    LegalDocument.DocumentType.BOOKING_POLICY: (
        "Booking, Cancellation, Reschedule, and No-Refund Policy",
        "v2026.06-draft",
        NO_REFUND_NOTICE,
        True,
    ),
    LegalDocument.DocumentType.COOKIE_NOTICE: (
        "Cookie Notice",
        "v2026.06-draft",
        "Draft for legal review before production. Only essential security/session cookies are expected unless a "
        "future consent flow is added.",
        False,
    ),
    LegalDocument.DocumentType.DATA_RETENTION: (
        "Data Retention Policy",
        "v2026.06-draft",
        "Draft for legal review before production. Accounting records, booking records, receipt records, OTP "
        "challenges, notifications, and logs follow limited retention and redaction policies.",
        False,
    ),
}


def _safe_meta(value, max_length):
    return " ".join(str(value or "").replace("\x00", " ").split())[:max_length]


def ensure_default_legal_documents():
    documents = []
    for document_type, (title, version, content, requires_acceptance) in DEFAULT_DOCUMENTS.items():
        document, _created = LegalDocument.objects.get_or_create(
            document_type=document_type,
            version=version,
            defaults={
                "title": title,
                "content_markdown": content,
                "is_active": True,
                "requires_acceptance": requires_acceptance,
                "effective_at": timezone.now(),
            },
        )
        if not document.is_active:
            document.is_active = True
            document.save(update_fields=["is_active", "content_hash", "updated_at"])
        documents.append(document)
    return documents


def get_active_required_documents():
    documents = {
        document.document_type: document
        for document in LegalDocument.objects.filter(
            document_type__in=[*REQUIRED_DOCUMENT_TYPES, *OPTIONAL_DOCUMENT_TYPES],
            is_active=True,
        )
    }
    missing = [document_type for document_type in REQUIRED_DOCUMENT_TYPES if document_type not in documents]
    if missing:
        raise ValidationError(GENERIC_POLICY_ERROR)
    return documents


def assert_checkout_policy_accepted(policy_acceptance):
    documents = get_active_required_documents()
    if not policy_acceptance or not policy_acceptance.get("accepted"):
        raise ValidationError(GENERIC_POLICY_ERROR)
    if policy_acceptance.get("checkbox_text") != POLICY_ACCEPTANCE_TEXT:
        raise ValidationError(GENERIC_POLICY_ERROR)
    return AcceptedPolicyDocuments(
        terms=documents[LegalDocument.DocumentType.TERMS],
        privacy=documents[LegalDocument.DocumentType.PRIVACY],
        booking_policy=documents[LegalDocument.DocumentType.BOOKING_POLICY],
        cookie_notice=documents.get(LegalDocument.DocumentType.COOKIE_NOTICE),
    )


def has_policy_acceptance(*, booking, checkout_session):
    return BookingPolicyAcceptance.objects.filter(booking=booking, checkout_session=checkout_session).exists()


def record_booking_policy_acceptance(*, booking, checkout_session, documents, policy_acceptance, request_context):
    if has_policy_acceptance(booking=booking, checkout_session=checkout_session):
        return BookingPolicyAcceptance.objects.get(booking=booking, checkout_session=checkout_session)

    accepted_at = timezone.now()
    ip_source = request_context.get("ip") or policy_acceptance.get("ip") or ""
    user_agent_source = request_context.get("user_agent") or policy_acceptance.get("user_agent") or ""
    with transaction.atomic():
        locked = Booking.objects.select_for_update().get(pk=booking.pk)
        acceptance = BookingPolicyAcceptance.objects.create(
            booking=locked,
            checkout_session=checkout_session,
            customer_profile=locked.customer_profile,
            terms_version=documents.terms.version,
            privacy_version=documents.privacy.version,
            booking_policy_version=documents.booking_policy.version,
            cookie_notice_version=documents.cookie_notice.version if documents.cookie_notice else "",
            accepted_at=accepted_at,
            ip_hash_hmac=hash_sensitive_value(ip_source) if ip_source else "",
            user_agent_hash_hmac=hash_sensitive_value(user_agent_source) if user_agent_source else "",
            locale=_safe_meta(policy_acceptance.get("locale"), 16),
            timezone_name=_safe_meta(policy_acceptance.get("timezone_name"), 64),
            country_hint=_safe_meta(policy_acceptance.get("country_hint"), 8).upper(),
            acceptance_text_hash=hash_sensitive_value(POLICY_ACCEPTANCE_TEXT),
        )
        locked.no_refund_policy_accepted_at = accepted_at
        locked.privacy_policy_accepted_at = accepted_at
        locked.terms_version = documents.terms.version
        locked.privacy_version = documents.privacy.version
        locked.save(
            update_fields=[
                "no_refund_policy_accepted_at",
                "privacy_policy_accepted_at",
                "terms_version",
                "privacy_version",
                "updated_at",
            ]
        )
        return acceptance
