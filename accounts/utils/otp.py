"""
accounts.utils.otp
~~~~~~~~~~~~~~~~~~

Utility functions for generating and sending OTP codes.
"""

import secrets

from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

from ..models import OTP


def _generate_otp():
    """Return a cryptographically strong 6-digit OTP string."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def _send_email(user, otp, message="Verification"):
    """
    Send OTP to the user's email.

    This is intentionally left unimplemented for now.
    """
    raise NotImplementedError("send_email_otp is not implemented yet.")


def _send_sms(user, otp, message="Verification"):
    """
    Send OTP to the user's phone via SMS.

    This is intentionally left unimplemented for now.
    """
    raise NotImplementedError("send_sms_otp is not implemented yet.")


def send_email_otp(user, purpose, message="Verification"):
    """Generate and send an OTP to the user's email."""

    if purpose not in OTP.OTPPurpose.values:
        raise ValueError("Invalid OTP purpose specified.")

    otp = _generate_otp()

    OTP.objects.create(
        user=user,
        purpose=purpose,
        otp=make_password(otp),
    )

    _send_email(user, otp, message)


def send_sms_otp(user, purpose, message="Verification"):
    """Generate and send an OTP to the user's phone."""

    if purpose not in OTP.OTPPurpose.values:
        raise ValueError("Invalid OTP purpose specified.")

    otp = _generate_otp()

    OTP.objects.create(
        user=user,
        purpose=purpose,
        otp=make_password(otp),
    )

    _send_sms(user, otp, message)


def check_otp(user, otp, purpose):
    """
    Validate OTP for a specific purpose.

    Rules:
    - OTP must belong to the user
    - OTP must match the purpose
    - OTP must not be expired
    - OTP must not be already used
    """

    now = timezone.now()

    otp_record = (
        OTP.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
            expires_at__gt=now,
        )
        .order_by("-created_at")
        .first()
    )

    if not otp_record:
        return False

    if check_password(otp, otp_record.otp):
        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])
        return True

    return False
