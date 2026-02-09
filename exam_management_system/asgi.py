"""
exam_management_system.asgi
~~~~~~~~~~~~~~~~~~~~~~~~~~~

ASGI entry point for the Django exam_management_system project.

This module exposes the ASGI callable used by asynchronous servers
(such as Daphne, Uvicorn, or Hypercorn) to serve the application.

It is responsible for:
- Initializing Django with the correct settings module
- Providing the ASGI application object for async-capable deployments
"""

import os

from django.core.asgi import get_asgi_application


# Set the default Django settings module for ASGI-based servers.
# This ensures the correct configuration is loaded before the application starts.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "exam_management_system.settings",
)

# Create and expose the ASGI application callable.
# This object is used by the ASGI server to handle incoming requests.
application = get_asgi_application()
