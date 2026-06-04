from django.urls import path

from bookings.legal_views import legal_document_detail, legal_document_list, legal_document_version

urlpatterns = [
    path("documents/", legal_document_list, name="legal-document-list"),
    path("documents/<str:document_type>/", legal_document_detail, name="legal-document-detail"),
    path("documents/<str:document_type>/<str:version>/", legal_document_version, name="legal-document-version"),
]
