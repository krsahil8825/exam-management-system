"""
accounts.models

This module defines the User model for the accounts application.
It extends Django's AbstractUser to allow for future customization
of user fields and behavior.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    """
