"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()

# Optional Sentry — no-op unless SENTRY_DSN is set (PII scrubbers always applied).
from core.sentry_init import init_sentry  # noqa: E402

init_sentry()
