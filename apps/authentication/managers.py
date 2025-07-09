from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Creating user, saving them and returning the user
    """

    def create_user(self, email, username, password=None, **extra_fields):

        if not email:
            raise ValueError("You must provide an email address")

        email = self.normalize_email(email)
        user_name = username.lower()
        user = self.model(email=email, username=user_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Creating SuperUser after the user creation.
        """
        user = self.create_user(
            email=email, username=username, password=password, **extra_fields
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
