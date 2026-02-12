"""
workflow.models
~~~~~~~~~~~~~~~

Defines models responsible for managing internal workflow
within the exam management system.

This module currently includes:
- Task: Represents work assigned between employees.

The workflow system allows structured task assignment,
status tracking, and priority management among staff members.
"""

import uuid

from django.db import models
from django.core.exceptions import ValidationError

from accounts.models import Employee


# =========================================================
# Task Model
# =========================================================
class Task(models.Model):
    """
    Model representing a task assigned between employees.
    """

    assigned_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="tasks_created",
    )

    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="tasks_received",
    )

    slug = models.SlugField(
        unique=True,
        editable=False,
        help_text="Unique identifier for the task (starts with 'TASK-').",
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

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    # Priority choices
    LOW = "L"
    MEDIUM = "M"
    HIGH = "H"

    PRIORITY_CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]

    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default=MEDIUM,
    )

    due_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model configuration."""

        ordering = ["-created_at"]

    def clean(self):
        """Ensure a task is not assigned to the same employee."""
        if self.assigned_by == self.assigned_to:
            raise ValidationError("Employee cannot assign task to themselves.")

    def save(self, *args, **kwargs):
        """Generate a unique slug if not already set."""
        if not self.slug:
            while True:
                unique_part = uuid.uuid4().hex[:10]
                generated_slug = f"TASK-{unique_part}"

                if not Task.objects.filter(slug=generated_slug).exists():
                    self.slug = generated_slug
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        """Return task title and status."""
        return f"{self.title} ({self.get_status_display()})"
