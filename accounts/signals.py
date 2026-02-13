"""
accounts.signals
~~~~~~~~~~~~~~~~

Automatically create Employee profile for superusers.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Employee


@receiver(post_save, sender=User)
def create_employee_for_superuser(sender, instance, created, **kwargs):
    """
    Automatically create an Employee profile when a superuser is created.
    """
    if created and instance.is_superuser:
        Employee.objects.create(
            user=instance,
            role=Employee.SUPER_ADMIN,
            is_verified=True,
        )
