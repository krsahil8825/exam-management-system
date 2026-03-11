"""
accounts.utils.decorators
~~~~~~~~~~~~~~~~~~~~~~~~~

Role-based access control decorators for the accounts app.
Ensures proper verification and profile validation.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from ..models import Employee


def email_verified_required(view_func):
    """Require login and verified email."""

    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.email_verified:
            raise PermissionDenied("Email is not verified.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def phone_verified_required(view_func):
    """Require login and verified phone."""

    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.phone_verified:
            raise PermissionDenied("Phone is not verified.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def fully_verified_required(view_func):
    """Require login with both email and phone verified."""

    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.email_verified:
            raise PermissionDenied("Email is not verified.")
        if not request.user.phone_verified:
            raise PermissionDenied("Phone is not verified.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def self_only_required(view_func):
    """Require user to access only their own resources."""

    @fully_verified_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        if user_id is not None and str(request.user.id) != str(user_id):
            raise PermissionDenied("You can only access your own resources.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def employee_required(view_func):
    """Require fully verified user with an employee profile."""

    @fully_verified_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, "employee_profile"):
            raise PermissionDenied("Employee access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def candidate_required(view_func):
    """Require fully verified user with a candidate profile."""

    @fully_verified_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, "candidate_profile"):
            raise PermissionDenied("Candidate access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def admin_required(view_func):
    """Require employee role to be SUPER_ADMIN or ADMIN."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        role = request.user.employee_profile.role
        allowed = {Employee.RoleChoices.SUPER_ADMIN, Employee.RoleChoices.ADMIN}
        if role not in allowed:
            raise PermissionDenied("Admin privileges required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def super_admin_required(view_func):
    """Require employee role to be SUPER_ADMIN."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_profile.role != Employee.RoleChoices.SUPER_ADMIN:
            raise PermissionDenied("Super admin privileges required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def manager_required(view_func):
    """Require employee role to be MANAGER."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_profile.role != Employee.RoleChoices.MANAGER:
            raise PermissionDenied("Manager access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def examiner_required(view_func):
    """Require employee role to be EXAMINER."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_profile.role != Employee.RoleChoices.EXAMINER:
            raise PermissionDenied("Examiner access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def invigilator_required(view_func):
    """Require employee role to be INVIGILATOR."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_profile.role != Employee.RoleChoices.INVIGILATOR:
            raise PermissionDenied("Invigilator access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def assistant_required(view_func):
    """Require employee role to be ASSISTANT."""

    @employee_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_profile.role != Employee.RoleChoices.ASSISTANT:
            raise PermissionDenied("Assistant access required.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
