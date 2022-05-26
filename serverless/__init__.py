from serverless.io import Request, Response, Invoke
from enum import StrEnum


class ContentType(StrEnum):
    MIMEJSON = "application/json"
    MIMEHTML = "text/html"
    MIMEXML = "application/xml"
    MIMEXML2 = "text/xml"
    MIMEPlain = "text/plain"
    MIMEPOSTForm = "application/x-www-form-urlencoded"
    MIMEMultipartPOSTForm = "multipart/form-data"
    MIMEPROTOBUF = "application/x-protobuf"
    MIMEMSGPACK = "application/x-msgpack"
    MIMEMSGPACK2 = "application/msgpack"
    MIMEYAML = "application/x-yaml"


__all__ = ["Request", "Response", "Invoke", "ContentType"]
