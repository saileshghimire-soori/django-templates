from django.contrib import admin

from apps.api_logs import models

admin.site.register(models.APILog)
