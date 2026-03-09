"""
workflow.admin
~~~~~~~~~~~~~~

Admin configuration for workflow models.
"""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Simple and practical admin for internal task operations."""

    list_display = (
        "task_code",
        "title",
        "assigned_by_email",
        "assigned_to_email",
        "status",
        "priority",
        "due_date",
        "created_at",
    )
    list_filter = ("status", "priority", "created_at", "due_date")
    search_fields = (
        "task_code",
        "title",
        "description",
        "assigned_by__user__email",
        "assigned_to__user__email",
    )
    autocomplete_fields = ("assigned_by", "assigned_to")
    readonly_fields = ("task_code", "completed_at", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_select_related = ("assigned_by__user", "assigned_to__user")

    fieldsets = (
        (
            "Task",
            {
                "fields": (
                    "task_code",
                    "title",
                    "description",
                    "assigned_by",
                    "assigned_to",
                    "status",
                    "priority",
                    "due_date",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("completed_at", "created_at", "updated_at")},
        ),
    )

    @admin.display(description="Assigned By", ordering="assigned_by__user__email")
    def assigned_by_email(self, obj):
        """Display the email of the employee who assigned the task."""
        return obj.assigned_by.user.email

    @admin.display(description="Assigned To", ordering="assigned_to__user__email")
    def assigned_to_email(self, obj):
        """Display the email of the employee to whom the task is assigned."""
        return obj.assigned_to.user.email


# Customize admin site titles
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management"
admin.site.index_title = "Admin Dashboard"
