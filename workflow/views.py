"""
workflow.views
~~~~~~~~~~~~~~

View functions for the workflow application.
"""

from django.http import HttpResponse

def home(request):
    """Render the home page for the workflow app."""
    return HttpResponse(
        "Welcome to the Workflow Module. Soon, you will be able to create and manage tasks here."
    )