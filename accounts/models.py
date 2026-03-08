"""
accounts.models
~~~~~~~~~~~~~~~

Defines the core data models for the accounts application.

This module includes:
- User: Custom authentication model extending AbstractUser.
- Candidate: Profile model for exam applicants.
- Employee: Profile model for staff members managing exams.
- Address: Normalized model for storing user address information.

The architecture separates authentication (User) from
domain-specific roles (Candidate and Employee) to ensure
clean design and enforce role-based constraints.
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
import uuid

from .managers import UserManager


# =========================================================
# Utility Function
# =========================================================
def user_profile_picture_path(instance, filename):
    """Return the upload path for a user's profile picture."""
    folder_name = str(instance).replace("@", "_at_").replace(".", "_dot_")
    return f"profile_pictures/{folder_name}/{filename}"


# =========================================================
# Custom User Model
# =========================================================
class User(AbstractUser):
    """Custom user model for authentication and profile linkage."""

    objects = UserManager()

    username = None

    country_code = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
    )

    # OTP fields for email and phone verification
    email_OTP = models.CharField(max_length=6, blank=True, null=True, editable=False)
    email_OTP_created_at = models.DateTimeField(blank=True, null=True, editable=False)
    phone_OTP = models.CharField(max_length=6, blank=True, null=True, editable=False)
    phone_OTP_created_at = models.DateTimeField(blank=True, null=True, editable=False)

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Important settings
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "country_code",
        "phone",
    ]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.email_verified = True
            self.phone_verified = True
            self.is_staff = True

        super().save(*args, **kwargs)

    def __str__(self):
        """Return the email."""
        return self.email


# =========================================================
# Address Model
# =========================================================
class Address(models.Model):
    """Model representing a user's address."""

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
        return f"{self.user.email} - {self.city}"


# =========================================================
# Candidate Profile
# =========================================================
class Candidate(models.Model):
    """Profile model for exam candidates."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )

    candidate_id = models.CharField(max_length=50, unique=True, editable=False)

    BACHELORS = "B"
    MASTERS = "M"
    PHD = "P"

    EDUCATION_LEVEL_CHOICES = [
        (BACHELORS, "Bachelor's Degree"),
        (MASTERS, "Master's Degree"),
        (PHD, "PhD"),
    ]

    education_level = models.CharField(
        max_length=1,
        choices=EDUCATION_LEVEL_CHOICES,
        default=BACHELORS,
    )

    university_name = models.CharField(max_length=255)
    enrollment_number = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=255)
    semester = models.PositiveIntegerField()

    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    dob = models.DateField()
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    gender_choices = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    gender = models.CharField(max_length=1, choices=gender_choices)

    def _generate_candidate_id(self):
        """Generate a unique candidate ID."""
        ID_PREFIX = "CAND"

        ID_SUFFIX = str(uuid.uuid4().hex[:12]).upper()

        return f"{ID_PREFIX}-{ID_SUFFIX}"

    def save(self, *args, **kwargs):
        """Ensure a user does not have both Candidate and Employee profiles."""
        if hasattr(self.user, "employee_profile"):
            raise ValidationError("This user already has an Employee profile.")

        if not self.candidate_id:
            self.candidate_id = self._generate_candidate_id()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable candidate representation."""
        return f"Candidate: {self.user.email}"


# =========================================================
# Employee Profile
# =========================================================
class Employee(models.Model):
    """Profile model for employees managing exams."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    employee_id = models.CharField(max_length=50, unique=True, editable=False)

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    gender_choices = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    gender = models.CharField(max_length=1, choices=gender_choices)

    NOT_ASSIGNED = "NA"
    SUPER_ADMIN = "SA"
    ADMIN = "AD"
    MANAGER = "MG"
    EXAMINER = "EX"
    INVIGILATOR = "IN"
    ASSISTANT = "AS"

    ROLE_CHOICES = [
        (NOT_ASSIGNED, "Not Assigned"),
        (SUPER_ADMIN, "Super Admin"),
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (EXAMINER, "Examiner"),
        (INVIGILATOR, "Invigilator"),
        (ASSISTANT, "Assistant"),
    ]

    role = models.CharField(
        max_length=2,
        choices=ROLE_CHOICES,
        default=NOT_ASSIGNED,
    )

    NOT_ALLOCATED = "NA"
    HR = "HR"
    DEVELOPMENT = "DEV"
    SALES = "SALES"
    MARKETING = "MKT"
    MANAGEMENT = "MGMT"

    DEPARTMENT_CHOICES = [
        (NOT_ALLOCATED, "Not Allocated"),
        (HR, "Human Resources"),
        (DEVELOPMENT, "Development"),
        (SALES, "Sales"),
        (MARKETING, "Marketing"),
        (MANAGEMENT, "Management"),
    ]

    department = models.CharField(
        max_length=5,
        choices=DEPARTMENT_CHOICES,
        default=NOT_ALLOCATED,
    )

    additional_info = models.TextField(blank=True, null=True)

    def _generate_employee_id(self):
        """Generate a unique employee ID."""
        ID_PREFIX = "EMP"
        ID_SUFFIX = str(uuid.uuid4().hex[:12]).upper()
        return f"{ID_PREFIX}-{ID_SUFFIX}"

    def save(self, *args, **kwargs):
        """Ensure a user does not have both Employee and Candidate profiles, and handle role-based logic."""

        if hasattr(self.user, "candidate_profile"):
            raise ValidationError("This user already has a Candidate profile.")

        # Set gender to Male by default to avoid validation errors when creating superusers.
        # Superusers can change it later since they have full permissions.
        if self.user.is_superuser:
            self.gender = self.MALE

        if self.user.is_staff and self.user.is_superuser:
            self.role = self.SUPER_ADMIN

        if not self.employee_id:
            self.employee_id = self._generate_employee_id()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable employee representation."""
        return f"Employee: {self.user.email} ({self.get_role_display()})"
