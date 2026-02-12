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
import random


# =========================================================
# Utility Function
# =========================================================
def user_profile_picture_path(instance, filename):
    """Return the upload path for a user's profile picture."""
    return f"profile_pictures/{instance.username}/{filename}"


# =========================================================
# Address Model
# =========================================================
class Address(models.Model):
    """Model representing a user's address."""

    street1 = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        """Return a readable address string."""
        return f"{self.street1}, {self.city}, {self.state}"


# =========================================================
# Custom User Model
# =========================================================
class User(AbstractUser):
    """Custom user model for authentication and profile linkage."""

    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
    )

    email_verified = models.BooleanField(default=False)

    def __str__(self):
        """Return the username."""
        return self.username


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

    application_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20, unique=True)
    exam_key = models.CharField(max_length=50, unique=True)

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

    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Ensure a user does not have both Candidate and Employee profiles."""
        if hasattr(self.user, "employee_profile"):
            raise ValidationError("This user already has an Employee profile.")

        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable candidate representation."""
        return f"Candidate: {self.user.username}"


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

    employee_id = models.CharField(max_length=50, unique=True)

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
        max_length=255,
        choices=DEPARTMENT_CHOICES,
        default=NOT_ALLOCATED,
    )

    is_verified = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True, null=True)

    def _generate_employee_id(self):
        """Generate a unique employee ID."""
        role_prefix = self.role if self.role != self.NOT_ASSIGNED else "EMP"
        random_number = random.randint(100000, 999999)

        while Employee.objects.filter(
            employee_id=f"{role_prefix}-{random_number}"
        ).exists():
            random_number = random.randint(100000, 999999)

        return f"{role_prefix}-{random_number}"

    def save(self, *args, **kwargs):
        """Handle role validation and employee ID generation."""
        if hasattr(self.user, "candidate_profile"):
            raise ValidationError("This user already has a Candidate profile.")

        if self.pk:
            old_instance = Employee.objects.get(pk=self.pk)

            if old_instance.role != self.role:
                self.employee_id = self._generate_employee_id()
            else:
                self.employee_id = old_instance.employee_id
        else:
            if not self.employee_id:
                self.employee_id = self._generate_employee_id()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable employee representation."""
        return f"Employee: {self.user.username} ({self.get_role_display()})"
