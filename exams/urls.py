"""
exams.urls
~~~~~~~~~~

URL patterns for the exams application.
"""

from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="exams_home"),
]
