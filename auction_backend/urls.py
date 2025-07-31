from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from .patterns import apipatterns, authpattern, schemapatterns

urlpatterns = [
    path("admin/", admin.site.urls),  # disable this at production
    path("api/", include(apipatterns)),
    path("docs/", include(schemapatterns)),
    path("api-auth/", include("rest_framework.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]

if settings.DEBUG and not settings.SERVER_ENV:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
