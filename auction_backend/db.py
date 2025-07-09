from decouple import config

DB_HOST = config("DB_HOST", default="localhost")

"""
https://docs.djangoproject.com/en/5.1/ref/databases/#persistent-connections
When using ASGI, persistent connections should be disabled. Instead, use your database backend's built-in connection pooling if available, or investigate a third-party connection pooling option if required.
"""
DATABASE = {
    "default": {
        # "ENGINE": "django.db.backends.postgresql_psycopg3",
        "ENGINE": "django.db.backends.postgresql",
        # "ENGINE": "django_tenants.postgresql_backend",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": DB_HOST,
        "PORT": config("DB_PORT"),
        "ATOMIC_REQUESTS": True,
        # https://docs.djangoproject.com/en/5.1/ref/databases/#persistent-connections
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {
            # "pool": True,
            "sslmode": "disable",
            "client_encoding": "UTF8",
        },
        "CONN_MAX_AGE": 0,  # Since we are using pooling, this should be disabled.
    },
}
