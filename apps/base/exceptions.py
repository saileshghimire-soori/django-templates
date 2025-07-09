from django.conf import settings
from django.core.exceptions import FieldError, ValidationError
from django.db import DatabaseError
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import _get_error_details
from rest_framework.serializers import ValidationError as REST_VALIDATOR


class BaseAPIValidationError(REST_VALIDATOR):

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = list(detail)
        self.detail = _get_error_details(detail, code)


class APIError(BaseAPIValidationError):
    pass


class ModelValidationError(BaseException):
    pass


class BaseException(Exception):

    def __init__(self, message, status_code=400, errors={}):
        super().__init__(message)
        self.success = False
        self.message = message
        self.status_code = status_code
        self.exception_class = self.__class__.__name__
        self.errors = errors


class ModelFieldError(BaseException):
    pass


BASE_EXCEPTIONS = [
    BaseException,
    FieldError,
    DatabaseError,
    OverflowError,  # for datetime
]

__all__ = [
    "BaseException",
    "FieldError",
    "DatabaseError",
    "OverflowError",
]
