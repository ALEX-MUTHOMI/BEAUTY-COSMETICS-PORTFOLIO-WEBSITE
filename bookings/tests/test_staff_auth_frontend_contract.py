from pathlib import Path

import pytest
from django.test import Client


@pytest.mark.django_db
def test_staff_auth_contract_routes_exist_and_do_not_issue_bearer_tokens():
    response = Client().post(
        "/api/staff/auth/login/",
        {"email": "missing@example.com", "password": "not the password"},
        content_type="application/json",
        secure=True,
    )

    assert response.status_code in {400, 429}
    assert "token" not in response.content.decode().lower()
    assert "session" not in response.content.decode().lower()


def test_staff_frontend_contract_does_not_store_staff_tokens_in_browser_storage():
    source = Path("frontend/src/staff/staffAuth.ts").read_text()

    assert "credentials: 'include'" in source
    assert ".setItem(" not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
