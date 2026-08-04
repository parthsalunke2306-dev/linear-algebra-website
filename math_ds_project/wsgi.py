"""
WSGI config for math_ds_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'math_ds_project.settings')

application = get_wsgi_application()

try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print("Auto-migration exception:", e)

app = application
