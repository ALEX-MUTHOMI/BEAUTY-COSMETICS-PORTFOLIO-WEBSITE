from io import BytesIO

from PIL import Image


def make_test_image_bytes(*, fmt="JPEG", size=(1200, 900), color=(210, 120, 90)):
    buffer = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def make_staff_session(client, staff_user):
    client.force_login(staff_user)
    session = client.session
    session["staff_auth_at"] = 1893456000
    session["staff_last_activity_at"] = 1893456000
    session.save()
    return client
