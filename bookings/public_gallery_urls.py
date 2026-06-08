from django.urls import path

from bookings import gallery_views

urlpatterns = [
    path("homepage/", gallery_views.public_gallery_homepage, name="public-gallery-homepage"),
    path("categories/<slug:category_slug>/", gallery_views.public_gallery_category, name="public-gallery-category"),
    path("services/<slug:service_slug>/", gallery_views.public_gallery_service, name="public-gallery-service"),
    path(
        "categories/<slug:category_slug>/<slug:subcategory_slug>/",
        gallery_views.public_gallery_subcategory,
        name="public-gallery-subcategory",
    ),
]
