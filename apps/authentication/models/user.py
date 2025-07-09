from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.managers import CustomUserManager
from apps.base.models import AbstractBaseModel, models
from apps.base.utils import hostname_from_request


def upload_path_user(instance, filename):
    return "/".join(["user_image", filename])


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """

    DO NOT raise any model validation error here from the User model.
    That will stop the complete cycle of request and response for
    default panel, & drf panel cycle as we are using CustomErrorMiddleware.
    And will result in an error:
    ```
    The request's session was deleted before the request completed.
    The user may have logged out in a concurrent request, for example.
    ```

    Also, the user may not log in to the admin panel.

    """

    GENDER_TYPE = (
        ("male", "MALE"),
        ("female", "FEMALE"),
        ("other", "OTHER"),
    )
    email = models.EmailField(
        max_length=255,
        help_text="Email address. Max Length: 255 characters",
        unique=True,
    )
    # If Login from email and password and no Need to username, Comment username
    username = models.CharField(
        max_length=50,
        unique=True,
        help_text="Username must be unique and max_length upto 50 characters",
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="First name can have max_length upto 50 characters, blank=True",
    )
    middle_name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Middle name can have max_length upto 50 characters, blank=True",
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Last name can have max_length upto 50 characters, blank=True",
    )
    full_name = models.CharField(
        max_length=152, help_text="full name max length=152", blank=True, editable=False
    )
    designation = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(
        max_length=30,
        choices=GENDER_TYPE,
        help_text="Choices are male, female, and other. Default=male",
    )
    birth_date = models.DateField(
        null=True, blank=True, help_text="Blank=True and null=True"
    )
    address = models.TextField(
        max_length=50,
        blank=True,
        help_text="Address should be maximum of 50 characters",
    )
    mobile_no = models.CharField(
        max_length=15,
        blank=True,
        help_text="Mobile no. should be maximum of 15 characters",
    )
    # photo = models.ImageField(
    #     upload_to=upload_path_user,
    #     validators=[validate_image],
    #     blank=True,
    #     default="default_images/profile.png",
    # )

    # --------------- ROLES and PERMISSIONS
    # roles = models.ManyToManyField("authentication.Roles", blank=True)

    # ---------- USER Status-------
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()
    # If username is not needed then make REQUIRED_FIELDS=[] and username=None
    # username=None
    REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = "email"

    def tokens(self, request):
        refresh = RefreshToken.for_user(self)
        host_name = hostname_from_request(request)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "domain_name": host_name,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "branch": self.get_branch_data,
            "is_superuser": self.is_superuser,
            **self.get_all_permissions,
        }

    def save(self, *args, **kwargs):
        names = [self.first_name, self.middle_name, self.last_name]
        self.full_name = " ".join(name for name in names if name)
        super().save(*args, **kwargs)
