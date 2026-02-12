"""
accounts.urls
~~~~~~~~~~~~~

URL configuration for the accounts application.

This module defines the URL patterns that route incoming HTTP
requests to the appropriate view functions within the accounts app.
"""

from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="accounts_home"),
]
