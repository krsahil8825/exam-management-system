"""
accounts.admin
~~~~~~~~~~~~~~

Admin configuration for accounts models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import Address, Candidate, Employee, OTP, User


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin view for user addresses."""

    list_display = ("user", "city", "state", "country", "zip_code")
    search_fields = ("user__email", "city", "state", "country", "zip_code")
    list_filter = ("country", "state")
    autocomplete_fields = ("user",)

    # performance optimization
    list_select_related = ("user",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin view for custom User model."""

    list_display = (
        "email",
        "email_verified",
        "phone_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "profile_picture_preview",
    )

    search_fields = (
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    ordering = ("email",)

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "phone_verified",
        "is_2FA_enabled",
        "gender",
    )

    readonly_fields = (
        "profile_picture_preview",
        "last_login",
        "date_joined",
        "totp_secret",
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "country_code",
                    "phone",
                    "profile_picture",
                    "profile_picture_preview",
                )
            },
        ),
        (
            "Verification",
            {
                "fields": (
                    "email_verified",
                    "phone_verified",
                )
            },
        ),
        (
            "Security",
            {
                "fields": (
                    "is_2FA_enabled",
                    "totp_secret",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "country_code",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description="Photo")
    def profile_picture_preview(self, obj):
        """Display a preview of the user's profile picture."""

        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:5px;" />',
                obj.profile_picture.url,
            )

        return "No Image"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Admin view for Candidate profiles."""

    list_display = (
        "user",
        "candidate_id",
        "education_level",
        "semester",
        "course_name",
        "university_name",
    )

    search_fields = (
        "user__email",
        "candidate_id",
        "enrollment_number",
        "university_name",
        "course_name",
    )

    list_filter = (
        "education_level",
        "semester",
    )

    readonly_fields = ("candidate_id",)

    autocomplete_fields = ("user",)

    list_select_related = ("user",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin view for Employee profiles."""

    list_display = (
        "user",
        "employee_id",
        "role",
        "department",
    )

    search_fields = (
        "user__email",
        "employee_id",
        "role",
        "department",
    )

    list_filter = (
        "role",
        "department",
    )

    readonly_fields = ("employee_id",)

    autocomplete_fields = ("user",)

    list_select_related = ("user",)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """Admin view for OTP records."""

    list_display = (
        "user",
        "purpose",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
        "purpose",
    )

    list_filter = (
        "purpose",
        "created_at",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "expires_at",
    )

    autocomplete_fields = ("user",)

    list_select_related = ("user",)


# Customize admin site titles
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management"
admin.site.index_title = "Admin Dashboard"
