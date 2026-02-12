"""
accounts.views
~~~~~~~~~~~~~~

Defines view functions for the accounts application.

This module contains views responsible for handling HTTP requests
related to user accounts and returning appropriate responses.
"""

from django.http import HttpResponse


def home(request):
    """Render the home page for the accounts app."""
    return HttpResponse(
        "Welcome to the Exam Management System! This is your dashboard. Soon, you will see your profile information or upcoming exams"
    )
