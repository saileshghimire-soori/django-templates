from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.base.api_urls.v1.urls")),
]
