"""
accounts.decorators
~~~~~~~~~~~~~~~~~~~

Role-based access control decorators for the accounts app.
Ensures proper verification and profile validation.
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Employee


# =========================================================
# Base Verification Decorator
# =========================================================
def verified_login_required(view_func):
    """
    Ensure user is authenticated and email is verified.
    """

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.email_verified:
            raise PermissionDenied("Email is not verified.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


# =========================================================
# Employee Required
# =========================================================
def employee_required(view_func):
    """
    Ensure user has an employee profile.
    """

    @wraps(view_func)
    @verified_login_required
    def _wrapped_view(request, *args, **kwargs):

        if not hasattr(request.user, "employee_profile"):
            raise PermissionDenied("Employee access required.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# =========================================================
# Candidate Required
# =========================================================
def candidate_required(view_func):
    """
    Ensure user has a candidate profile.
    """

    @wraps(view_func)
    @verified_login_required
    def _wrapped_view(request, *args, **kwargs):

        if not hasattr(request.user, "candidate_profile"):
            raise PermissionDenied("Candidate access required.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# =========================================================
# Admin Required (SUPER_ADMIN or ADMIN)
# =========================================================
def admin_required(view_func):
    """
    Ensure user is an admin-level employee.
    """

    @wraps(view_func)
    @employee_required
    def _wrapped_view(request, *args, **kwargs):

        role = request.user.employee_profile.role

        if role not in [Employee.SUPER_ADMIN, Employee.ADMIN]:
            raise PermissionDenied("Admin privileges required.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# =========================================================
# Verified Employee Required
# =========================================================
def verified_employee_required(view_func):
    """
    Ensure employee profile exists and is verified.
    """

    @wraps(view_func)
    @employee_required
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.employee_profile.is_verified:
            raise PermissionDenied("Employee profile not verified.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


# =========================================================
# Verified Candidate Required
# =========================================================
def verified_candidate_required(view_func):
    """
    Ensure candidate profile exists and is verified.
    """

    @wraps(view_func)
    @candidate_required
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.candidate_profile.is_verified:
            raise PermissionDenied("Candidate profile not verified.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
