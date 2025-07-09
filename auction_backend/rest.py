from decouple import config

DEBUG = config("DEBUG", cast=bool, default=False)
DISABLED_AUTHENTICATION = config("DISABLED_AUTHENTICATION", cast=bool, default=False)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "auction_backend.paginations.CustomPagePagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        []
        if DISABLED_AUTHENTICATION
        else [
            "rest_framework.permissions.IsAuthenticated",
        ]
    ),
    "DEFAULT_RENDERER_CLASSES": (
        (
            "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
            "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
        )
        if DEBUG
        else (
            "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
            "rest_framework.renderers.JSONRenderer",
        )
    ),
    "DEFAULT_PARSER_CLASSES": (
        "apps.base.parser.parser.CustomNestedParser",
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        # "rest_framework.throttling.ScopedRateThrottle",
        "apps.base.libs.throttling.CustomScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "superuser": "150/second",  # superuser can have access to everything
        "public_get": "5/second",  # public users can have limited number of requests
        "public_post": "2/min",
        "public_patch": "2/min",
        "public_delete": "1/min",
        "auth_get": "10/second",  # authenticated users can have higher number of requests than public
        "auth_post": "5/second",
        "auth_patch": "5/second",
        "auth_delete": "5/second",
    },
    "EXCEPTION_HANDLER": "apps.core_app.exception_handlers.custom_exception_handler",
}
