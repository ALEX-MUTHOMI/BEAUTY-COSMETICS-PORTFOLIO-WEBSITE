import os
import uuid
from pathlib import Path

from django.conf import settings


class GalleryStorageError(Exception):
    pass


def _storage_root():
    return Path(getattr(settings, "GALLERY_STORAGE_ROOT", settings.BASE_DIR / "var" / "gallery-storage"))


def _safe_relative_key(key):
    key = str(key or "").replace("\\", "/").lstrip("/")
    if not key or ".." in key.split("/"):
        raise GalleryStorageError("Invalid gallery storage key.")
    return key


def build_quarantine_key(batch_public_id, image_public_id, _filename):
    return f"gallery/quarantine/{batch_public_id}/{image_public_id}/original"


def build_variant_key(image_public_id, variant_type):
    return f"gallery/variants/{image_public_id}/{variant_type}.webp"


PUBLIC_VARIANT_FORMATS = {"webp", "jpeg", "jpg", "png"}


def public_variant_extension(image_format):
    extension = str(image_format or "").lower().lstrip(".")
    if extension not in PUBLIC_VARIANT_FORMATS:
        raise GalleryStorageError("Invalid public gallery format.")
    return extension


def public_variant_url(variant_public_id, image_format):
    try:
        public_handle = uuid.UUID(str(variant_public_id))
    except (TypeError, ValueError, AttributeError) as exc:
        raise GalleryStorageError("Invalid public gallery handle.") from exc
    extension = public_variant_extension(image_format)
    base = getattr(settings, "GALLERY_PUBLIC_BASE_URL", "/media/").rstrip("/") + "/"
    return f"{base}public/{public_handle}.{extension}"


class GalleryObjectStorage:
    """
    Local object-storage adapter used by tests and lean deployments.
    Production can replace this boundary with R2/S3 without changing callers.
    """

    def _path(self, key):
        key = _safe_relative_key(key)
        root = _storage_root().resolve()
        path = (root / key).resolve()
        if root not in path.parents and path != root:
            raise GalleryStorageError("Invalid gallery storage path.")
        return path

    def put(self, key, content):
        path = self._path(key)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(content)
        except OSError as exc:
            raise GalleryStorageError("Gallery storage write failed.") from exc
        return key

    def get(self, key):
        try:
            with open(self._path(key), "rb") as handle:
                return handle.read()
        except OSError as exc:
            raise GalleryStorageError("Gallery storage read failed.") from exc

    def open(self, key):
        try:
            return open(self._path(key), "rb")
        except OSError as exc:
            raise GalleryStorageError("Gallery storage read failed.") from exc

    def exists(self, key):
        return self._path(key).exists()

    def delete(self, key):
        try:
            os.remove(self._path(key))
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise GalleryStorageError("Gallery storage delete failed.") from exc
        return True
