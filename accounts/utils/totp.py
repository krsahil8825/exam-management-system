"""
accounts.utils.totp
~~~~~~~~~~~~~~~~~~~

Utility functions for generating and validating Time-based One-Time Passwords (TOTP).
"""

import base64
from io import BytesIO

import pyotp
import qrcode

from .crypto import encrypt, decrypt


def _get_totp_secret():
    """Generate a random base32 secret for TOTP."""
    return pyotp.random_base32()


def _generate_qr(user_email, totp_secret):
    """
    Generate a QR code for TOTP setup and return a base64 image path
    that can be embedded directly in HTML.
    """

    totp_uri = pyotp.TOTP(totp_secret).provisioning_uri(
        name=user_email,
        issuer_name="Exam Management System",
    )

    qr = qrcode.make(totp_uri)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_base64}"


def generate_totp(user):
    """
    Generate a TOTP secret, encrypt it, and store it in the database.
    """

    secret = _get_totp_secret()

    encrypted_secret = encrypt(secret)

    user.totp_secret = encrypted_secret
    user.save(update_fields=["totp_secret"])

    return _generate_qr(user.email, secret)


def turn_on_totp(user):
    """Enable TOTP for the user."""
    user.is_totp_enabled = True
    user.save(update_fields=["is_totp_enabled"])


def validate_totp(user, token):
    """
    Validate a TOTP token using the decrypted secret.
    """

    if not user.totp_secret:
        return False

    secret = decrypt(user.totp_secret)

    totp = pyotp.TOTP(secret)

    return totp.verify(token)


def disable_totp(user):
    """Disable TOTP and remove the secret."""

    user.totp_secret = None
    user.is_totp_enabled = False

    user.save(update_fields=["totp_secret", "is_totp_enabled"])
