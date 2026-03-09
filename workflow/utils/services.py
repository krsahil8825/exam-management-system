"""
workflow.utils.services
~~~~~~~~~~~~~~~~~~~~~~~

This module contains service functions for managing workflow tasks, including creation, updates, and status transitions. These functions encapsulate business logic and ensure proper validation and atomic operations on tasks.

"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction

from accounts.models import Employee
from ..models import Task


def _get_employee(user):
    """Return the employee profile for a non-superuser."""
    if user.is_superuser:
        return None

    employee = getattr(user, "employee_profile", None)
    if employee is None:
        raise ValidationError("Only employees can perform this action.")

    return employee


def _transition_task(task, *, from_status, to_status, completed_at):
    """Perform an atomic status transition and return the refreshed task."""
    updated_at = timezone.now()
    with transaction.atomic():
        updated = Task.objects.filter(pk=task.pk, status=from_status).update(
            status=to_status,
            completed_at=completed_at,
            updated_at=updated_at,
        )
    if not updated:
        raise ValidationError("Task status changed. Refresh and try again.")

    task.refresh_from_db()
    return task


def create_task(
    *,
    user,
    assigned_to,
    title,
    description,
    due_date=None,
    priority=Task.Priority.MEDIUM,
):
    """Create a new task assigned by the requesting employee."""
    assigned_by = _get_employee(user)
    if assigned_by is None:
        raise ValidationError("Superusers must provide an employee creator.")

    if not isinstance(assigned_to, Employee):
        raise ValidationError("A valid assignee employee is required.")

    task = Task(
        assigned_by=assigned_by,
        assigned_to=assigned_to,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        status=Task.Status.PENDING,
    )
    task.save()
    return task


def update_task_details(task, user, *, title=None, description=None, due_date=None):
    """Allow creator to edit task details while task is pending."""
    employee = _get_employee(user)

    if employee is not None and employee != task.assigned_by:
        raise ValidationError("Only the creator can edit task details.")

    if task.status != task.Status.PENDING:
        raise ValidationError("Task can only be edited while pending.")

    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if due_date is not None:
        task.due_date = due_date

    task.save()
    return task


def cancel_task(task, user):
    """Cancel a pending or in-progress task."""
    employee = _get_employee(user)

    if employee is not None and employee not in (task.assigned_by, task.assigned_to):
        raise ValidationError("You cannot cancel this task.")

    if task.status not in (task.Status.PENDING, task.Status.IN_PROGRESS):
        raise ValidationError("Only pending or in-progress tasks can be cancelled.")

    return _transition_task(
        task,
        from_status=task.status,
        to_status=task.Status.CANCELLED,
        completed_at=None,
    )


def start_task(task, user):
    """Move task from pending to in-progress."""
    employee = _get_employee(user)

    if employee is not None and employee != task.assigned_to:
        raise ValidationError("Only the assignee can start the task.")

    if task.status != task.Status.PENDING:
        raise ValidationError("Task must be pending to start.")

    return _transition_task(
        task,
        from_status=task.Status.PENDING,
        to_status=task.Status.IN_PROGRESS,
        completed_at=None,
    )


def complete_task(task, user):
    """Move task from in-progress to completed."""
    employee = _get_employee(user)

    if employee is not None and employee != task.assigned_to:
        raise ValidationError("Only the assignee can complete the task.")

    if task.status != task.Status.IN_PROGRESS:
        raise ValidationError("Task must be in progress to complete.")

    return _transition_task(
        task,
        from_status=task.Status.IN_PROGRESS,
        to_status=task.Status.COMPLETED,
        completed_at=timezone.now(),
    )
