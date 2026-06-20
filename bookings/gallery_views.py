from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Prefetch
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from bookings.gallery.selectors.public_gallery import (
    get_homepage_gallery,
    get_public_category_gallery,
    get_public_service_gallery,
    get_public_subcategory_gallery,
)
from bookings.models import GalleryCategory, GalleryImage, GalleryImageVariant, GallerySubcategory
from bookings.services.gallery_images import create_gallery_image_from_upload
from bookings.services.gallery_storage import GalleryObjectStorage, GalleryStorageError, public_variant_extension
from bookings.services.staff_auth import GENERIC_SESSION_EXPIRED, enforce_staff_session


def _json(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _staff_forbidden():
    return _json({"detail": "Staff gallery is unavailable."}, status=403)


def _safe_validation(status=400):
    return _json({"detail": "Gallery request could not be accepted."}, status=status)


def _media_content_type(extension):
    return {"webp": "image/webp", "jpeg": "image/jpeg", "jpg": "image/jpeg", "png": "image/png"}[extension]


def _require_staff(request):
    if not getattr(request.user, "is_authenticated", False) or not getattr(request.user, "is_staff", False):
        return _staff_forbidden()
    if not enforce_staff_session(request):
        return _json({"detail": GENERIC_SESSION_EXPIRED}, status=403)
    return None


@require_GET
def staff_gallery_categories(request):
    denied = _require_staff(request)
    if denied:
        return denied
    categories = (
        GalleryCategory.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=GallerySubcategory.objects.filter(is_active=True).order_by("sort_order", "name"),
            )
        )
        .order_by("sort_order", "name")
    )
    return _json(
        {
            "categories": [
                {
                    "public_id": str(category.public_id),
                    "name": category.name,
                    "slug": category.slug,
                    "is_sensitive_default": category.is_sensitive_default,
                    "subcategories": [
                        {
                            "public_id": str(sub.public_id),
                            "name": sub.name,
                            "slug": sub.slug,
                            "sensitivity_default": sub.sensitivity_default,
                            "requires_warning_default": sub.requires_warning_default,
                        }
                        for sub in category.subcategories.all()
                    ],
                }
                for category in categories
            ]
        }
    )


@require_POST
def staff_gallery_image_upload(request):
    denied = _require_staff(request)
    if denied:
        return denied
    upload = request.FILES.get("image")
    if upload is None:
        return _safe_validation()
    try:
        image = create_gallery_image_from_upload(
            staff_user=request.user,
            category_public_id=request.POST.get("category_public_id", ""),
            subcategory_public_id=request.POST.get("subcategory_public_id") or None,
            title=request.POST.get("title", ""),
            upload=upload,
        )
    except GalleryCategory.DoesNotExist:
        return _safe_validation()
    except ValidationError as exc:
        message = str(exc).lower()
        if "cap" in message:
            return _safe_validation(status=429)
        if "duplicate" in message:
            return _safe_validation(status=409)
        return _safe_validation()
    return _json(
        {
            "image": {
                "public_id": str(image.public_id),
                "status": image.status,
                "title": image.title,
                "category": image.category.slug,
            }
        },
        status=202,
    )


@require_GET
def public_gallery_homepage(request):
    return _json(get_homepage_gallery())


@require_GET
def public_gallery_category(request, category_slug):
    try:
        return _json(get_public_category_gallery(category_slug))
    except ObjectDoesNotExist:
        return _json({"detail": "Gallery category is unavailable."}, status=404)


@require_GET
def public_gallery_service(request, service_slug):
    try:
        return _json(get_public_service_gallery(service_slug))
    except ObjectDoesNotExist:
        return _json({"detail": "Gallery category is unavailable."}, status=404)


@require_GET
def public_gallery_subcategory(request, category_slug, subcategory_slug):
    try:
        return _json(get_public_subcategory_gallery(category_slug, subcategory_slug))
    except ObjectDoesNotExist:
        return _json({"detail": "Gallery category is unavailable."}, status=404)


@require_GET
def public_gallery_variant(request, public_handle, extension):
    try:
        normalized_extension = public_variant_extension(extension)
    except GalleryStorageError as exc:
        raise Http404 from exc

    variant = (
        GalleryImageVariant.objects.select_related("gallery_image")
        .filter(
            public_id=public_handle,
            is_public=True,
            gallery_image__status=GalleryImage.Status.PUBLISHED,
        )
        .first()
    )
    if variant is None:
        raise Http404
    try:
        expected_extension = public_variant_extension(variant.format)
    except GalleryStorageError as exc:
        raise Http404 from exc
    if expected_extension != normalized_extension:
        raise Http404

    try:
        file_handle = GalleryObjectStorage().open(variant.storage_key)
    except GalleryStorageError as exc:
        raise Http404 from exc

    response = FileResponse(file_handle, content_type=_media_content_type(normalized_extension))
    # Archived media must become unavailable promptly; do not make a revocable
    # public variant immutable in browser/CDN caches.
    response["Cache-Control"] = "public, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = "inline"
    return response
