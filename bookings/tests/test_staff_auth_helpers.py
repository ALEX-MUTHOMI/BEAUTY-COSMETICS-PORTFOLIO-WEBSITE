from django.contrib.auth import get_user_model

User = get_user_model()


def make_staff(email="staff-auth@example.com", password="Correct horse battery staple 2026"):
    return User.objects.create_user(
        email=email,
        password=password,
        phone_number="+254700000111",
        is_staff=True,
    )


def make_customer(email="staff-auth-customer@example.com", password="Correct horse battery staple 2026"):
    return User.objects.create_user(
        email=email,
        password=password,
        phone_number="+254700000112",
    )


def login_payload(email="staff-auth@example.com", password="Correct horse battery staple 2026"):
    return {"email": email, "password": password}
