import os
import shutil

from decouple import config

from .conf import *

SECRET_KEY = config("SECRET_KEY", cast=str)

DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")], default="*"
)

APPEND_SLASH = False


CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default=f"http://localhost:{config("BACKEND_EXPOSE_PORT")}",
    # default=f"http://localhost:{config("NGINX_EXPOSE_PORT")}, http://localhost:{config("BACKEND_EXPOSE_PORT")}",
)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default=f"http://localhost:{config("BACKEND_EXPOSE_PORT")}",
    # default=f"http://localhost:{config("NGINX_EXPOSE_PORT")}, http://localhost:{config("BACKEND_EXPOSE_PORT")}",
)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default=f"http://localhost:8000",
)


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
if not os.path.exists(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


DECIMAL_PLACES = config("DECIMAL_PLACES", cast=int, default=4)
MAX_DIGITS = config("MAX_DIGITS", cast=int, default=12)
MAX_DECIMAL_DIGITS = config("MAX_DECIMAL_DIGITS", cast=int, default=16)

## File and Image size for validators
FILE_MAX_UPLOAD_SIZE = config("FILE_MAX_UPLOAD_SIZE", cast=int, default=2) * 1024 * 1024
IMAGE_MAX_UPLOAD_SIZE = (
    config("IMAGE_MAX_UPLOAD_SIZE", cast=int, default=2) * 1024 * 1024
)

FILE_HELP_TEXT_SIZE = f"{config("FILE_MAX_UPLOAD_SIZE", cast=int, default=2)}"
IMAGE_HELP_TEXT_SIZE = f"{config("IMAGE_MAX_UPLOAD_SIZE", cast=int, default=2)}"
## File and Image size for validators


# Payload size memory usage config
MAX_UPLOAD_SIZE_MB = config(
    "MAX_UPLOAD_SIZE_MB", cast=int, default=30
)  # Allowed payload size

MAX_UPLOAD_FILE_SIZE_MB = config(
    "MAX_UPLOAD_FILE_SIZE_MB", cast=float, default=0.1
)  # 100KB by default
# Upto 100Kb the file will be stored in memory, For more than that, data
# will be uploaded in server temporarily which will be handled by FILE_UPLOAD_HANDLERS.


DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024
# This is to let the django upload data in memory, so that the request can proceed.
# Payload size memory usage config

MAX_UPLOAD_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
from .db import DATABASE as DATABASES_

DATABASES = DATABASES_


def copy_default_images():
    """
    We won't be editing media dir
    media dir will reside in .gitignore
    So, we are not doing any manual work
    to copy media files,
    and pushing to git repo.
    """

    # Default Images source that exist in the root
    destination_for_source = BASE_DIR / "default_images"

    # Path for the default images that will be copied into
    destination_for_default_folder = MEDIA_ROOT / "default_images"
    if not os.path.exists(destination_for_default_folder):
        os.makedirs(destination_for_default_folder)

    try:
        shutil.copytree(
            destination_for_source, destination_for_default_folder, dirs_exist_ok=True
        )
    except Exception as e:
        pass
    return None


try:
    copy_default_images()
except Exception:
    pass


from .rest import *
from .spectacular import *

INTERNAL_IPS = []
SERVER_ENV = config("SERVER_ENV", cast=bool, default=True)
# setting SERVER_ENV to True


if DEBUG and not SERVER_ENV:
    import socket

    hostname_ = socket.gethostname()
    ip_address = socket.gethostbyname(hostname_)
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
        ip_address,
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: True,
    }


DISABLED_AUTHENTICATION = config("DISABLED_AUTHENTICATION", cast=bool, default=False)

SECURE_PROXY = config("SECURE_PROXY", cast=bool, default=False)
if SECURE_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
