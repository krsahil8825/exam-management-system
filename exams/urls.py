"""
exams.urls
~~~~~~~~~~
This module defines URL patterns for the exams app, 
including routes for viewing the home page and managing exams.
"""

from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="exams_home"),
]
