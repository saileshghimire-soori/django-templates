from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

apipatterns = [
    path("", include("apps.base.urls")),
]

authpattern = [path("", include("apps.authentication.urls"))]
