"""
exams.views
~~~~~~~~~~~

View functions for the exams application.
"""

from django.http import HttpResponse


def home(request):
    """Render the home page for the exams app."""
    return HttpResponse(
        "Welcome to the Exams Module. Soon, you will be able to create and manage exams here."
    )
