from serverless import Request, Response, Invoke, ContentType
from http import HTTPStatus


def action(req: Request) -> Invoke or Response:
    a = req.param('a')
    b = req.param('b')
    s = req.param("sign")

    if s == '+':
        return Invoke("add", params={'a': a, 'b': b})
    elif s == '*':
        return Invoke("mult", params={'a': a, 'b': b})
    elif s == '>':
        return Response(str(a > b))
    elif s == '<':
        return Response(str(a < b))
    elif s == "==":
        return Response(str(a == b))
    else:
        return Response("unknown sign: {}".format(s), http_status=HTTPStatus.BAD_REQUEST)
