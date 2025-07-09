import json
import sys
import traceback

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpResponse, JsonResponse
from djangorestframework_camel_case.util import camelize
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from apps.base.exceptions import BASE_EXCEPTIONS
from apps.base.utils import is_valid_json, log_request_response


class CustomErrorMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        self.exception = exception
        self.is_api_request = request.path.startswith("/api/")

        if self.is_api_request:

            if isinstance(
                exception,
                (
                    DjangoValidationError,
                    ValueError,
                    TypeError,
                    AttributeError,
                    *BASE_EXCEPTIONS,
                ),
            ):
                message = self.get_exception_message(exception)
                if isinstance(message, dict):
                    message = self.camelize_dict(message)
                    response = Response(message, status=status.HTTP_400_BAD_REQUEST)
                    response.accepted_renderer = JSONRenderer()
                    response.accepted_media_type = "application/json"
                    response.renderer_context = {"request": request}
                    return response
                return self.create_error_response(request, message)

        if isinstance(
            exception, (DjangoValidationError, ValueError, TypeError, *BASE_EXCEPTIONS)
        ):
            message = self.get_exception_message(exception)
            # message = self.camelize_dict(message)
            return self.create_error_response(request, message)

        return None

    def create_error_response(
        self, request, message, status_code=status.HTTP_400_BAD_REQUEST
    ):
        traceback_details = self.get_traceback_details()
        response_data = {
            "message": message,
            "details": traceback_details,
            "exception_class": self.exception.__class__.__name__,
        }
        if hasattr(self.exception, "errors"):
            response_data["errors"] = self.exception.errors
        # response = self.get_response(request)
        # TODO - handle for the django model response
        # response local variable issue

        # response = Response(response_data, status=status_code)
        # response.accepted_renderer = JSONRenderer()
        # response.accepted_media_type = "application/json"
        # response.renderer_context = {"request": request}

        # if self.is_api_request:
        #     body = (
        #         json.loads(request.body.decode("utf-8"))
        #         if request.body and is_valid_json(request.body.decode, "utf-8")
        #         else {}
        #     )
        #     log_request_response(
        #         request=request,
        #         response=response,
        #         body=body,
        #         catch_error=True,
        #         server_error_logging=True,
        #     )
        # return response

        if self.is_api_request:
            response = Response(response_data, status=status_code)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {"request": request}

            # body = (
            #     json.loads(request.body.decode("utf-8"))
            #     if request.body and is_valid_json(request.body.decode, "utf-8")
            #     else {}
            # )
            # log_request_response(
            #     request=request,
            #     response=response,
            #     body=body,
            #     catch_error=True,
            #     server_error_logging=True,
            # )
            # TODO - check status code in logging
            headers = response.headers
            headers["server_error"] = True
            return response
        else:
            response = JsonResponse(response_data, status=status_code)

    def get_exception_message(self, exception):
        """
        Helper function to extract a consistent message from an exception.
        """
        traceback_details = self.get_traceback_details()
        if hasattr(exception, "message"):
            msg = exception.message
            if isinstance(msg, dict):
                msg = self.camelize_dict(msg)  # Use the safe camelize_dict
            if hasattr(exception, "exception_class"):
                msg["exception_class"] = self.camelize_dict(exception.exception_class)
            if hasattr(exception, "errors"):
                msg["errors"] = self.camelize_dict(exception.errors)
            msg["details"] = traceback_details
            return msg
        return str(exception).capitalize()

    def get_traceback_details(self):
        """
        Helper function to get detailed traceback with file names and line numbers in a dict.
        """
        if not settings.DEBUG:
            return None

        # For production, capture just the relevant parts of the traceback
        exc_type, exc_value, exc_tb = sys.exc_info()

        traceback_info = []

        tb = exc_tb
        while tb:
            frame = tb.tb_frame
            lineno = tb.tb_lineno
            co = frame.f_code
            filename = co.co_filename
            funcname = co.co_name
            linecache = traceback.format_exc().splitlines()

            # Capture local variables (limit depth or sensitive info if needed)
            local_vars = {
                k: repr(v)
                for k, v in frame.f_locals.items()
                if not k.startswith("__") and not callable(v)
            }

            traceback_info.append(
                {
                    "file": filename,
                    "line": lineno,
                    "function": funcname,
                    "locals": local_vars,
                }
            )

            tb = tb.tb_next

        # for filename, lineno, funcname, line in traceback.extract_tb(exc_tb):
        #     traceback_info.append(
        #         {
        #             "file": filename,
        #             "line": lineno,
        #             "function": funcname,
        #             "code": line.strip() if line else None,
        #         }
        #     )

        return {"traceback": list(reversed(traceback_info))}

    def camelize_dict(self, data):
        """Utility method to camelize dictionary keys."""
        if isinstance(data, dict):
            # Process the dictionary: recursively camelize its keys
            return camelize(
                {
                    k: self.camelize_dict(v) if isinstance(v, (dict, list)) else v
                    for k, v in data.items()
                }
            )
        elif isinstance(data, list):
            # If it's a list, recursively process each item
            return [self.camelize_dict(item) for item in data]
        else:
            # Base case: return the value as-is (it's neither a dict nor a list)
            return data


class NonHtmlDebugToolbarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not settings.SERVER_ENV and settings.DEBUG:

            if (
                request.GET.get("format", "") == "json"
                and response["Content-Type"] == "application/json"
            ):
                # content = json.dumps(sort_json(json.loads(response.content)), indent=2)
                content = json.dumps(
                    json.loads(response.content), sort_keys=True, indent=2
                )
                response = HttpResponse(
                    f"<html><body><pre>{content}</pre></body></html>"
                )
        return response


import time

from django.http import HttpResponse
from django.utils.timezone import now


class RequestTimerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()  # Record start time

        # Call the next middleware or view
        response = self.get_response(request)

        end_time = time.perf_counter()
        elapsed_time_ms = (end_time - start_time) * 1000
        rounded_time = round(elapsed_time_ms, 2)
        # elapsed time will be in headers
        response["X-Elapsed-Time"] = str(rounded_time)
        return response
