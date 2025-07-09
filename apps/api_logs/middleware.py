import json

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import QueryDict
from django.http.multipartparser import MultiPartParser, MultiPartParserError

from apps.base.utils import is_valid_json, log_request_response


class ApiLog:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        body = self._get_request_body(request)
        response = self.get_response(request)
        log_request_response(request, response, body)
        return response

    def _get_request_body(self, request):

        body_data = request.body
        if request.content_type == "application/json":
            return (
                json.loads(body_data.decode("utf-8"))
                if body_data and is_valid_json(body_data.decode, "utf-8")
                else {}
            )
        elif request.content_type == "application/x-www-form-urlencoded":
            return QueryDict(body_data).dict()
        elif request.content_type.startswith("multipart/form-data"):
            try:
                parser = MultiPartParser(request.META, request, request.upload_handlers)
                data, files = parser.parse()
                body = data.dict()
                body.update(
                    {
                        key: (
                            file.name
                            if isinstance(file, InMemoryUploadedFile)
                            else str(file)
                        )
                        for key, file in files.items()
                    }
                )

                return body
            except MultiPartParserError:
                return {}
        else:
            return {}
