# django-lgi - Django Lambda Gateway Interface

django-lgi is a python module that interprets [HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html) requests sent to your Django project in Lambda.

## Features
* Process [2.0 payload format version](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html) data that API Gateway sends to a Lambda integration.
* Trigger management commands directly on lambda, e.g. invoke lambda function with `{"manage": ["version"]}` to [display the current Django version](https://docs.djangoproject.com/en/dev/ref/django-admin/#determining-the-version).

## Installation

`pip install django-lgi`

## Usage

Create `lgi.py` file in Django project root. Remember to replace `mysite.settings` with dotted path to your settings module.

```
import os

from lgi import get_lgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

application = get_lgi_application()
```

Set lambda handler to `mysite.lgi.application`.

## Examples
* [Djambda](https://github.com/netsome/djambda) - example project setting up Django application in AWS Lambda managed by Terraform.

## Related Projects
* [awsgi](https://github.com/slank/awsgi)
* [apig-wsgi](https://github.com/adamchainz/apig-wsgi)
* [Zappa](https://github.com/Miserlou/Zappa)
* [chalice](https://github.com/aws/chalice)

## Testing
To run the test suite, first, create and activate a virtual environment. Then run tests.
```
$ flit install -s
$ cd tests
$ ./runtests.py
```
