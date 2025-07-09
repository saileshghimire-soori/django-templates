from django.db import models

from apps.base.models import AbstractBaseModel


class APILog(AbstractBaseModel):
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    body = models.JSONField(blank=True, null=True, default=dict)
    header = models.JSONField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    system_details = models.JSONField(blank=True, null=True, default=dict)
    user_id = models.IntegerField(blank=True, null=True)
    extra_field = models.JSONField(blank=True, null=True)
    status_code = models.CharField(max_length=255, blank=True, null=True)

    # def __str__(self) -> str:


#        return f"({self.pk})-{self.ip}-{self.method}-{self.url}-{self.status_code}"


class ErrorLog(AbstractBaseModel):
    url = models.CharField(max_length=255)

    METHOD_CHOICES = (
        ("get", "GET"),
        ("post", "POST"),
        ("put", "PUT"),
        ("patch", "PATCH"),
        ("delete", "DELETE"),
    )
    method = models.CharField(
        max_length=8,
        choices=METHOD_CHOICES,
        default="get",
    )

    ip = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    body = models.JSONField(blank=True, null=True, default=dict)
    header = models.JSONField(blank=True, null=True)
    response = models.JSONField(blank=True, null=True)
    system_details = models.JSONField(blank=True, null=True, default=dict)
    user_id = models.IntegerField(blank=True, null=True)
    extra_field = models.JSONField(blank=True, null=True)
    status_code = models.CharField(max_length=255, blank=True, null=True)
