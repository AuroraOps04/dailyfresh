"""
WSGI config for dailyfresh project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

profile = os.environ.get('DAILYFRESH_PROFILE', 'develop')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings.%s" % profile)

application = get_wsgi_application()
