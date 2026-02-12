"""
communication.urls
~~~~~~~~~~~~~~~~~~

URL patterns for the communication application.

This module maps URL paths to their corresponding view functions.
"""

from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="communication_home"),
]
