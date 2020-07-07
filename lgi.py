"""
Django Lambda Gateway Interface
"""
__version__ = "0.1.1"

import logging
from io import BytesIO, StringIO

import django
from django.conf import settings
from django.core import management, signals
from django.core.handlers import base
from django.http import HttpRequest, QueryDict, parse_cookie
from django.urls import set_script_prefix
from django.utils.functional import cached_property

logger = logging.getLogger("django.request")
_default_route_key = "$default"


class LGIRequest(HttpRequest):
    def __init__(self, event):
        script_name = get_script_name(event)
        self.path = event["requestContext"]["http"]["path"]
        # If PATH_INFO is empty (e.g. accessing the SCRIPT_NAME URL without a
        # trailing slash), operate as if '/' was requested.
        prefix_end = len(script_name.rstrip("/"))
        self.path_info = self.path[prefix_end:] or "/"
        self.event = event
        self.method = event["requestContext"]["http"]["method"]
        self.META = {
            "REQUEST_METHOD": self.method,
            "QUERY_STRING": event["rawQueryString"],
            "SCRIPT_NAME": script_name,
            "PATH_INFO": self.path_info,
            "REMOTE_ADDR": event["requestContext"]["http"]["sourceIp"],
            "REMOTE_HOST": event["requestContext"]["http"]["sourceIp"],
            "SERVER_NAME": event["requestContext"]["domainName"],
            "SERVER_PORT": "443",
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
        }
        for name, value in event["headers"].items():
            corrected_name = name.replace("-", "_").upper()
            if corrected_name not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                corrected_name = f"HTTP_{corrected_name}"
            # Duplicate query strings are combined with commas
            self.META[corrected_name] = value
        self._set_content_type_params(self.META)
        self._stream = BytesIO(self.event.get("body", "").encode())
        self._read_started = False
        self.resolver_match = None

    def _get_scheme(self):
        # Amazon API Gateway exposes HTTPS endpoints only
        return "https"

    @cached_property
    def GET(self):
        return QueryDict(self.META["QUERY_STRING"])

    def _get_post(self):
        if not hasattr(self, "_post"):
            self._load_post_and_files()
        return self._post

    def _set_post(self, post):
        self._post = post

    POST = property(_get_post, _set_post)

    @property
    def FILES(self):
        if not hasattr(self, "_files"):
            self._load_post_and_files()
        return self._files

    @cached_property
    def COOKIES(self):
        # parse_cookie expects cookies list as a ; separated string
        return parse_cookie(";".join(self.event.get("cookies", [])))


class LGIHandler(base.BaseHandler):
    request_class = LGIRequest

    def __init__(self):
        super().__init__()
        self.load_middleware()

    def __call__(self, event, context):
        logger.debug(event)

        # management commands
        if "manage" in event:
            output = StringIO()
            management.call_command(*event["manage"], stdout=output)
            return {"output": output.getvalue()}

        # api gateway
        version = event["version"]
        if version != "2.0":
            raise ValueError(f"{version} format version is not supported")

        set_script_prefix(get_script_name(event))
        signals.request_started.send(sender=self.__class__, event=event)
        request = self.request_class(event)
        response = self.get_response(request)

        response._handler_class = self.__class__

        return {
            "cookies": list(c.output(header="") for c in response.cookies.values()),
            "isBase64Encoded": False,
            "statusCode": response.status_code,
            "headers": dict(response.items()),
            "body": response.content.decode(),
        }


def get_script_name(event):
    return settings.FORCE_SCRIPT_NAME or ""


def get_lgi_application():
    django.setup(set_prefix=False)
    return LGIHandler()
