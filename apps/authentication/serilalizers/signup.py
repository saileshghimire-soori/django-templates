from apps.authentication.models import CustomUser
from apps.base.serializers import BaseModelSerializer, serializers


class SignupSerializer(BaseModelSerializer):
    """
    Serializer for user signup.
    """

    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        attrs.pop("confirm_password", None)
        return super().validate(attrs)
