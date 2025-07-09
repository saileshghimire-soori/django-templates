from django.db import models
from django.db import transaction
from django.utils import timezone
from .exceptions import ModelValidationError


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self, hard=False):
        if hard:
            return super().delete()
        return self.update(deleted_at=timezone.now())

    def restore(self):
        return self.update(deleted_at=None)
    
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )

    def hard_delete(self):
        return self.get_queryset().delete(hard=True)

class AbstractSoftDelete(models.Model):
    deleted_at = models.DateTimeField(
        null=True, blank=True, default=None, editable=False
    )
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using, keep_parents)
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True

class AbstractCreatedByModifiedBy(models.Model):
    """
    An abstract class that provides created_by and modified_by fields.
    """

    created_by = models.IntegerField(default=0, editable=False)
    modified_by = models.IntegerField(default=0, editable=False)

    class Meta:
        abstract = True

class AbstractCreatedAtModifiedAt(models.Model):
    """
    Abstract class that provides created_at and updated_at fields.
    """

    created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, editable=False
    )
    created_at_bs = models.CharField(
        max_length=10, blank=True, null=True, editable=False
    )
    updated_at = models.DateTimeField(
        auto_now=True, blank=True, null=True, editable=False
    )

    class Meta:
        abstract = True


class DeviceApp(models.Model):
    DEVICE_TYPE = (
        ("mobile", "MOBILE"),
        ("pc", "PC"),
        ("tablet", "TABLET"),
        ("other", "OTHER"),
    )
    OS_TYPE = (
        ("windows", "Windows"),
        ("ios", "IOS"),
        ("android", "ANDROID"),
        ("mac", "MAC"),
        ("linux", "LINUX"),
        ("other", "OTHER"),
    )

    device_type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPE,
        default="mobile",
        help_text="Enum field for the device type.",
        editable=False,
    )
    os_type = models.CharField(
        max_length=10,
        choices=OS_TYPE,
        default="other",
        help_text="Enum field for the app type.",
        editable=False,
    )

    class Meta:
        abstract = True

class AbstractBaseModel(
    AbstractCreatedAtModifiedAt,
    AbstractCreatedByModifiedBy,
    AbstractSoftDelete,
    DeviceApp,
):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.errors_ = {}
        self.message_ = {}
    
    def _validate_update_data(self) -> None:
        pass

    def _validate_create_data(self) -> None:
        pass

    def _validate_required_field(self) -> None:
        pass

    def _validate_unique_together(self)-> None:
        pass

    def _validate(self):
        self._validate_required_field()
        self._validate_unique_together()
        if self.pk:
            self._validate_update_data()
        else:
            self._validate_create_data()

    def raise_exception(self, errors={}, message={},exception_class=None):
        if errors == {} or message == {}:
            raise ValueError("Please pass message, and errors.")
        if exception_class:
            raise exception_class(errors=errors, message=message)

        raise ModelValidationError(errors=errors, message=message)

    @transaction.atomic
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    class Meta:
        abstract = True