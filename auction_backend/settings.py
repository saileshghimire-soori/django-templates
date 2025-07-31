from .settings_config import *
from .simplejwt import *

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "django_user_agents",
    "rest_framework_simplejwt.token_blacklist",
    "mptt",
    "debug_toolbar",
]

if not SERVER_ENV:
    SIDE_CAR_APPS = [
        "drf_spectacular_sidecar",
    ]

    THIRD_PARTY_APPS.extend(SIDE_CAR_APPS)

LOCAL_APPS = ["apps.api_logs", "apps.base", "apps.core_app", "apps.authentication"]
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
INSTALLED_APPS += THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
    "apps.core_app.middleware.CustomErrorMiddleware",
    # "apps.api_logs.middleware.ApiLog",
]

ROOT_URLCONF = "auction_backend.urls"  # changed for every project

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "auction_backend.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
# TIME_ZONE= "" # Set to your desired timezone, e.g., "Asia/Kathmandu"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AUTH_USER_MODEL="" # name of user model, e.g "apps.base.models.User"

if DEBUG and not SERVER_ENV:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "apps.core_app.middleware.NonHtmlDebugToolbarMiddleware",
    ]
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": True,
        "PRETTIFY_SQL": True,
        "ROOT_TAG_EXTRA_ATTRS": "data-turbo-permanent",
        # "SHOW_TOOLBAR_CALLBACK": True,
        "IS_RUNNING_TESTS": False,
    }


# if you want to use Redis for caching, uncomment the following lines and configure accordingly

# REDIS_PROTOCOL = config("REDIS_PROTOCOL", default="redis")
# REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
# REDIS_PORT = config("REDIS_PORT", default="6379")
# REDIS_DB = config("REDIS_DB", default="1")

# REDIS_URI = f"{REDIS_PROTOCOL}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URI,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             # redis doesnt throw error if redis is down instead,gives NONE as values
#             "IGNORE_EXCEPTIONS": True,
#             "CONNECTION_POOL_KWARGS": {
#                 "max_connections": 100,
#                 "retry_on_timeout": True,
#             },
#         },
#     }
# }

CORS_ALLOW_ALL_ORIGINS = True
