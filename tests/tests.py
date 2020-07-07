from django.core.signals import request_started
from django.db import close_old_connections
from django.test import SimpleTestCase, override_settings

from lgi import get_lgi_application


@override_settings(ROOT_URLCONF="urls")
class LGITestCase(SimpleTestCase):
    def setUp(self):
        request_started.disconnect(close_old_connections)
        self.application = get_lgi_application()

    def tearDown(self):
        request_started.connect(close_old_connections)

    def test_get_lgi_application_manage(self):
        event = {"manage": ["check"]}
        response = self.application(event, None)
        self.assertEqual(
            response, {"output": "System check identified no issues (0 silenced).\n"}
        )

    def test_get_lgi_application_gateway(self):
        event = {
            "version": "2.0",
            "rawQueryString": "",
            "headers": {},
            "requestContext": {
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "GET", "path": "/", "sourceIp": "IP"},
            },
        }
        response = self.application(event, None)
        self.assertEqual(response["body"], "Hello World!")
        self.assertEqual(
            response["headers"], {"Content-Type": "text/html; charset=utf-8"}
        )
        self.assertEqual(response["statusCode"], 200)

    def test_body(self):
        event = {
            "version": "2.0",
            "rawQueryString": "",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            },
            "requestContext": {
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "POST", "path": "/", "sourceIp": "IP"},
            },
            "body": "name=Andrew",
        }
        response = self.application(event, None)
        self.assertEqual(response["body"], "Hello Andrew!")
        self.assertEqual(response["statusCode"], 200)

    def test_body_b64(self):
        event = {
            "version": "2.0",
            "rawQueryString": "",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            },
            "requestContext": {
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "POST", "path": "/", "sourceIp": "IP"},
            },
            "body": "bmFtZT1BbmRyZXc=",  # name=Andrew
            "isBase64Encoded": True,
        }
        response = self.application(event, None)
        self.assertEqual(response["body"], "Hello Andrew!")
        self.assertEqual(response["statusCode"], 200)

    def test_get_query_string(self):
        event = {
            "version": "2.0",
            "rawQueryString": "name=Andrew",
            "headers": {},
            "requestContext": {
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "GET", "path": "/", "sourceIp": "IP"},
            },
        }
        response = self.application(event, None)
        self.assertEqual(response["body"], "Hello Andrew!")

    def test_headers(self):
        event = {
            "version": "2.0",
            "rawQueryString": "",
            "headers": {
                "Content-Type": "text/plain; charset=utf-8",
                "Referer": "Wales",
            },
            "requestContext": {
                "domainName": "id.execute-api.us-east-1.amazonaws.com",
                "http": {"method": "GET", "path": "/meta/", "sourceIp": "IP"},
            },
        }
        response = self.application(event, None)
        self.assertEqual(response["body"], "From Wales")
        self.assertEqual(
            response["headers"], {"Content-Type": "text/plain; charset=utf-8"}
        )
        self.assertEqual(response["statusCode"], 200)
