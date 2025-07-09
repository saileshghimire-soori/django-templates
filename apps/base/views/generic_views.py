import django_filters
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.base.views import CustomAPIResponse


class CustomThrottlingClass:

    @property
    def throttle_scope(self):
        if self.request.user.is_superuser:
            return "superuser"
        method_scope_map = {
            "GET": "get",
            "POST": "post",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        scope_suffix = method_scope_map.get(self.request.method, "get")
        return (
            f"auth_{scope_suffix}"
            if self.request.user and self.request.user.is_authenticated
            else f"public_{scope_suffix}"
        )


class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"

    # if limit ,page is not given then default pagination limit sets to 50
    page_size = 50

    # if limit > this. the qs are capped to max_page_size limit (threshold for limit)
    max_page_size = 50

    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": getattr(
                    self, "success_response_message", "Data retrieved successfully."
                ),
                "total_count": self.page.paginator.count,
                "current_count": len(data),
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "data": data,
            }
        )

    def get_results(self, data):
        """
        Since we've overriden the results key with `data`
        in `get_paginated_response`, the `Filters` button
        in Browsable API Docs will disappear.

        To bring that button back, we need to
        override this get_results() method
        by returning the actual results/data.
        Here in our case, data will be in `data` key.
        """
        return data["data"]


class FilteringOrderingPaginationMixin:
    # Mixin to add filtering, ordering, and pagination to a view.

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = []
    ordering_fields = ["-created_at", "created_at", "id", "-id"]
    ordering = "-created_at"
    filterset_fields = []
    pagination_class = CustomPagination


class CustomGenericListView(FilteringOrderingPaginationMixin, ListAPIView):
    request_action = "list"

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CustomErrorMessage:

    def _get_message(self, data):
        for field, errors in data.items():
            if isinstance(errors, list):
                for error in errors:
                    return f"Failed. {str(error).capitalize()}"
            elif isinstance(errors, str):
                return f"Failed. {errors.capitalize()}"
        return None


class CustomGenericCreateView(CreateAPIView, CustomErrorMessage):

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            message = self._get_message(data=errors)
            if message:
                return CustomAPIResponse.custom_error_response(
                    errors=errors, message=message
                )
            return CustomAPIResponse.custom_error_response(
                errors=errors,
            )
        self.perform_create(serializer)
        return CustomAPIResponse.custom_success_response(
            data=serializer.data,
            message="Data created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CustomGenericUpdateView(UpdateAPIView, CustomErrorMessage):
    http_method_names = ["patch"]  # only allows PATCH

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            errors = serializer.errors
            message = self._get_message(data=errors)
            if message:
                return CustomAPIResponse.custom_error_response(
                    errors=errors, message=message
                )
            return CustomAPIResponse.custom_error_response(
                errors=errors,
            )

        self.perform_update(serializer)
        return CustomAPIResponse.custom_success_response(
            data=serializer.data, message="Data updated successfully."
        )


class CustomGenericRetrieveView(RetrieveAPIView):

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomAPIResponse.custom_success_response(
            data=serializer.data, message="Data retrieved successfully."
        )
