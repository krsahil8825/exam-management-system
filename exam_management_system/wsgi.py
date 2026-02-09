"""
exam_management_system.wsgi
~~~~~~~~~~~~~~~~~~~~~~~~~~~

WSGI entry point for the Django exam_management_system project.

This module exposes the WSGI callable used by synchronous web servers
(such as Gunicorn, uWSGI, or mod_wsgi) to serve the application.

It is responsible for:
- Initializing Django with the correct settings module
- Providing the WSGI application object for production deployments
"""

import os

from django.core.wsgi import get_wsgi_application


# Set the default Django settings module for WSGI-based servers.
# This ensures the correct configuration is loaded before the application starts.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "exam_management_system.settings",
)

# Create and expose the WSGI application callable.
# This object is used by the WSGI server to handle incoming requests.
application = get_wsgi_application()
