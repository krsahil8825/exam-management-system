"""
exam_management_system.urls
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Root URL configuration for the exam_management_system project.

This module defines the top-level URL routing table and delegates
request handling to application-specific URL configurations.

It is responsible for:
- Mapping global URL patterns
- Including app-level URL configurations
- Exposing the Django admin interface
- Registering environment-specific error handlers
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings


# ============================
# URL patterns
# ============================
# Root URL patterns
# App-specific routes should be included here using `include()`
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # User accounts and profiles
    path("exams/", include("exams.urls")),  # Exam management and scheduling
    path(
        "communication/", include("communication.urls")
    ),  # Messaging and notifications
    path("workflow/", include("workflow.urls")),  # Workflow and process management
]

# Development-only URLs
if settings.DEBUG and settings.ENVIRONMENT == "development":
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]


# ============================
# Error handlers
# ============================
# Custom error handlers are registered only in production-like environments.
# During development and testing, Django's default debug pages are preferred.
if settings.ENVIRONMENT == "production" and not settings.DEBUG and not settings.TESTING:
    handler400 = "errors.views.custom_400_view"
    handler403 = "errors.views.custom_403_view"
    handler404 = "errors.views.custom_404_view"
    handler500 = "errors.views.custom_500_view"
