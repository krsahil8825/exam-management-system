"""
exams.views
~~~~~~~~~~~

This module contains views related to exam management, including creating,
updating, and viewing exams.
"""

from django.http import HttpResponse

def home(request):
    """
    Home view for the exams app.
    """
    return HttpResponse(
        "Welcome to the Exam Management System! This is your dashboard. Soon, you will see your profile information or upcoming exams"
    )