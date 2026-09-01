from html import escape

from django.conf import settings

from bookings.models import GalleryCategory, GalleryImage
from bookings.privacy import neutralize_script_payload, strip_markup
from bookings.services.gallery_storage import public_variant_url


def _safe_text(value, max_length=500):
    text = neutralize_script_payload(strip_markup(value, max_length=max_length))
    return escape(text, quote=True)


def image_public_payload(image):
    variants = {}
    for variant in image.variants.filter(is_public=True).order_by("variant_type"):
        variants[variant.variant_type] = {
            "url": public_variant_url(variant.public_id, variant.format),
            "width": variant.width,
            "height": variant.height,
            "format": variant.format,
            "size_bytes": variant.size_bytes,
        }
    return {
        "public_id": str(image.public_id),
        "title": _safe_text(image.title, 120),
        "description": _safe_text(image.description, 500),
        "category": {"slug": image.category.slug, "name": _safe_text(image.category.name, 96)},
        "subcategory": (
            {"slug": image.subcategory.slug, "name": _safe_text(image.subcategory.name, 96)}
            if image.subcategory_id
            else None
        ),
        "sensitivity_level": image.sensitivity_level,
        "requires_warning": image.requires_warning,
        "variants": variants,
    }


def _published_queryset():
    return (
        GalleryImage.objects.filter(
            status=GalleryImage.Status.PUBLISHED,
            category__is_active=True,
            variants__is_public=True,
        )
        .exclude(category__slug__startswith="api-acceptance")
        .select_related("category", "subcategory")
        .prefetch_related("variants")
        .distinct()
        .order_by("-is_featured", "sort_order", "-published_at", "-created_at")
    )


def get_homepage_gallery():
    limit = int(getattr(settings, "GALLERY_HOMEPAGE_FEATURED_LIMIT", 12))
    queryset = (
        _published_queryset()
        .filter(show_on_homepage=True)
        .exclude(sensitivity_level__in=[GalleryImage.Sensitivity.SENSITIVE, GalleryImage.Sensitivity.RESTRICTED])[
            :limit
        ]
    )
    return {"images": [image_public_payload(image) for image in queryset]}


def get_public_category_gallery(category_slug):
    limit = int(getattr(settings, "GALLERY_PUBLIC_CATEGORY_LIMIT", 18))
    category = GalleryCategory.objects.get(slug=category_slug, is_active=True)
    queryset = _published_queryset().filter(category=category)[:limit]
    return {
        "category": {
            "slug": category.slug,
            "name": _safe_text(category.name, 96),
            "requires_warning": category.is_sensitive_default,
        },
        "images": [image_public_payload(image) for image in queryset],
    }


def get_public_service_gallery(service_slug):
    payload = get_public_category_gallery(service_slug)
    payload["service"] = {
        "slug": payload["category"]["slug"],
        "name": payload["category"]["name"],
        "requires_warning": payload["category"]["requires_warning"],
    }
    return payload


def get_public_subcategory_gallery(category_slug, subcategory_slug):
    limit = int(getattr(settings, "GALLERY_PUBLIC_SUBCATEGORY_LIMIT", 10))
    category = GalleryCategory.objects.get(slug=category_slug, is_active=True)
    queryset = _published_queryset().filter(category=category, subcategory__slug=subcategory_slug)[:limit]
    return {
        "category": {"slug": category.slug, "name": _safe_text(category.name, 96)},
        "images": [image_public_payload(image) for image in queryset],
    }
