from serverless import Request, Response, Evoke

action_name = 'calculate'


def action(req: Request) -> Evoke or Response:
    a = req.param('a')
    b = req.param('b')
    s = req.param('sign')

    if s == '+':
        return Evoke("add", params={'a': a, 'b': b})
    elif s == '*':
        return Evoke("mult", params={'a': a, 'b': b})
    elif s == '>':
        return Response(str(a > b))
    elif s == '<':
        return Response(str(a < b))
    elif s == '==':
        return Response(str(a == b))
    else:
        return Response("unknown sign: {}".format(s))
