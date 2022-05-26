from http import HTTPStatus
from serverless import ContentType


class Request:
    def __init__(self,
                 params: {},
                 path: str,
                 body: str):
        self._params = params
        self._path = path
        self._body = body

    def param(self, key: str):
        return self._params[key]

    def path(self) -> str:
        return self._path

    def body(self) -> str:
        return self._body


class Invoke:
    def __init__(self,
                 invoke_action: str,
                 params: {} = {},
                 path: str = "",
                 body: str = ""):
        self._invoke_action = invoke_action
        self._params = params
        self._path = path
        self._body = body

    def invoke_action(self) -> str:
        return self._invoke_action

    def params(self) -> {}:
        return self._params

    def path(self) -> str:
        return self._path

    def body(self) -> str:
        return self._body


class Response:
    def __init__(self,
                 payload: str,
                 http_status: int = HTTPStatus.OK,
                 content_type: ContentType = ContentType.MIMEPlain):
        self._payload = payload
        self._http_status = http_status
        self._content_type = content_type

    def content_type(self) -> ContentType:
        return self._content_type

    def payload(self) -> str:
        return self._payload

    def http_status(self) -> int:
        return self._http_status
