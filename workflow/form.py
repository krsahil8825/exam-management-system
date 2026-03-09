"""
workflow.form
~~~~~~~~~~~~~

Forms for creating and editing workflow tasks.
"""

from django import forms
from django.utils import timezone

from accounts.models import Employee
from .models import Task


class TaskCreateForm(forms.ModelForm):
    """Form used by employees to create new tasks."""

    class Meta:
        """Use only fields relevant for task creation and apply basic styling."""

        model = Task
        fields = ("assigned_to", "title", "description", "priority", "due_date")
        widgets = {
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Task title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Task description",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """Accept an optional assigned_by employee to set the creator context for validation and queryset filtering."""
        self.assigned_by = kwargs.pop("assigned_by", None)
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = Employee.objects.select_related("user")
        self.fields["due_date"].required = False

    def clean_due_date(self):
        """Ensure due date is in the future when provided."""
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date

    def clean(self):
        """Disallow assigning the task to the same creator."""
        cleaned_data = super().clean()
        assigned_to = cleaned_data.get("assigned_to")

        if self.assigned_by and assigned_to and self.assigned_by.pk == assigned_to.pk:
            raise forms.ValidationError(
                "A task cannot be assigned to the same employee."
            )

        return cleaned_data

    def save(self, *, assigned_by=None, commit=True):
        """Create a pending task with the provided creator employee."""
        creator = assigned_by or self.assigned_by
        if creator is None:
            raise ValueError("assigned_by is required to create a task.")

        task = super().save(commit=False)
        task.assigned_by = creator
        task.status = Task.Status.PENDING
        if commit:
            task.save()
        return task


class TaskEditForm(forms.ModelForm):
    """Form for editing task details while task is pending."""

    class Meta:
        """Use only fields relevant for editing task details and apply basic styling."""

        model = Task
        fields = ("title", "description", "priority", "due_date")
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Task title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Task description",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }

    def clean_due_date(self):
        """Ensure due date is in the future when provided."""
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")
        return due_date

    def clean(self):
        """Allow edits only when the task is still pending."""
        cleaned_data = super().clean()
        instance = self.instance

        if instance.pk and instance.status != Task.Status.PENDING:
            raise forms.ValidationError("Only pending tasks can be edited.")

        return cleaned_data
