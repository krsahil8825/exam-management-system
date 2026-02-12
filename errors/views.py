"""
errors.views
~~~~~~~~~~~~

Custom error handlers for the application.
"""

from django.shortcuts import render


def custom_400_view(request, exception):
    """Handle 400 Bad Request errors."""
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
    """Handle 403 Forbidden errors."""
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
    """Handle 404 Not Found errors."""
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
    """Handle 500 Internal Server Error."""
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
