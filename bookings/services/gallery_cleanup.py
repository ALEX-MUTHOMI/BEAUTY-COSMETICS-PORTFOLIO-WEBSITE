from django.utils import timezone

from bookings.models import GalleryImage
from bookings.services.gallery_storage import GalleryObjectStorage


def cleanup_gallery_quarantine(limit=100):
    storage = GalleryObjectStorage()
    deleted = 0
    queryset = GalleryImage.objects.filter(
        delete_after__lte=timezone.now(),
        quarantine_key__gt="",
        status__in=[GalleryImage.Status.FAILED, GalleryImage.Status.REJECTED, GalleryImage.Status.DELETE_PENDING],
    ).order_by("delete_after")[:limit]
    for image in queryset:
        key = image.quarantine_key
        storage.delete(key)
        image.quarantine_key = ""
        image.save(update_fields=["quarantine_key", "updated_at"])
        deleted += 1
    return {"deleted": deleted}
