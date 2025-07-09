from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

User = get_user_model()
from rest_framework.serializers import ListSerializer
from rest_framework.settings import api_settings
from rest_framework.utils.serializer_helpers import ReturnDict

from .exceptions import APIError


class ReadOnlyFields:
    read_only = [
        "created_by",
        "created_at",
        "created_at_bs",
        "updated_at",
        "modified_by",
        "deleted_at",
        "device_type",
        "os_type",
    ]


class ExcludeFields:
    exclude = [
        "created_by",
        "created_at",
        "created_at_bs",
        "updated_at",
        "modified_by",
        "deleted_at",
        "device_type",
        "os_type",
    ]


class ActionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class BaseModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop("exclude_fields", [])
        include_fields = kwargs.pop("include_fields", [])
        super().__init__(*args, **kwargs)
        for field_name in exclude_fields:
            self.fields.pop(field_name, None)

        # Include only specified fields
        if include_fields:
            new_fields = {
                field_name: self.fields[field_name] for field_name in include_fields
            }
            self.fields = new_fields

    def _assign_os_device(self, attrs):
        request = self.context.get("request", None)
        device_type = {
            "mobile": request.user_agent.is_mobile,
            "pc": request.user_agent.is_pc,
            "tablet": request.user_agent.is_tablet,
            "other": request.user_agent.is_tablet,
        }
        os_ = request.user_agent.os.family.lower()
        os_type_ = os_.split()[0]
        os_type = {
            "windows": os_type_ == "windows",
            "ios": os_type_ == "ios",
            "android": os_type_ == "android",
            "mac": os_type_ == "mac",
            "linux": os_type_ == "linux",
            "other": os_type_ == "other",
        }

        true_os = next((key for key, value in os_type.items() if value), "other")
        true_device = next(
            (key for key, value in device_type.items() if value), "other"
        )

        attrs["device_type"] = true_device
        attrs["os_type"] = true_os
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request_data = self.context.get("request")
        validated_data.pop("id", None)
        if not request_data:
            raise serializers.ValidationError(
                {
                    "message": "Invalid request. `request` needs to be passed "
                    "while creating the data"
                }
            )
        if not settings.DISABLED_AUTHENTICATION:
            user_id = None
            try:
                user_id = self.context.get("request").user.id
            except Exception:
                raise serializers.ValidationError(
                    {"message": "Invalid request. Invalid user."}
                )
            if user_id:
                validated_data["created_by"] = user_id
                validated_data["modified_by"] = user_id
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        request_data = self.context.get("request")
        if not request_data:
            raise serializers.ValidationError(
                {
                    "message": "Invalid request. `request` needs to be passed "
                    "while updating the data"
                }
            )

        if not settings.DISABLED_AUTHENTICATION:
            user_id = None
            try:
                user_id = self.context.get("request").user.id
            except Exception:
                raise serializers.ValidationError(
                    {"message": "Invalid request. Invalid user."}
                )

            if not user_id:
                raise serializers.ValidationError(
                    {
                        "message": "Failed to update the instance",
                        "detail": "Public user can not update the data",
                    }
                )
            validated_data["modified_by"] = user_id
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if "created_by" in self.fields:
            if instance.created_by:
                if instance.created_by >= 1 and "created_by" in self.fields:
                    repr["created_by"] = ActionUserSerializer(
                        User.objects.get(id=instance.created_by)
                    ).data
        if "modified_by" in self.fields:
            if instance.modified_by:
                if instance.modified_by >= 1 and "modified_by" in self.fields:
                    repr["modified_by"] = ActionUserSerializer(
                        User.objects.get(id=instance.modified_by)
                    ).data

        return repr

    @property
    def errors(self):
        from collections import OrderedDict

        formatted_errors = OrderedDict()

        all_errors = super().errors
        if not all_errors:
            return ReturnDict(formatted_errors, serializer=self)

        fields = self.fields  # caching fields
        required_msg = "This field is required."

        for field_name, field_errors in all_errors.items():
            # Skip empty errors immediately
            if not field_errors:
                continue

            # Handle non-list errors directly
            if not isinstance(field_errors, list):
                formatted_errors[field_name] = field_errors
                continue

            # Get field type once
            field = fields.get(field_name)

            # Handle non-ListSerializer fields directly
            if not isinstance(field, ListSerializer):
                formatted_errors[field_name] = field_errors
                continue

            # Handle required field error - most common case first
            if len(field_errors) == 1 and field_errors[0] == required_msg:
                formatted_errors[field_name] = field_errors
                continue

            indexed_errors = {
                idx: (
                    error
                    if isinstance(error, dict)
                    else {"non_field_errors": [str(error).capitalize()]}
                )
                for idx, error in enumerate(field_errors)
                if error
            }

            if indexed_errors:
                formatted_errors[field_name] = indexed_errors

        return ReturnDict(formatted_errors, serializer=self)

    @property
    def exception_class(self):
        return APIError

    def raise_exception(
        self,
        errors={},
    ):

        if not errors:
            raise ValueError("`errors` dict is required to raise a exception.")
        raise self.exception_class(errors)

    def get_request(self):
        request = self.context.get("request", None)
        if not request:
            self.raise_exception(
                {"request": "Request needs to be passed to the serializer"}
            )
            return None, None
        return request, request.method.lower()

    def validate_update(self, attrs):
        return attrs

    def validate_create(self, attrs):
        return attrs

    def validate(self, attrs):
        super().validate(attrs)
        self._assign_os_device(attrs=attrs)

        request, method = self.get_request()
        if method:
            if method in ["patch", "put"]:
                self.validate_update(attrs=attrs)
            elif method == "post":
                self.validate_create(attrs=attrs)

        return attrs

    def init_empty_dict_of_errors(self):
        # Initialize a empty dict for errors
        self.empty_dict_of_errors = {}

    def custom_errors_generator(
        self, error_dict, error_key, error_value: dict, parent_key
    ):
        """
        appends the given errors into the empt_dict_of_errors
        """
        if parent_key not in self.empty_dict_of_errors:
            self.empty_dict_of_errors[parent_key] = {}
        index = str(error_key)
        self.empty_dict_of_errors[parent_key][index] = error_value

    def raise_if_validation_errors(self):
        """
        This has to be called everytime we generate and stack errors and if the  dict of  errors is not empty then raise exception
        """

        if self.empty_dict_of_errors:

            keys_to_remove = [
                key for key, value in self.empty_dict_of_errors.items() if not value
            ]
            for key in keys_to_remove:
                del self.empty_dict_of_errors[key]
            self.raise_exception(errors=self.empty_dict_of_errors)


class AbstractBaseModelSerializer(serializers.ModelSerializer):
    """
    this base serializer sets the `created_by` and `modified_by` fields
    from the JWT token in the request.
    """

    def create(self, validated_data):
        user_id = self.context["request"].user.id
        print("user id : ", user_id, self.context["request"].user)
        validated_data["created_by"] = user_id
        validated_data["modified_by"] = user_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_id = self.context["request"].user.id
        validated_data["modified_by"] = user_id
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.created_by >= 1 and "created_by" in self.fields:
            repr["created_by"] = ActionUserSerializer(
                User.objects.get(id=instance.created_by)
            ).data
        if instance.modified_by >= 1 and "modified_by" in self.fields:
            repr["modified_by"] = ActionUserSerializer(
                User.objects.get(id=instance.modified_by)
            ).data
        return repr

    class Meta:
        abstract = True
