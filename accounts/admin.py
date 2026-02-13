"""
accounts.admin
~~~~~~~~~~~~~~

Admin configuration for User, Candidate, Employee, and Address models.

Provides:
- Extended User admin with profile inline support.
- Clean list display, search, and filters.
- Role-aware employee visibility.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, Candidate, Employee, Address


# =========================================================
# Address Admin
# =========================================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for Address model."""

    list_display = ("street1", "city", "state", "country", "zip_code")
    search_fields = ("street1", "city", "state", "zip_code")
    list_filter = ("state", "country")


# =========================================================
# Candidate Inline
# =========================================================
class CandidateInline(admin.StackedInline):
    """Inline admin for Candidate profile inside User."""

    model = Candidate
    can_delete = False
    verbose_name_plural = "Candidate Profile"


# =========================================================
# Employee Inline
# =========================================================
class EmployeeInline(admin.StackedInline):
    """Inline admin for Employee profile inside User."""

    model = Employee
    can_delete = False
    readonly_fields = ("employee_id",)
    verbose_name_plural = "Employee Profile"


# =========================================================
# Custom User Admin
# =========================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with profile integration."""

    model = User

    list_display = (
        "username",
        "email",
        "phone",
        "is_staff",
        "is_superuser",
        "email_verified",
        "profile_preview",
    )

    list_filter = ("is_staff", "is_superuser", "email_verified")
    search_fields = ("username", "email", "phone")
    ordering = ("username",)

    readonly_fields = ("profile_preview",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "phone",
                    "address",
                    "profile_picture",
                    "profile_preview",
                    "email_verified",
                )
            },
        ),
    )

    inlines = [CandidateInline, EmployeeInline]

    def profile_preview(self, obj):
        """Show profile picture preview in admin."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:50%;" />',
                obj.profile_picture.url,
            )
        return "No Image"

    profile_preview.short_description = "Profile Preview"


# =========================================================
# Candidate Admin
# =========================================================
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Admin configuration for Candidate profile."""

    list_display = (
        "user",
        "application_number",
        "roll_number",
        "education_level",
        "semester",
        "is_verified",
    )

    search_fields = (
        "user__username",
        "application_number",
        "roll_number",
        "university_name",
    )

    list_filter = ("education_level", "gender", "is_verified")
    readonly_fields = ("application_number", "roll_number", "exam_key")


# =========================================================
# Employee Admin
# =========================================================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for Employee profile."""

    list_display = (
        "user",
        "employee_id",
        "role",
        "department",
        "is_verified",
    )

    search_fields = (
        "user__username",
        "employee_id",
    )

    list_filter = ("role", "department", "is_verified")
    readonly_fields = ("employee_id",)


# ========================================================

admin.site.index_title = "Exam Management Admin"
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management Admin"