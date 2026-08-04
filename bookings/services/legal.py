import html
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
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
GENERIC_LEGAL_NOT_FOUND = "Legal document is unavailable."
LEGAL_DOCS_DIR = Path(settings.BASE_DIR) / "docs" / "legal"
LEGAL_FRONTEND_ROUTES = {
    LegalDocument.DocumentType.TERMS: "/terms-of-service",
    LegalDocument.DocumentType.PRIVACY: "/privacy-policy",
    LegalDocument.DocumentType.BOOKING_POLICY: "/booking-policy",
    LegalDocument.DocumentType.COOKIE_NOTICE: "/cookie-notice",
    LegalDocument.DocumentType.DATA_RETENTION: "/data-retention-policy",
}
LEGAL_SOURCE_FILES = {
    LegalDocument.DocumentType.TERMS: "TERMS_OF_SERVICE.md",
    LegalDocument.DocumentType.PRIVACY: "PRIVACY_POLICY.md",
    LegalDocument.DocumentType.BOOKING_POLICY: "BOOKING_CANCELLATION_RESCHEDULE_POLICY.md",
    LegalDocument.DocumentType.COOKIE_NOTICE: "COOKIE_NOTICE.md",
    LegalDocument.DocumentType.DATA_RETENTION: "DATA_RETENTION_POLICY.md",
}
LEGAL_PUBLIC_REVIEW_STATUS = {
    LegalDocument.LegalReviewStatus.PENDING: "business_approved_pending_legal_review",
    LegalDocument.LegalReviewStatus.REVIEWED: "reviewed",
    LegalDocument.LegalReviewStatus.NOT_REQUIRED: "not_required",
}


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


def load_legal_markdown_source(filename):
    safe_name = Path(filename).name
    path = LEGAL_DOCS_DIR / safe_name
    if not path.exists():
        raise FileNotFoundError(f"Missing legal source file: {safe_name}")
    return path.read_text(encoding="utf-8")


def render_public_legal_document(markdown):
    escaped = html.escape(str(markdown or ""), quote=True)
    escaped = re.sub(r"(?i)\son[a-z]+\s*=\s*[^&\s]+", "", escaped)
    escaped = re.sub(r"(?im)^\# (.+)$", r"<h1>\1</h1>", escaped)
    escaped = re.sub(r"(?im)^\#\# (.+)$", r"<h2>\1</h2>", escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https://[^)\s]+)\)",
        r'<a href="\2" rel="noopener noreferrer">\1</a>',
        escaped,
    )
    escaped = re.sub(r"\[([^\]]+)\]\((?!https://)[^)]+\)", r"\1", escaped)
    paragraphs = [line for line in escaped.splitlines()]
    return "\n".join(f"<p>{line}</p>" if line and not line.startswith("<h") else line for line in paragraphs)


def activate_legal_document(document):
    with transaction.atomic():
        locked = LegalDocument.objects.select_for_update().get(pk=document.pk)
        LegalDocument.objects.select_for_update().filter(
            document_type=locked.document_type,
            status=LegalDocument.Status.ACTIVE,
        ).exclude(pk=locked.pk).update(
            status=LegalDocument.Status.ARCHIVED,
            is_active=False,
            archived_at=timezone.now(),
        )
        locked.status = LegalDocument.Status.ACTIVE
        locked.is_active = True
        if locked.published_at is None:
            locked.published_at = timezone.now()
        locked.save(
            update_fields=[
                "status",
                "is_active",
                "published_at",
                "content_hash",
                "updated_at",
            ]
        )
        return locked


def ensure_default_legal_documents():
    documents = []
    for document_type, (title, version, content, requires_acceptance) in DEFAULT_DOCUMENTS.items():
        document, _created = LegalDocument.objects.get_or_create(
            document_type=document_type,
            version=version,
            defaults={
                "title": title,
                "content_markdown": content,
                "status": LegalDocument.Status.ACTIVE,
                "is_active": True,
                "requires_acceptance": requires_acceptance,
                "effective_at": timezone.now(),
                "published_at": timezone.now(),
                "slug": document_type.replace("_", "-"),
            },
        )
        if document.status != LegalDocument.Status.ACTIVE or not document.is_active:
            document.status = LegalDocument.Status.ACTIVE
            document.is_active = True
            document.save(update_fields=["status", "is_active", "published_at", "content_hash", "updated_at"])
        documents.append(document)
    return documents


def get_active_required_documents():
    documents = {
        document.document_type: document
        for document in LegalDocument.objects.filter(
            document_type__in=[*REQUIRED_DOCUMENT_TYPES, *OPTIONAL_DOCUMENT_TYPES],
            status=LegalDocument.Status.ACTIVE,
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


def seed_legal_documents(*, activate=False, stdout=None):
    created = 0
    updated = 0
    activated = 0
    for document_type, filename in LEGAL_SOURCE_FILES.items():
        content = load_legal_markdown_source(filename)
        default_title = dict(LegalDocument.DocumentType.choices)[document_type]
        desired_status = LegalDocument.Status.ACTIVE if activate else LegalDocument.Status.BUSINESS_APPROVED
        document, was_created = LegalDocument.objects.get_or_create(
            document_type=document_type,
            version="v2026.06-draft",
            defaults={
                "title": default_title,
                "slug": document_type.replace("_", "-"),
                "content_markdown": content,
                "status": desired_status,
                "requires_acceptance": document_type in REQUIRED_DOCUMENT_TYPES,
                "effective_at": timezone.now(),
            },
        )
        if was_created:
            created += 1
        else:
            update_fields = []
            if document.content_markdown != content:
                document.content_markdown = content
                update_fields.append("content_markdown")
            if document.title != default_title:
                document.title = default_title
                update_fields.append("title")
            if document.requires_acceptance != (document_type in REQUIRED_DOCUMENT_TYPES):
                document.requires_acceptance = document_type in REQUIRED_DOCUMENT_TYPES
                update_fields.append("requires_acceptance")
            if update_fields:
                document.save(update_fields=[*update_fields, "content_hash", "updated_at"])
                updated += 1
        if activate and document.status != LegalDocument.Status.ACTIVE:
            activate_legal_document(document)
            activated += 1
    if stdout:
        stdout.write(f"legal_documents created={created} updated={updated} activated={activated}")
    return {"created": created, "updated": updated, "activated": activated}


def public_legal_document_queryset():
    return LegalDocument.objects.filter(status=LegalDocument.Status.ACTIVE, is_active=True).order_by("document_type")


def get_public_legal_document(*, document_type, version=None):
    valid_types = set(LegalDocument.DocumentType.values)
    if document_type not in valid_types:
        raise Http404(GENERIC_LEGAL_NOT_FOUND)
    queryset = public_legal_document_queryset().filter(document_type=document_type)
    if version is not None:
        queryset = queryset.filter(version=version)
    document = queryset.first()
    if document is None:
        raise Http404(GENERIC_LEGAL_NOT_FOUND)
    return document


def serialize_public_legal_document(document):
    return {
        "document_type": document.document_type,
        "version": document.version,
        "title": document.title,
        "slug": document.slug,
        "effective_at": document.effective_at.isoformat(),
        "published_at": document.published_at.isoformat() if document.published_at else None,
        "last_updated": document.updated_at.isoformat(),
        "content_markdown": document.content_markdown,
        "content_html": render_public_legal_document(document.content_markdown),
        "content_hash": document.content_hash,
        "requires_acceptance": document.requires_acceptance,
        "legal_review_status": LEGAL_PUBLIC_REVIEW_STATUS[document.legal_review_status],
        "frontend_path": LEGAL_FRONTEND_ROUTES.get(document.document_type, "/legal"),
    }


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
            terms_content_hash=documents.terms.content_hash,
            privacy_content_hash=documents.privacy.content_hash,
            booking_policy_content_hash=documents.booking_policy.content_hash,
            cookie_notice_content_hash=documents.cookie_notice.content_hash if documents.cookie_notice else "",
            accepted_at=accepted_at,
            ip_hash_hmac=hash_sensitive_value(ip_source) if ip_source else "",
            user_agent_hash_hmac=hash_sensitive_value(user_agent_source) if user_agent_source else "",
            locale=_safe_meta(policy_acceptance.get("locale"), 16),
            timezone_name=_safe_meta(policy_acceptance.get("timezone_name"), 64),
            country_hint=_safe_meta(policy_acceptance.get("country_hint"), 8).upper(),
            acceptance_text_hash=hash_sensitive_value(POLICY_ACCEPTANCE_TEXT),
            no_refund_ack_hash=hash_sensitive_value(NO_REFUND_NOTICE),
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
