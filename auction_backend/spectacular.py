from decouple import config

SPECTACULAR_SETTINGS = {
    "TITLE": "iBiSAP APIs",
    "DESCRIPTION": "iBiSAP Backend API Documentation",
    "VERSION": "1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": [
        (
            "rest_framework.permissions.IsAuthenticated"
            if config("DEBUG", cast=bool, default=False)
            else "ibisap_backend.custom_permissions.IsAdminOrSuperUser"
        )
    ],
    "SCHEMA_PATH_PREFIX_TRIM": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    # 'SCHEMA_PATH_PREFIX': None,
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "operationsSorter": "method",
        "tagsSorter": "alpha",
        # "tagsSorter": "(a, b) => a.localeCompare(b)",
        "supportedSubmitMethods": [
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
        ],
        "docExpansion": "none",
        "apisSorter": "alpha",
        "showRequestHeaders": False,
        "filter": True,  # Enable filtering
        "deepLinking": True,
        "requestContentType": "multipart/form-data",
        "displayRequestDuration": True,
        "showExtensions": True,
        # "displayOperationId": True,
    },
}

SIDECAR_CONFIGS = {
    # If no internet, use sidecar for doc rendering from cache
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

if not config("SERVER_ENV", cast=bool, default=False):
    SPECTACULAR_SETTINGS.update(SIDECAR_CONFIGS)
