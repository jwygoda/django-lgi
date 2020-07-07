#!/usr/bin/env python
import unittest

try:
    import lgi  # noqa: F401
except ImportError as e:
    raise RuntimeError(
        "django-lgi module not found, reference README.md for instructions."
    ) from e
else:
    from django.conf import settings

if __name__ == "__main__":
    settings.configure()
    unittest.main("tests")
