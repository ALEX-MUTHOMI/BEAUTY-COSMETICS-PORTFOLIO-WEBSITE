import pytest

from bookings.services.legal import render_public_legal_document


def test_legal_markdown_sanitizer_strips_script_and_unsafe_links():
    markdown = """
# Policy
<script>alert('xss')</script>
[bad](javascript:alert(1))
[data](data:text/html;base64,PHNjcmlwdD5hPC9zY3JpcHQ+)
<img src=x onerror=alert(1)>
[safe](https://example.test/policy)
"""

    rendered = render_public_legal_document(markdown)

    assert "<script" not in rendered.lower()
    assert "javascript:" not in rendered.lower()
    assert "data:" not in rendered.lower()
    assert "onerror" not in rendered.lower()
    assert "https://example.test/policy" in rendered


@pytest.mark.django_db
def test_public_api_returns_sanitized_html(client):
    from bookings.models import LegalDocument

    LegalDocument.objects.create(
        document_type=LegalDocument.DocumentType.TERMS,
        version="xss",
        title="Terms",
        slug="terms-xss",
        status=LegalDocument.Status.ACTIVE,
        content_markdown="<script>alert(1)</script>[x](javascript:alert(1))",
    )

    response = client.get("/api/legal/documents/terms_of_service/", secure=True)

    assert response.status_code == 200
    payload = response.json()
    assert "<script" not in payload["content_html"].lower()
    assert "javascript:" not in payload["content_html"].lower()
