"""
workflow.urls
~~~~~~~~~~~~~

URL patterns for the workflow application.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='workflow_home'),
]