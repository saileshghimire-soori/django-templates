from django.urls import path

from apps.authentication.views.signup import SignupView

urlpatterns = [
    path("users/signup", SignupView.as_view(), name="user-signup"),
]
