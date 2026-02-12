"""
communication.views
~~~~~~~~~~~~~~~~~~~

View functions for the communication application.
"""

from django.http import HttpResponse


def home(request):
    """Render the home page for the communication app."""
    return HttpResponse(
        "Welcome to the Communication Center. Soon, you will be able to access messaging features here."
    )
