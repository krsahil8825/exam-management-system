"""
managers.py
~~~~~~~~~~~

Custom manager responsible for creating users and superusers.
"""

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user.
        """

        if not email:
            raise ValueError("Email must be provided")

        if not password:
            raise ValueError("Password must be provided")

        if not extra_fields.get("phone"):
            raise ValueError("Phone must be provided")

        if not extra_fields.get("country_code"):
            raise ValueError("Country code must be provided")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser and automatically
        create the Employee profile.
        """

        from .models import Employee

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValidationError("Superuser must have is_superuser=True")

        user = self.create_user(email, password, **extra_fields)

        # Create employee profile automatically
        Employee.objects.create(
            user=user,
            gender=Employee.MALE,
            role=Employee.SUPER_ADMIN,
            department=Employee.MANAGEMENT,
        )

        return user
