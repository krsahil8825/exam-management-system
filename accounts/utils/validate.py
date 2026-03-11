"""
accounts.utils.validate
~~~~~~~~~~~~~~~~~~~~~~~

Validation utilities for user data and profile photos.
"""

import os

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from PIL import Image, UnidentifiedImageError


# Validators for phone numbers
phone_validator = RegexValidator(
    regex=r"^[1-9]\d{6,14}$",
    message=(
        "Enter a valid phone number without country code. "
        "It must contain 7-15 digits and cannot start with 0."
    ),
)

# Validator for international country codes
country_code_validator = RegexValidator(
    regex=r"^\+[1-9]\d{0,3}$",
    message=(
        "Enter a valid international country code starting with + "
        "(example: +1, +44, +91)."
    ),
)


ALLOWED_IMAGE_TYPES = {"jpeg", "png"}
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}

MIN_IMAGE_SIZE = 40 * 1024 # 40 KB
MAX_IMAGE_SIZE = 200 * 1024 # 200 KB

MIN_WIDTH = 200 # 200 pixels
MIN_HEIGHT = 200 # 200 pixels
MAX_WIDTH = 2000 # 2000 pixels
MAX_HEIGHT = 2000 # 2000 pixels


def _get_extension(file_name):
    """Extract and return the file extension in lowercase without the dot."""
    _, ext = os.path.splitext(file_name or "")
    return ext.lstrip(".").lower()


def validate_profile_photo(file):
    """Validate profile image by size, extension, image content and dimensions."""
    if not file:
        raise ValidationError("No image file was provided.")

    if file.size < MIN_IMAGE_SIZE:
        raise ValidationError("Image must be at least 40 KB.")
    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError("Image must not exceed 200 KB.")

    extension = _get_extension(file.name)
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            "Unsupported image format. Allowed formats: JPG, JPEG, PNG."
        )

    try:
        file.seek(0)
        image = Image.open(file)
        image_format = (image.format or "").lower()
        if image_format not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Uploaded file is not a valid image format.")

        image.verify()

        file.seek(0)
        image = Image.open(file)
        width, height = image.size
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError("Invalid or corrupted image file.")
    finally:
        file.seek(0)

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValidationError(
            f"Image dimensions must be at least {MIN_WIDTH}x{MIN_HEIGHT}px."
        )
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValidationError(
            f"Image dimensions must not exceed {MAX_WIDTH}x{MAX_HEIGHT}px."
        )
