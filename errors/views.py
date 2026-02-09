"""
errors.views
~~~~~~~~~~~~

Custom error view implementations for the Exam Management System.

This module defines user-friendly handlers for common HTTP error responses
that may occur during normal operation of the application.

Purpose:
- Replace Django's default error pages in production
- Render a unified error template for all HTTP errors
- Return correct HTTP status codes without exposing internal details

These views are intended to be registered as global error handlers
in the root URL configuration when running in production environments.
"""

from django.shortcuts import render


def custom_400_view(request, exception):
    """
    Handle HTTP 400 (Bad Request) errors.

    This view is triggered when the server cannot process a malformed
    or invalid client request.
    """
    return render(
        request,
        "errors/error.html",
        {
            "status_code": 400,
            "title": "Bad Request",
            "message": "The request could not be understood by the server.",
        },
        status=400,
    )


def custom_403_view(request, exception):
    """
    Handle HTTP 403 (Forbidden) errors.

    This view is triggered when a user attempts to access a resource
    without sufficient permissions.
    """
    return render(
        request,
        "errors/error.html",
        {
            "status_code": 403,
            "title": "Permission Denied",
            "message": "You do not have permission to access this resource.",
        },
        status=403,
    )


def custom_404_view(request, exception):
    """
    Handle HTTP 404 (Not Found) errors.

    This view is triggered when a requested URL does not match any
    registered route in the application.
    """
    return render(
        request,
        "errors/error.html",
        {
            "status_code": 404,
            "title": "Page Not Found",
            "message": "The page you are looking for does not exist.",
        },
        status=404,
    )


def custom_500_view(request):
    """
    Handle HTTP 500 (Internal Server Error) errors.

    This view is triggered when an unhandled exception occurs on the
    server side during request processing.
    """
    return render(
        request,
        "errors/error.html",
        {
            "status_code": 500,
            "title": "Server Error",
            "message": "An internal server error occurred. Please try again later.",
        },
        status=500,
    )
