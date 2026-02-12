"""
communication.models
~~~~~~~~~~~~~~~~~~~~

Defines models related to internal communication between employees.

This module currently includes:
- Message: Represents direct employee-to-employee communication.

The design intentionally limits messaging to Employee profiles
to maintain clear domain boundaries and internal communication control.
"""

import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from accounts.models import Employee


# =========================================================
# Utility Function
# =========================================================
def message_attachment_path(instance, filename):
    """Return the upload path for a message attachment."""
    sender_id = instance.sender.employee_id
    receiver_id = instance.receiver.employee_id
    return f"message_attachments/{sender_id}_{receiver_id}/{filename}"


# =========================================================
# Message Model
# =========================================================
class Message(models.Model):
    """Model representing a message between two employees."""

    sender = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )

    receiver = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text="Unique identifier used for URL-based message access.",
    )

    subject = models.CharField(max_length=200)
    content = models.TextField()

    attachment = models.FileField(
        upload_to=message_attachment_path,
        blank=True,
        null=True,
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Model configuration."""

        ordering = ["-created_at"]

    def clean(self):
        """Ensure sender and receiver are not the same."""
        if self.sender == self.receiver:
            raise ValidationError("Employee cannot message themselves.")

    def save(self, *args, **kwargs):
        """Handle slug generation and validation before saving."""
        if not self.slug:
            unique_id = uuid.uuid4().hex[:8]
            self.slug = slugify(f"{self.subject}-{unique_id}")

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a readable message representation."""
        return (
            f"{self.sender.user.username} → "
            f"{self.receiver.user.username} "
            f"({self.subject[:30]})"
        )
