from apps.base.serializers import BaseModelSerializer, ExcludeFields

from .models import APILog


class APILogExcludeFields:

    exclude = ExcludeFields.exclude + [
        "body",
        "response",
        "header",
    ]


class ApiLogsListSerializer(BaseModelSerializer):
    class Meta:
        model = APILog
        # exclude = APILogExcludeFields.exclude
        fields = [
            "id",
            "url",
            "os_type",
            "device_type",
            "method",
            "ip",
            "user_agent",
            "system_details",
            "user_id",
            "extra_field",
            "status_code",
            "created_at",
            "created_by",
        ]


class ApiLogsRetrieveSerializer(BaseModelSerializer):
    class Meta:
        model = APILog
        exclude = [
            "deleted_at",
        ]
