from bookings.services.gallery_storage import GalleryObjectStorage, build_quarantine_key, public_variant_url


def test_gallery_storage_abstraction_uses_private_quarantine_and_public_variants(tmp_path, settings):
    settings.GALLERY_STORAGE_ROOT = str(tmp_path)
    settings.GALLERY_PUBLIC_BASE_URL = "/media/"
    storage = GalleryObjectStorage()
    key = build_quarantine_key("batch", "image", "client.jpg")
    storage.put(key, b"image")

    assert storage.exists(key)
    assert key.startswith("gallery/quarantine/")
    assert "client.jpg" not in key
    url = public_variant_url("gallery/variants/image/mobile.webp")
    assert url.startswith("/media/public/")
    assert url.endswith(".webp")
    assert "gallery/variants/image/mobile.webp" not in url
