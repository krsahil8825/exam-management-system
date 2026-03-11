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
from django.utils import timezone
from datetime import timedelta

from .managers import UserManager
from .utils.validate import (
    country_code_validator,
    phone_validator,
    validate_profile_photo,
)


def user_profile_picture_path(instance, filename):
    """Return a stable and safe upload path for profile photos."""

    _, extension = os.path.splitext(filename)
    extension = extension.lstrip(".").lower()
    name = f"{instance.first_name or 'user'}_{instance.last_name or ''}".strip().lower()
    email_prefix = (instance.email or "user").split("@")[0].lower()
    unique_prefix = uuid.uuid4().hex[:20]

    while True:
        path = f"profile_pictures/{email_prefix}/{unique_prefix}_{name}.{extension}"
        if not instance.profile_picture.storage.exists(path):
            return path
        unique_prefix = uuid.uuid4().hex[:20]


def otp_expiry_time():
    """Return default OTP expiration time (10 minutes from now)."""
    return timezone.now() + timedelta(minutes=10)


class User(AbstractUser):
    """Custom authentication model using email as the username field."""

    class GenderChoices(models.TextChoices):
        """Standardized gender options for user profiles."""

        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    objects = UserManager()

    username = None

    country_code = models.CharField(max_length=5, validators=[country_code_validator])
    phone = models.CharField(max_length=20, unique=True, validators=[phone_validator])
    email = models.EmailField(unique=True)
    gender = models.CharField(
        max_length=1, choices=GenderChoices.choices, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        validators=[validate_profile_photo],
    )

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # used for 2FA using TOTP (authenticator apps)
    is_2FA_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(
        max_length=255, blank=True, null=True, editable=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["country_code", "phone", "first_name", "last_name"]

    def clean(self):
        """Normalize email and phone fields, and enforce required fields when phone is provided."""
        super().clean()
        if self.email:
            self.email = self.email.strip().lower()

        self.country_code = (self.country_code or "").strip().replace(" ", "")
        self.phone = (self.phone or "").strip().replace(" ", "")

        if self.phone and not self.country_code:
            raise ValidationError("Country code is required when phone is provided.")

    def save(self, *args, **kwargs):
        """
        Override save to:
        - Reset verification flags when email/phone changes
        - Enforce required contact fields
        - Automatically configure superusers
        - Validate model data
        - Remove old profile pictures when updated
        """

        is_raw_save = kwargs.get("raw", False)

        old = self.__class__.objects.filter(pk=self.pk).first()

        # Reset verification flags
        if old and not self.is_superuser:
            new_email = (self.email or "").strip().lower()
            old_email = (old.email or "").strip().lower()

            if new_email != old_email:
                self.email_verified = False

            phone_changed = (self.phone or "") != (old.phone or "")
            code_changed = (self.country_code or "") != (old.country_code or "")

            if phone_changed or code_changed:
                self.phone_verified = False

            if not self.email or not self.phone or not self.country_code:
                raise ValidationError(
                    "Email, phone, and country code are required fields."
                )

        # Superuser defaults
        if self.is_superuser:
            self.is_staff = True
            self.email_verified = True
            self.phone_verified = True

        # Model validation
        if not is_raw_save:
            self.full_clean()

        # Delete old profile picture
        if old and old.profile_picture and old.profile_picture != self.profile_picture:
            storage = old.profile_picture.storage
            if storage.exists(old.profile_picture.name):
                storage.delete(old.profile_picture.name)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to also remove the associated profile picture file."""
        if self.profile_picture:
            storage = self.profile_picture.storage
            if storage.exists(self.profile_picture.name):
                storage.delete(self.profile_picture.name)

        super().delete(*args, **kwargs)

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


class OTP(models.Model):
    """Model to store OTPs for various verification purposes."""

    class OTPPurpose(models.TextChoices):
        """Standardized OTP purposes for verification processes."""

        EMAIL_VERIFY = "EMAIL_VERIFY", "Email Verification"
        PHONE_VERIFY = "PHONE_VERIFY", "Phone Verification"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        EMAIL_CHANGE = "EMAIL_CHANGE", "Email Change"
        PHONE_CHANGE = "PHONE_CHANGE", "Phone Change"
        SET_2FA = "SET_2FA", "Set Two-Factor Authentication"
        REMOVE_2FA = "REMOVE_2FA", "Remove Two-Factor Authentication"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otps",
    )

    purpose = models.CharField(max_length=50, choices=OTPPurpose.choices)

    otp = models.CharField(max_length=256)  # Store hashed OTP for security

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=otp_expiry_time)

    class Meta:
        """Define indexes for efficient OTP management."""

        indexes = [
            models.Index(fields=["user", "purpose", "expires_at", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        """
        Save OTP with rate limiting and storage optimization.

        Rules:
        - Each (user, purpose) has its own rate limit.
        - Maximum LIMIT_RATE OTPs allowed within RATE_LIMIT_WINDOW.
        - If limit reached within window -> block new OTP.
        - While saving, keep only latest LIMIT_RATE OTPs by deleting oldest.
        """

        LIMIT_RATE = 12
        RATE_LIMIT_WINDOW = timedelta(hours=1)

        if self.pk:
            return super().save(*args, **kwargs)

        now = timezone.now()

        qs = OTP.objects.filter(user=self.user, purpose=self.purpose).order_by(
            "-created_at"
        )

        recent_count = qs.filter(created_at__gte=now - RATE_LIMIT_WINDOW).count()

        if recent_count >= LIMIT_RATE:
            raise ValidationError("OTP request limit exceeded. Try again later.")

        # Storage optimization
        total_count = qs.count()

        if total_count >= LIMIT_RATE:
            oldest_to_delete = qs.last()
            oldest_to_delete.delete()

        super().save(*args, **kwargs)


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
        """Override save to generate a unique employee_id if not set."""

        if not self.employee_id:
            self.employee_id = self._next_employee_id()

        return super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the employee."""
        return f"Employee: {self.user.email} ({self.get_role_display()})"
