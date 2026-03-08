"""
otp.py
~~~~~~

Utility functions for generating and sending OTP codes
via email and SMS.
"""

import secrets
from django.utils import timezone


# =========================================================
# OTP Generator
# =========================================================
def generate_otp():
    # Generates a cryptographically strong 6-digit string
    return "".join(secrets.choice("0123456789") for _ in range(6))


# =========================================================
# Email Sender
# =========================================================
def send_email_otp(user, otp, purpose="Verification"):
    """Send OTP to the user's email."""
    # TODO


# =========================================================
# SMS Sender
# =========================================================
def send_sms_otp(user, otp, purpose="Verification"):
    """Send OTP to user's phone via SMS."""
    # TODO


# ========================================================
# OTP Sending Functions
# ========================================================
def send_email_verification_otp(user):
    """
    Generate and send OTP for email verification.
    """

    otp = generate_otp()

    user.email_OTP = otp
    user.email_OTP_created_at = timezone.now()

    user.save(update_fields=["email_OTP", "email_OTP_created_at"])

    send_email_otp(user, otp, purpose="Email Verification")


def send_phone_verification_otp(user):
    """
    Generate and send OTP for phone verification.
    """

    otp = generate_otp()

    user.phone_OTP = otp
    user.phone_OTP_created_at = timezone.now()

    user.save(update_fields=["phone_OTP", "phone_OTP_created_at"])

    send_sms_otp(user, otp, purpose="Phone Verification")


def send_password_reset_otp(user):
    """
    Generate and send OTP for password reset.
    """

    otp = generate_otp()

    user.password_otp = otp
    user.password_otp_created_at = timezone.now()

    user.save(update_fields=["password_otp", "password_otp_created_at"])

    send_email_otp(user, otp, purpose="Password Reset")
