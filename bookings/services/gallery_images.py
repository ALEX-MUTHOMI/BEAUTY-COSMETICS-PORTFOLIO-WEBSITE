import hashlib
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from billing.redaction import hash_sensitive_value
from bookings.models import GalleryAuditLog, GalleryCategory, GalleryImage, GalleryImageVariant, GalleryUploadBatch
from bookings.services.gallery_storage import (
    GalleryObjectStorage,
    GalleryStorageError,
    build_quarantine_key,
    build_variant_key,
)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
VARIANT_WIDTHS = {
    GalleryImageVariant.VariantType.THUMBNAIL: 320,
    GalleryImageVariant.VariantType.MOBILE: 640,
    GalleryImageVariant.VariantType.TABLET: 960,
    GalleryImageVariant.VariantType.DESKTOP: 1280,
    GalleryImageVariant.VariantType.HERO: 1600,
}


def audit_gallery_event(
    event_type,
    *,
    staff_user=None,
    gallery_image=None,
    upload_batch=None,
    metadata=None,
    ip_address="",
    user_agent="",
):
    return GalleryAuditLog.objects.create(
        staff_user=staff_user,
        gallery_image=gallery_image,
        upload_batch=upload_batch,
        event_type=event_type,
        metadata_redacted=metadata or {},
        ip_hash_hmac=hash_sensitive_value(ip_address) if ip_address else "",
        user_agent_hash_hmac=hash_sensitive_value(user_agent) if user_agent else "",
    )


def classify_source_profile(*, file_size, width, height, exif_make="", exif_software=""):
    make = (exif_make or "").lower()
    software = (exif_software or "").lower()
    megapixels = (int(width or 0) * int(height or 0)) / 1_000_000
    if (
        any(vendor in make for vendor in ["canon", "nikon", "sony", "fujifilm", "panasonic", "olympus"])
        or megapixels >= 30
    ):
        return GalleryImage.SourceProfile.HIGH_RES_CAMERA
    if any(vendor in make for vendor in ["apple", "samsung", "xiaomi", "oppo", "android"]) and megapixels <= 20:
        return GalleryImage.SourceProfile.PHONE_STANDARD
    if any(tool in software for tool in ["lightroom", "photoshop", "snapseed", "canva"]):
        return GalleryImage.SourceProfile.EDITED_EXPORT
    if "instagram" in software or (file_size < 150_000 and width <= 1200 and height <= 1200):
        return GalleryImage.SourceProfile.COMPRESSED_SOCIAL
    return GalleryImage.SourceProfile.UNKNOWN


def _setting_int(name, default):
    return int(getattr(settings, name, default))


def _extension(filename):
    return str(filename or "").rsplit(".", 1)[-1].lower() if "." in str(filename or "") else ""


def validate_gallery_upload(upload):
    filename = getattr(upload, "name", "")
    content_type = getattr(upload, "content_type", "")
    size = int(getattr(upload, "size", 0) or 0)
    if _extension(filename) not in ALLOWED_EXTENSIONS:
        raise ValidationError("Gallery image format is not allowed.")
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Gallery image type is not allowed.")
    if size <= 0 or size > _setting_int("GALLERY_MAX_HIGH_RES_IMAGE_BYTES", 26_214_400):
        raise ValidationError("Gallery image size is not allowed.")
    content = upload.read()
    upload.seek(0)
    if content.startswith((b"<svg", b"<html", b"PK\x03\x04")) or b"<script" in content[:512].lower():
        raise ValidationError("Gallery image content is not allowed.")
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
        with Image.open(BytesIO(content)) as image:
            width, height = image.size
            if width * height > _setting_int("GALLERY_MAX_IMAGE_PIXELS", 50_000_000):
                raise ValidationError("Gallery image dimensions are not allowed.")
            if image.format.lower() not in {"jpeg", "png", "webp"}:
                raise ValidationError("Gallery image format is not allowed.")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValidationError("Gallery image failed validation.") from exc
    return content


def enforce_gallery_caps(*, staff_user, desired_status=None):
    if desired_status == GalleryImage.Status.PUBLISHED:
        if GalleryImage.objects.filter(status=GalleryImage.Status.PUBLISHED).count() >= _setting_int(
            "GALLERY_MAX_PUBLISHED_IMAGES", 80
        ):
            raise ValidationError("Gallery published image cap reached.")
    if desired_status == GalleryImage.Status.DRAFT:
        if GalleryImage.objects.filter(status=GalleryImage.Status.DRAFT).count() >= _setting_int(
            "GALLERY_MAX_DRAFT_IMAGES", 100
        ):
            raise ValidationError("Gallery draft image cap reached.")
    if desired_status is None:
        today_count = GalleryImage.objects.filter(
            uploaded_by=staff_user, created_at__date=timezone.now().date()
        ).count()
        if today_count >= _setting_int("GALLERY_MAX_DAILY_UPLOADS", 30):
            raise ValidationError("Gallery daily upload cap reached.")


def create_gallery_image_from_upload(*, staff_user, category_public_id, upload, title="", subcategory_public_id=None):
    enforce_gallery_caps(staff_user=staff_user)
    content = validate_gallery_upload(upload)
    category = GalleryCategory.objects.get(public_id=category_public_id, is_active=True)
    subcategory = None
    if subcategory_public_id:
        subcategory = category.subcategories.get(public_id=subcategory_public_id, is_active=True)

    batch = GalleryUploadBatch.objects.create(staff_user=staff_user, image_count=1, total_size_bytes=len(content))
    sensitivity = (
        subcategory.sensitivity_default
        if subcategory
        else (GalleryImage.Sensitivity.SENSITIVE if category.is_sensitive_default else GalleryImage.Sensitivity.NORMAL)
    )
    requires_warning = bool(category.is_sensitive_default or (subcategory and subcategory.requires_warning_default))
    image = GalleryImage.objects.create(
        upload_batch=batch,
        category=category,
        subcategory=subcategory,
        uploaded_by=staff_user,
        title=str(title or "")[:120],
        status=GalleryImage.Status.QUARANTINED,
        sensitivity_level=sensitivity,
        requires_warning=requires_warning,
    )
    key = build_quarantine_key(str(batch.public_id), str(image.public_id), getattr(upload, "name", ""))
    try:
        GalleryObjectStorage().put(key, content)
    except GalleryStorageError as exc:
        image.status = GalleryImage.Status.FAILED
        image.processing_error_code = "storage_write_failed"
        image.save(update_fields=["status", "processing_error_code", "updated_at"])
        raise ValidationError("Gallery storage is unavailable.") from exc
    image.quarantine_key = key
    image.save(update_fields=["quarantine_key", "updated_at"])
    audit_gallery_event(
        GalleryAuditLog.EventType.UPLOADED_TO_QUARANTINE, staff_user=staff_user, gallery_image=image, upload_batch=batch
    )
    transaction.on_commit(lambda: _enqueue_gallery_processing(str(image.public_id)))
    return image


def _enqueue_gallery_processing(image_public_id):
    from bookings.tasks import process_gallery_image

    process_gallery_image.delay(image_public_id)


def process_gallery_image_now(image_public_id):
    storage = GalleryObjectStorage()
    image = GalleryImage.objects.get(public_id=image_public_id)
    image.status = GalleryImage.Status.PROCESSING
    image.processing_error_code = ""
    image.save(update_fields=["status", "processing_error_code", "updated_at"])
    audit_gallery_event(GalleryAuditLog.EventType.PROCESSING_STARTED, staff_user=image.uploaded_by, gallery_image=image)
    try:
        content = storage.get(image.quarantine_key)
    except GalleryStorageError as exc:
        image.status = GalleryImage.Status.FAILED
        image.processing_error_code = "storage_missing"
        image.save(update_fields=["status", "processing_error_code", "updated_at"])
        audit_gallery_event(
            GalleryAuditLog.EventType.STORAGE_FAILURE, staff_user=image.uploaded_by, gallery_image=image
        )
        raise ValidationError("Gallery storage object is unavailable.") from exc

    try:
        with Image.open(BytesIO(content)) as source:
            exif = source.getexif()
            exif_make = str(exif.get(271, "") if exif else "")
            exif_software = str(exif.get(305, "") if exif else "")
            source = ImageOps.exif_transpose(source).convert("RGB")
            image.source_profile = classify_source_profile(
                file_size=len(content),
                width=source.width,
                height=source.height,
                exif_make=exif_make,
                exif_software=exif_software,
            )
            GalleryImageVariant.objects.filter(gallery_image=image).delete()
            for variant_type, width in VARIANT_WIDTHS.items():
                resized = source.copy()
                if resized.width > width:
                    ratio = width / resized.width
                    resized = resized.resize((width, max(1, int(resized.height * ratio))), Image.Resampling.LANCZOS)
                buffer = BytesIO()
                resized.save(buffer, format="WEBP", quality=84, method=4)
                data = buffer.getvalue()
                key = build_variant_key(str(image.public_id), variant_type)
                storage.put(key, data)
                GalleryImageVariant.objects.create(
                    gallery_image=image,
                    variant_type=variant_type,
                    storage_key=key,
                    width=resized.width,
                    height=resized.height,
                    format="webp",
                    size_bytes=len(data),
                    sha256_hash=hashlib.sha256(data).hexdigest(),
                    is_public=True,
                )
    except Exception as exc:
        image.status = GalleryImage.Status.FAILED
        image.processing_error_code = "processing_failed"
        image.save(update_fields=["status", "processing_error_code", "updated_at"])
        audit_gallery_event(
            GalleryAuditLog.EventType.PROCESSING_FAILED, staff_user=image.uploaded_by, gallery_image=image
        )
        raise ValidationError("Gallery processing failed.") from exc

    image.original_private_key = f"gallery/originals-private/{image.public_id}/original"
    image.status = GalleryImage.Status.READY
    image.save(update_fields=["original_private_key", "source_profile", "status", "updated_at"])
    audit_gallery_event(
        GalleryAuditLog.EventType.PROCESSING_SUCCEEDED, staff_user=image.uploaded_by, gallery_image=image
    )
    return image


def publish_gallery_image(image, *, staff_user):
    if image.status != GalleryImage.Status.READY:
        raise ValidationError("Gallery image is not ready to publish.")
    enforce_gallery_caps(staff_user=staff_user, desired_status=GalleryImage.Status.PUBLISHED)
    if image.sensitivity_level in {GalleryImage.Sensitivity.SENSITIVE, GalleryImage.Sensitivity.RESTRICTED}:
        if not image.requires_warning or not image.sensitive_publish_confirmed:
            raise ValidationError("Sensitive gallery image requires explicit warning confirmation.")
        if image.show_on_homepage:
            raise ValidationError("Sensitive gallery image cannot be homepage featured by default.")
    if image.is_identifiable and image.consent_status != GalleryImage.ConsentStatus.CONFIRMED:
        raise ValidationError("Identifiable gallery image requires confirmed consent.")
    image.status = GalleryImage.Status.PUBLISHED
    image.published_at = timezone.now()
    image.save(update_fields=["status", "published_at", "updated_at"])
    audit_gallery_event(GalleryAuditLog.EventType.PUBLISHED, staff_user=staff_user, gallery_image=image)
    return image


def archive_gallery_image(image, *, staff_user):
    image.status = GalleryImage.Status.ARCHIVED
    image.archived_at = timezone.now()
    image.save(update_fields=["status", "archived_at", "updated_at"])
    audit_gallery_event(GalleryAuditLog.EventType.ARCHIVED, staff_user=staff_user, gallery_image=image)
    return image
