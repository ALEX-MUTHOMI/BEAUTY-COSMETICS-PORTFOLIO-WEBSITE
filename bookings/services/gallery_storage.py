# Compatibility wrapper. Canonical implementation lives in bookings.infrastructure.gallery_storage.
# New code should import from bookings.infrastructure.gallery_storage.
from bookings.infrastructure.gallery_storage import *  # noqa: F401,F403
from bookings.infrastructure.gallery_storage import (  # noqa: F811
    GalleryObjectStorage,
    GalleryStorageError,
    build_quarantine_key,
    build_variant_key,
    public_variant_url,
)

__all__ = [
    "GalleryObjectStorage",
    "GalleryStorageError",
    "build_quarantine_key",
    "build_variant_key",
    "public_variant_url",
]
