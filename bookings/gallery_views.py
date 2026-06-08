from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from bookings.models import GalleryCategory
from bookings.services.gallery_images import create_gallery_image_from_upload
from bookings.services.gallery_public import (
    get_homepage_gallery,
    get_public_category_gallery,
    get_public_subcategory_gallery,
)
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
        GalleryCategory.objects.filter(is_active=True).prefetch_related("subcategories").order_by("sort_order", "name")
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
                        for sub in category.subcategories.filter(is_active=True).order_by("sort_order", "name")
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
def public_gallery_subcategory(request, category_slug, subcategory_slug):
    try:
        return _json(get_public_subcategory_gallery(category_slug, subcategory_slug))
    except ObjectDoesNotExist:
        return _json({"detail": "Gallery category is unavailable."}, status=404)
