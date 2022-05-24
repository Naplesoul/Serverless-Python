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


class Evoke:
    def __init__(self,
                 action_name: str,
                 params: {} = {},
                 path: str = "",
                 body: str = ""):
        self._action_name = action_name
        self._params = params
        self._path = path
        self._body = body

    def action_name(self) -> str:
        return self._action_name

    def params(self) -> {}:
        return self._params

    def path(self) -> str:
        return self._path

    def body(self) -> str:
        return self._body


class Response:
    def __init__(self, payload: str):
        self._payload = payload

    def payload(self) -> str:
        return self._payload
