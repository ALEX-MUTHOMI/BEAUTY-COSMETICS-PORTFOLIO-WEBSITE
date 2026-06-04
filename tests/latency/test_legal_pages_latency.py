import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bookings.services.legal import ensure_default_legal_documents


@pytest.mark.django_db
@pytest.mark.latency
def test_legal_documents_list_is_query_bounded(client):
    ensure_default_legal_documents()

    with CaptureQueriesContext(connection) as captured:
        response = client.get("/api/legal/documents/", secure=True)

    assert response.status_code == 200
    assert len(captured) <= 3
