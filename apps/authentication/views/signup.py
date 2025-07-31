from django.contrib.auth import get_user_model

from apps.authentication.serilalizers.signup import SignupSerializer
from apps.base.views import CustomGenericCreateView

User = get_user_model()


class SignupView(CustomGenericCreateView):
    """
    View for user signup.
    """

    serializer_class = SignupSerializer
    permission_classes = []
    authentication_classes = []
    queryset = User.objects.all()
