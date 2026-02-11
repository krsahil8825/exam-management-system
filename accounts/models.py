"""
accounts.models

This module defines the data models for the accounts app, including:
- User: Custom user model extending Django's AbstractUser.
- Candidate: Profile for students registering for exams.
- Employee: Profile for staff managing exams.
- Address: Separate model for user addresses.
- Task: Represents tasks assigned between employees.
- Message: Represents direct messages between users.

These models are designed to support the functionality of an online examination
system, allowing for user authentication, profile management, task assignment,
and communication between users.
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
import random


# =========================================================
# Utility Function
# =========================================================
def user_profile_picture_path(instance, filename):
    """
    Dynamic upload path for user profile pictures.
    Files will be stored as:
        profile_pictures/<username>/<filename>
    """
    return f"profile_pictures/{instance.username}/{filename}"


# =========================================================
# Address Model
# =========================================================
class Address(models.Model):
    """
    Stores address information for a user.
    Separated for normalization and reusability.
    """

    street1 = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street1}, {self.city}, {self.state}"


# =========================================================
# Custom User Model
# =========================================================
class User(AbstractUser):
    """
    Base user model.
    Acts as authentication layer for both Candidate and Employee.
    """
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path, blank=True, null=True
    )

    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# =========================================================
# Candidate Profile
# =========================================================
class Candidate(models.Model):
    """
    Candidate profile for students registering for exams.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="candidate_profile"
    )

    # Candidate-specific fields automatically generated in views
    application_number = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20, unique=True)
    exam_key = models.CharField(max_length=50, unique=True)

    # Academic Information
    HIGH_SCHOOL = "HS"
    BACHELORS = "BA"
    MASTERS = "MA"
    PHD = "PHD"

    EDUCATION_LEVEL_CHOICES = [
        (HIGH_SCHOOL, "High School"),
        (BACHELORS, "Bachelor's Degree"),
        (MASTERS, "Master's Degree"),
        (PHD, "PhD"),
    ]

    education_level = models.CharField(
        max_length=3, choices=EDUCATION_LEVEL_CHOICES, default=HIGH_SCHOOL
    )

    university_name = models.CharField(max_length=255)
    enrollment_number = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=255)
    semester = models.PositiveIntegerField()

    # Personal Information
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Prevents a user from having both Candidate and Employee profiles.
        """
        if hasattr(self.user, "employee_profile"):
            raise ValidationError("This user already has an Employee profile.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Candidate: {self.user.username}"


# =========================================================
# Employee Profile
# =========================================================
class Employee(models.Model):
    """
    Employee profile for staff managing exams.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_profile"
    )

    # Employee-specific fields automatically generated
    employee_id = models.CharField(max_length=50, unique=True)

    # Roles
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

    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default=NOT_ASSIGNED)

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
        max_length=255, choices=DEPARTMENT_CHOICES, default=NOT_ALLOCATED
    )

    is_verified = models.BooleanField(default=False)
    additional_info = models.TextField(blank=True, null=True)

    def _generate_employee_id(self):
        """
        Generates a unique employee ID based on the role and a random number.
        Format: <ROLE_PREFIX><RANDOM_NUMBER>
        Example: AD123456 for an Admin.
        """
        role_prefix = self.role if self.role != self.NOT_ASSIGNED else "EMP"
        random_number = random.randint(100000, 999999)

        # Ensure uniqueness of the generated employee ID
        while Employee.objects.filter(
            employee_id=f"{role_prefix}-{random_number}"
        ).exists():
            random_number = random.randint(100000, 999999)

        return f"{role_prefix}-{random_number}"

    def save(self, *args, **kwargs):
        """
        Prevents a user from having both Candidate and Employee profiles.

        Also handles employee ID generation and updates based on role changes.
        """
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
        return f"Employee: {self.user.username} ({self.get_role_display()})"


# =========================================================
# Task Model
# =========================================================
class Task(models.Model):
    """
    Represents a task assigned between employees.
    """

    # Who created/assigned the task
    assigned_by = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="tasks_created"
    )

    # Who receives the task
    assigned_to = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="tasks_received"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Status choices
    PENDING = "P"
    IN_PROGRESS = "IP"
    COMPLETED = "C"
    CANCELLED = "X"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)

    # Priority choices
    LOW = "L"
    MEDIUM = "M"
    HIGH = "H"

    PRIORITY_CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]

    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default=MEDIUM)

    due_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Prevent employee from assigning task to themselves.
        """
        if self.assigned_by == self.assigned_to:
            raise ValidationError("Employee cannot assign task to themselves.")

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


# =========================================================
# Message Model
# =========================================================
class Message(models.Model):
    """
    Direct message between users.
    """

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )

    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )

    content = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Prevent users from messaging themselves.
        """
        if self.sender == self.receiver:
            raise ValidationError("User cannot message themselves.")

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
