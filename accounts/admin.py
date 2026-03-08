"""
accounts.admin
~~~~~~~~~~~~~~

Admin configuration for User, Candidate, Employee, and Address models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Candidate, Employee, Address


# =========================================================
# Address Admin
# =========================================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "state", "country", "zip_code")
    search_fields = ("user__email", "city", "state", "zip_code")


# =========================================================
# Custom User Admin
# =========================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "phone",
        "email_verified",
        "phone_verified",
        "is_staff",
        "is_superuser",
    )

    search_fields = ("email", "phone")

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Contact", {"fields": ("country_code", "phone")}),
        ("Profile", {"fields": ("profile_picture",)}),
        ("Verification", {"fields": ("email_verified", "phone_verified")}),
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
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "country_code",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# =========================================================
# Candidate Admin
# =========================================================
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "candidate_id",
        "education_level",
        "semester",
        "gender",
    )

    search_fields = (
        "user__email",
        "candidate_id",
        "enrollment_number",
    )

    readonly_fields = ("candidate_id",)


# =========================================================
# Employee Admin
# =========================================================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "employee_id",
        "role",
        "department",
        "gender",
    )

    search_fields = (
        "user__email",
        "employee_id",
    )

    readonly_fields = ("employee_id",)


# =========================================================
# Admin Site Branding
# =========================================================
admin.site.site_header = "Exam Management Admin"
admin.site.site_title = "Exam Management"
admin.site.index_title = "Admin Dashboard"
