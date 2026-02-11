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

import os
import sys
import dotenv

from django.contrib import admin
from django.urls import path, include


# ============================
# Load environment variables
# ============================
# Loads variables from a .env file into the environment
dotenv.load_dotenv()


# ============================
# Environment detection
# ============================

# DEBUG
# Enabled only when DEBUG=True explicitly in environment variables
DEBUG = os.getenv("DEBUG") == "True"

# TESTING
# Detects Django test runs (manage.py test)
TESTING = "test" in sys.argv

# ENVIRONMENT
# Defines deployment environment: production / staging / development
ENVIRONMENT = os.getenv("ENV", "production").lower()


# ============================
# URL patterns
# ============================
# Root URL patterns
# App-specific routes should be included here using `include()`
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # User accounts and profiles
]


# ============================
# Error handlers
# ============================
# Custom error handlers are registered only in production-like environments.
# During development and testing, Django's default debug pages are preferred.
if ENVIRONMENT == "production" and not DEBUG and not TESTING:
    handler400 = "errors.views.custom_400_view"
    handler403 = "errors.views.custom_403_view"
    handler404 = "errors.views.custom_404_view"
    handler500 = "errors.views.custom_500_view"
