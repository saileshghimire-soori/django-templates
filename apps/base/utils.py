import json

from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.response import Response


def hostname_from_request(request):
    # split on `:` to remove port
    if not settings.DEBUG:
        return request.get_host().split(":")[0].lower()

    return request.get_host()


def is_valid_json(json_data_function, *args):
    try:
        json.loads(json_data_function(*args))
        return True
    except Exception:
        pass
    return False


def clean_response(response, include_tokens=False):
    resp_data = (
        json.loads(response.content.decode("utf-8"))
        if response.content and is_valid_json(response.content.decode, "utf-8")
        else {}
    )
    if include_tokens:
        resp_data["access"] = ""
        resp_data["refresh"] = ""
    return resp_data


def log_request_response(
    request: WSGIRequest | ASGIRequest,
    response: Response,
    body: dict,
    catch_error=False,
    server_error_logging=False,
) -> None:
    allowed_methods = ["PATCH", "PUT", "POST", "DELETE"]
    allowed_endpoints = ["/api/"]

    if (
        request.method.casefold() in [method.casefold() for method in allowed_methods]
        and any(
            str(endpoint).casefold() in str(request.get_full_path()).casefold()
            for endpoint in allowed_endpoints
        )
        or catch_error
    ):

        try:
            body.pop("password", "password")
            body.pop("new_password", "new_password")
        except Exception as e:
            pass

        device_type = {
            "mobile": request.user_agent.is_mobile,
            "pc": request.user_agent.is_pc,
            "tablet": request.user_agent.is_tablet,
            "other": request.user_agent.is_tablet,
        }
        os_ = request.user_agent.os.family.lower()
        os_type_ = os_.split()[0]
        os_type = {
            "windows": os_type_ == "windows",
            "ios": os_type_ == "ios",
            "android": os_type_ == "android",
            "mac": os_type_ == "mac",
            "linux": os_type_ == "linux",
            "other": os_type_ == "other",
        }

        true_os = next((key for key, value in os_type.items() if value), "other")
        true_device = next(
            (key for key, value in device_type.items() if value), "other"
        )

        from apps.api_logs.models import APILog

        try:
            response.render()
        except Exception as e:
            pass
        include_tokens = "login" in str(request.get_full_path()).casefold()

        headers_data = dict(request.headers)
        try:
            headers_data.pop("Authorization", None)
            headers_data.pop("authorization", None)
        except Exception as e:
            pass

        server_error = json.loads(response.headers.get("server_error", "false").lower())
        params = {
            "url": str(request.get_full_path()),
            "method": request.method,
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": request.headers.get("user-agent"),
            "body": body,
            "header": headers_data,
            "response": clean_response(response, include_tokens=include_tokens),
            "user_id": request.user.id if request.user else 0,
            "device_type": true_device,
            "os_type": true_os,
            "status_code": 500 if server_error else response.status_code,
            # "status_code": (
            #     500
            #     if server_error_logging and request.method.lower() == "get"
            #     else response.status_code
            # ),
            # "created_by": request.user.id if request.user else 0,
        }

        APILog.objects.create(**params)
        return
