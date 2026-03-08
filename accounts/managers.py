"""
accounts.managers
~~~~~~~~~~~~~~~~~

Custom user manager for regular and superuser creation.
"""

from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction


class UserManager(BaseUserManager):
    """Manager that enforces required fields for the custom User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and persist a regular user."""
        if not email:
            raise ValueError("Email must be provided.")
        if not password:
            raise ValueError("Password must be provided.")
        if not extra_fields.get("phone"):
            raise ValueError("Phone must be provided.")
        if not extra_fields.get("country_code"):
            raise ValueError("Country code must be provided.")

        email = self.normalize_email(email).strip().lower()
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    @transaction.atomic
    def create_superuser(self, email, password=None, **extra_fields):
        """Create superuser and ensure an employee profile exists."""
        from .models import Employee, GenderChoices

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)

        Employee.objects.get_or_create(
            user=user,
            defaults={
                "gender": GenderChoices.MALE,
                "role": Employee.RoleChoices.SUPER_ADMIN,
                "department": Employee.DepartmentChoices.MANAGEMENT,
            },
        )
        return user
