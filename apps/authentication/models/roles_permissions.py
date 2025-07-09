from apps.base.models import AbstractBaseModel, SoftDeleteManager, models


class Roles(AbstractBaseModel):
    name = models.CharField(
        max_length=50, help_text="Name can have max of 50 characters"
    )
    is_active = models.BooleanField(default=True, help_text="by default=True")
    permissions = models.ManyToManyField(
        "CustomPermission",
        blank=True,
        help_text="blank=True",
        related_name="roles",
    )
    remarks = models.TextField(blank=True, null=True)

    # def __str__(self) -> str:
    #        return f"{self.name}"

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class PermissionCategory(AbstractBaseModel):
    name = models.CharField(
        max_length=50, help_text="Name can have max of 50 characters"
    )

    # def __str__(self):
    #     return f"ID-{self.id} : {self.name}"

    class Meta:
        verbose_name = "Permission Category"
        verbose_name_plural = "Permission Categories"


class CustomPermission(AbstractBaseModel):
    name = models.CharField(
        max_length=50, help_text="Name can have max of 50 characters"
    )
    code_name = models.CharField(
        max_length=50, help_text="Code Name can have max of 50 characters"
    )
    category = models.ForeignKey(
        "PermissionCategory",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="null=True, blank=True",
    )

    # def __str__(self):
    #     return f"{self.category} : {self.code_name} "

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def save(self, *args, **kwargs):
        self.code_name = str(self.code_name).lower()
        super().save(*args, **kwargs)
