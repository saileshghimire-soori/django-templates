from rest_framework import status
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
    _positive_int,
)
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 1000

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request, self.count)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset : self.offset + self.limit])

    def get_paginated_response(
        self, data, message="List retrieved successfully.", stats=status.HTTP_200_OK
    ):
        return Response(
            {
                "message": message,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.count,
                "data_count": len(data),
                "data": data,
            },
            status=stats,
        )

    def get_results(self, data):
        """
        Since we've overriden the results key with `data`
        in `get_paginated_response`, the `Filters` button
        in Browsable API Docs will disappear.

        To bring that button, we need to
        override this get_results() method
        by returning the actual results/data.
        Here in our case, data will be in `data` key.
        """
        return data["data"]

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "data_count": {
                    "type": "integer",
                    "example": 123,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{offset_param}=400&{limit_param}=100".format(
                        offset_param=self.offset_query_param,
                        limit_param=self.limit_query_param,
                    ),
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{offset_param}=200&{limit_param}=100".format(
                        offset_param=self.offset_query_param,
                        limit_param=self.limit_query_param,
                    ),
                },
                "data": schema,
            },
        }

    def get_limit(self, request, count):
        if self.limit_query_param:
            try:
                query_limit = int(request.query_params[self.limit_query_param])
                max_limit_ = 0
                if query_limit == 0 and not self.max_limit:
                    return count

                elif query_limit == 0 and self.max_limit:
                    max_limit_ = self.max_limit
                elif query_limit > self.max_limit:
                    max_limit_ = self.max_limit
                if max_limit_ > 0:
                    return max_limit_
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit,
                )
            except (KeyError, ValueError):
                pass

        return self.default_limit


class CustomPagePagination(PageNumberPagination):
    page_size_query_param = "limit"
    page_query_param = "offset"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "Data retrieved successfully.",
                "data": data,
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
            }
        )

    def get_results(self, data):
        """
        Since we've overriden the results key with `data`
        in `get_paginated_response`, the `Filters` button
        in Browsable API Docs will disappear.

        To bring that button, we need to
        override this get_results() method
        by returning the actual results/data.
        Here in our case, data will be in `data` key.
        """
        return data["data"]
