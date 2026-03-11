"""
accounts.utils.crypto
~~~~~~~~~~~~~~~~~~~~~

Utility functions for encrypting and decrypting sensitive data
such as TOTP secrets.
"""

import os
from cryptography.fernet import Fernet


def _get_cipher():
    """
    Return a Fernet cipher using the encryption key stored
    in environment variables.
    """

    key = os.environ.get("TOTP_ENCRYPTION_KEY")

    if not key:
        raise ValueError("TOTP_ENCRYPTION_KEY is not set")

    return Fernet(key.encode())


def encrypt(value: str) -> str:
    """
    Encrypt a string value.
    """

    cipher = _get_cipher()
    encrypted = cipher.encrypt(value.encode())

    return encrypted.decode()


def decrypt(value: str) -> str:
    """
    Decrypt an encrypted string.
    """

    cipher = _get_cipher()
    decrypted = cipher.decrypt(value.encode())

    return decrypted.decode()
