"""
accounts.models
~~~~~~~~~~~~~~~

Defines the custom User model with email-based authentication, along with related Address, Candidate, and Employee profile models. Includes validation logic for user data and profile photos.
"""

import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .managers import UserManager
from .utils.validate import (
    country_code_validator,
    phone_validator,
    validate_profile_photo,
)


class GenderChoices(models.TextChoices):
    """Standardized gender options for user profiles."""

    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


def user_profile_picture_path(instance, filename):
    """Return a stable and safe upload path for profile photos."""
    base_name = os.path.basename(filename)
    email_prefix = (instance.email or "user").split("@")[0].lower()
    unique_prefix = uuid.uuid4().hex[:12]
    return f"profile_pictures/{email_prefix}/{unique_prefix}_{base_name}"


class User(AbstractUser):
    """Custom authentication model using email as the username field."""

    objects = UserManager()

    username = None

    country_code = models.CharField(max_length=5, validators=[country_code_validator])
    phone = models.CharField(max_length=20, unique=True, validators=[phone_validator])
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        validators=[validate_profile_photo],
    )

    email_OTP = models.CharField(max_length=6, blank=True, null=True, editable=False)
    email_OTP_created_at = models.DateTimeField(blank=True, null=True, editable=False)
    phone_OTP = models.CharField(max_length=6, blank=True, null=True, editable=False)
    phone_OTP_created_at = models.DateTimeField(blank=True, null=True, editable=False)
    password_otp = models.CharField(max_length=6, blank=True, null=True, editable=False)
    password_otp_created_at = models.DateTimeField(
        blank=True, null=True, editable=False
    )

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["country_code", "phone", "first_name", "last_name"]

    def clean(self):
        """Normalize email and phone fields, and enforce required fields when phone is provided."""
        super().clean()
        if self.email:
            self.email = self.email.strip().lower()

        self.country_code = (self.country_code or "").strip()
        self.phone = (self.phone or "").strip()

        if self.phone and not self.country_code:
            raise ValidationError("Country code is required when phone is provided.")

    def save(self, *args, **kwargs):
        """Override save to handle email normalization, verification status resets, and superuser defaults."""
        is_raw_save = kwargs.get("raw", False)

        if not is_raw_save and self.pk and not self.is_superuser:
            previous = (
                type(self)
                .objects.filter(pk=self.pk)
                .values("email", "phone", "country_code")
                .first()
            )
            if previous:
                current_email = (self.email or "").strip().lower()
                previous_email = (previous["email"] or "").strip().lower()
                if current_email != previous_email:
                    self.email_verified = False

                phone_changed = (self.phone or "") != (previous["phone"] or "")
                country_code_changed = (self.country_code or "") != (
                    previous["country_code"] or ""
                )
                if phone_changed or country_code_changed:
                    self.phone_verified = False

                if not self.email or not self.phone or not self.country_code:
                    raise ValidationError(
                        "Email, phone, and country code are required fields."
                    )

        if self.is_superuser:
            self.is_staff = True
            self.email_verified = True
            self.phone_verified = True

        if not is_raw_save:
            self.full_clean()

        return super().save(*args, **kwargs)

    def __str__(self):
        """Return the email as the string representation of the user."""
        return self.email


class Address(models.Model):
    """Stores one normalized address per user."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="address",
    )
    street1 = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        """Return a string representation of the address."""
        return f"{self.user.email} - {self.city}"


class Candidate(models.Model):
    """Profile model for exam candidates."""

    class EducationLevel(models.TextChoices):
        """Standardized education level options for candidate profiles."""

        BACHELORS = "B", "Bachelor's Degree"
        MASTERS = "M", "Master's Degree"
        PHD = "P", "PhD"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    candidate_id = models.CharField(max_length=50, unique=True, editable=False)
    education_level = models.CharField(
        max_length=1,
        choices=EducationLevel.choices,
        default=EducationLevel.BACHELORS,
    )
    university_name = models.CharField(max_length=255)
    enrollment_number = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=255)
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GenderChoices.choices)

    @classmethod
    def _next_candidate_id(cls):
        """Generate a unique candidate ID in the format CAND-XXXXXXXXXXXX where X is a hexadecimal character."""
        while True:
            candidate_id = f"CAND-{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(candidate_id=candidate_id).exists():
                return candidate_id

    def clean(self):
        """Ensure that a user cannot have both Candidate and Employee profiles, and that the candidate_id is unique if set."""
        super().clean()
        if self.user_id and Employee.objects.filter(user_id=self.user_id).exists():
            raise ValidationError("This user already has an Employee profile.")

    def save(self, *args, **kwargs):
        """Override save to generate a unique candidate_id if not set."""
        if not self.candidate_id:
            self.candidate_id = self._next_candidate_id()

        return super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the candidate."""
        return f"Candidate: {self.user.email}"


class Employee(models.Model):
    """Profile model for employees managing exams."""

    class RoleChoices(models.TextChoices):
        """Standardized role options for employee profiles."""

        NOT_ASSIGNED = "NA", "Not Assigned"
        SUPER_ADMIN = "SA", "Super Admin"
        ADMIN = "AD", "Admin"
        MANAGER = "MG", "Manager"
        EXAMINER = "EX", "Examiner"
        INVIGILATOR = "IN", "Invigilator"
        ASSISTANT = "AS", "Assistant"

    class DepartmentChoices(models.TextChoices):
        """Standardized department options for employee profiles."""

        NOT_ALLOCATED = "NA", "Not Allocated"
        HR = "HR", "Human Resources"
        DEVELOPMENT = "DEV", "Development"
        SALES = "SALES", "Sales"
        MARKETING = "MKT", "Marketing"
        MANAGEMENT = "MGMT", "Management"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    employee_id = models.CharField(max_length=50, unique=True, editable=False)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices)
    role = models.CharField(
        max_length=2,
        choices=RoleChoices.choices,
        default=RoleChoices.NOT_ASSIGNED,
    )
    department = models.CharField(
        max_length=5,
        choices=DepartmentChoices.choices,
        default=DepartmentChoices.NOT_ALLOCATED,
    )
    additional_info = models.TextField(blank=True, null=True)

    @classmethod
    def _next_employee_id(cls):
        """Generate a unique employee ID in the format EMP-XXXXXXXXXXXX where X is a hexadecimal character."""
        while True:
            employee_id = f"EMP-{uuid.uuid4().hex[:12].upper()}"
            if not cls.objects.filter(employee_id=employee_id).exists():
                return employee_id

    def clean(self):
        """Ensure that a user cannot have both Employee and Candidate profiles, and that the employee_id is unique if set."""
        super().clean()
        if self.user_id and Candidate.objects.filter(user_id=self.user_id).exists():
            raise ValidationError("This user already has a Candidate profile.")

    def save(self, *args, **kwargs):
        """Override save to generate a unique employee_id if not set, and set defaults for superusers."""
        if self.user and self.user.is_superuser:
            self.gender = GenderChoices.MALE
            self.role = self.RoleChoices.SUPER_ADMIN

        if not self.employee_id:
            self.employee_id = self._next_employee_id()

        return super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the employee."""
        return f"Employee: {self.user.email} ({self.get_role_display()})"
