"""
accounts.utils.otp
~~~~~~~~~~~~~~~~~~

Utility functions for generating and sending OTP codes.
"""

import secrets

from django.utils import timezone


def generate_otp():
    """Return a cryptographically strong 6-digit OTP string."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def send_email_otp(user, otp, purpose="Verification"):
    """
    Send OTP to the user's email.

    This is intentionally left unimplemented for now.
    """
    raise NotImplementedError("send_email_otp is not implemented yet.")


def send_sms_otp(user, otp, purpose="Verification"):
    """
    Send OTP to the user's phone via SMS.

    This is intentionally left unimplemented for now.
    """
    raise NotImplementedError("send_sms_otp is not implemented yet.")


def send_email_verification_otp(user):
    """Generate and store OTP for email verification, then send it."""

    otp = generate_otp()
    user.email_OTP = otp
    user.email_OTP_created_at = timezone.now()
    user.save(update_fields=["email_OTP", "email_OTP_created_at"])
    send_email_otp(user, otp, purpose="Email Verification")


def send_phone_verification_otp(user):
    """Generate and store OTP for phone verification, then send it."""

    otp = generate_otp()
    user.phone_OTP = otp
    user.phone_OTP_created_at = timezone.now()
    user.save(update_fields=["phone_OTP", "phone_OTP_created_at"])
    send_sms_otp(user, otp, purpose="Phone Verification")


def send_password_reset_otp(user):
    """Generate and store OTP for password reset, then send it by email."""

    otp = generate_otp()
    user.password_otp = otp
    user.password_otp_created_at = timezone.now()
    user.save(update_fields=["password_otp", "password_otp_created_at"])
    send_email_otp(user, otp, purpose="Password Reset")
