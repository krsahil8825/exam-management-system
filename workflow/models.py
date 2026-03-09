"""
workflow.models
~~~~~~~~~~~~~~~

Data models for internal work assignment and tracking.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import Employee


def generate_task_code() -> str:
    """Return a short, globally unique public task code."""
    return f"TASK-{uuid.uuid4().hex[:12].upper()}"


class Task(models.Model):
    """Task assigned from one employee to another."""

    class Status(models.TextChoices):
        """Task status options."""

        PENDING = "P", "Pending"
        IN_PROGRESS = "IP", "In Progress"
        COMPLETED = "C", "Completed"
        CANCELLED = "X", "Cancelled"

    class Priority(models.TextChoices):
        """Task priority levels."""

        LOW = "L", "Low"
        MEDIUM = "M", "Medium"
        HIGH = "H", "High"

    task_code = models.CharField(
        max_length=17,
        unique=True,
        editable=False,
        default=generate_task_code,
        db_index=True,
        help_text="Immutable public identifier for the task.",
    )

    assigned_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="tasks_created",
    )
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="tasks_received",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    priority = models.CharField(
        max_length=1,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )

    due_date = models.DateTimeField(blank=True, null=True, db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta configuration for Task model."""

        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(assigned_by=models.F("assigned_to")),
                name="workflow_task_assigned_by_ne_assigned_to",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def clean(self):
        """Validate task ownership and timeline consistency."""
        super().clean()

        if self.assigned_by_id and self.assigned_by_id == self.assigned_to_id:
            raise ValidationError("A task cannot be assigned to the same employee.")

        if self.due_date and self.due_date <= timezone.now() and not self.pk:
            raise ValidationError("Due date must be in the future for new tasks.")

        if self.status != self.Status.COMPLETED and self.completed_at:
            raise ValidationError(
                {
                    "completed_at": "Only completed tasks can have a completion timestamp."
                }
            )

    def save(self, *args, **kwargs):
        """Automatically set or clear completed_at based on status changes and ensure validation."""
        
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.Status.COMPLETED:
            self.completed_at = None

        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Return a human-readable string representation of the task."""
        title = self.title[:30]
        if len(self.title) > 30:
            title += "..."
        return f"{self.task_code} - {title}"
