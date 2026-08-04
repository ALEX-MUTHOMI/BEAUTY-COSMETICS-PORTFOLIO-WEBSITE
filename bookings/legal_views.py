from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET

from bookings.services.legal import (
    get_public_legal_document,
    public_legal_document_queryset,
    serialize_public_legal_document,
)


def _not_found(_request, _exception=None):
    return JsonResponse({"detail": "Legal document is unavailable."}, status=404)


@require_GET
def legal_document_list(_request):
    documents = [serialize_public_legal_document(document) for document in public_legal_document_queryset()]
    response = JsonResponse({"results": documents})
    response["Cache-Control"] = "public, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@require_GET
def legal_document_detail(_request, document_type):
    try:
        document = get_public_legal_document(document_type=document_type)
    except Http404:
        return _not_found(_request)
    response = JsonResponse(serialize_public_legal_document(document))
    response["Cache-Control"] = "public, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@require_GET
def legal_document_version(_request, document_type, version):
    try:
        document = get_public_legal_document(document_type=document_type, version=version)
    except Http404:
        return _not_found(_request)
    response = JsonResponse(serialize_public_legal_document(document))
    response["Cache-Control"] = "public, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    return response
