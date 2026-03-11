"""
workflow.forms
~~~~~~~~~~~~~

Forms for creating and editing workflow tasks. These forms handle input validation and delegate business logic to the service layer for task management.
"""

from django import forms
from django.utils import timezone

from accounts.models import Employee
from .models import Task
from .utils.services import create_task, update_task_details


class BaseTaskForm(forms.Form):
    """Shared task fields used for task creation and editing."""

    title = forms.CharField(
        label="Title",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Task title"}
        ),
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Task description",
            }
        ),
    )

    priority = forms.ChoiceField(
        label="Priority",
        choices=Task.Priority.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    due_date = forms.DateTimeField(
        label="Due Date",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"class": "form-control", "type": "datetime-local"}
        ),
    )

    def clean_title(self):
        """Normalize title."""
        return self.cleaned_data["title"].strip()

    def clean_description(self):
        """Normalize description."""
        return self.cleaned_data["description"].strip()

    def clean_due_date(self):
        """Ensure due date is in the future."""
        due_date = self.cleaned_data.get("due_date")

        if due_date and due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")

        return due_date


class TaskCreateForm(BaseTaskForm):
    """Form used to create new tasks."""

    assigned_to = forms.ModelChoiceField(
        label="Assign To",
        queryset=Employee.objects.select_related("user"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        """Initialize form with requesting user."""
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        """Ensure creator is not assigning task to themselves."""
        cleaned_data = super().clean()

        assigned_to = cleaned_data.get("assigned_to")

        employee = getattr(self.user, "employee_profile", None)

        if employee and assigned_to and employee.pk == assigned_to.pk:
            raise forms.ValidationError(
                "A task cannot be assigned to the same employee."
            )

        return cleaned_data

    def save(self):
        """Create a task using workflow service layer."""
        return create_task(
            user=self.user,
            assigned_to=self.cleaned_data["assigned_to"],
            title=self.cleaned_data["title"],
            description=self.cleaned_data["description"],
            priority=self.cleaned_data["priority"],
            due_date=self.cleaned_data.get("due_date"),
        )


class TaskEditForm(BaseTaskForm):
    """Form used to edit task details."""

    def __init__(self, *args, task=None, user=None, **kwargs):
        """Initialize form with task instance."""
        self.task = task
        self.user = user

        initial = kwargs.setdefault("initial", {})

        if task and not kwargs.get("data"):
            initial.update(
                {
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "due_date": task.due_date,
                }
            )

        super().__init__(*args, **kwargs)

    def clean(self):
        """Allow edits only when task is pending."""
        cleaned_data = super().clean()

        if self.task.status != Task.Status.PENDING:
            raise forms.ValidationError("Only pending tasks can be edited.")

        return cleaned_data

    def save(self):
        """Update task using service layer."""
        return update_task_details(
            self.task,
            self.user,
            title=self.cleaned_data["title"],
            description=self.cleaned_data["description"],
            due_date=self.cleaned_data.get("due_date"),
        )
