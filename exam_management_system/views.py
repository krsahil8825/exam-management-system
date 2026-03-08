"""
exam_management_system.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It contains the home page view and the about page view.
"""

from django.shortcuts import render


def index(request):
    """
    Index Page Views
    """
    return render(request, "index.html")
