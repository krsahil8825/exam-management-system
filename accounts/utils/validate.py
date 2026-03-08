from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from PIL import Image


# =========================================================
# PHONE VALIDATOR (WITHOUT COUNTRY CODE)
# Accepts international style local phone numbers
# =========================================================

phone_validator = RegexValidator(
    regex=r"^[1-9]\d{6,14}$",
    message=(
        "Enter a valid phone number without country code. "
        "It must contain 7-15 digits and cannot start with 0."
    ),
)


# =========================================================
# COUNTRY CODE VALIDATOR
# =========================================================

country_code_validator = RegexValidator(
    regex=r"^\+[1-9]\d{0,3}$",
    message=(
        "Enter a valid international country code starting with + "
        "(example: +1, +44, +91)."
    ),
)


# =========================================================
# IMAGE VALIDATION SETTINGS
# =========================================================

ALLOWED_IMAGE_TYPES = {
    "jpeg",
    "png",
}

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
}

MIN_IMAGE_SIZE = 40 * 1024  # 40 KB
MAX_IMAGE_SIZE = 200 * 1024  # 200 KB

MIN_WIDTH = 200
MIN_HEIGHT = 200

MAX_WIDTH = 2000
MAX_HEIGHT = 2000


# =========================================================
# PROFILE PHOTO VALIDATOR
# =========================================================


def validate_profile_photo(file):
    """
    Validate uploaded profile photo.

    Checks:
    - File size
    - File extension
    - Image header type
    - Image integrity
    - Image dimensions
    """

    # FILE SIZE VALIDATION
    if file.size < MIN_IMAGE_SIZE:
        raise ValidationError("Image must be at least 40 KB.")

    if file.size > MAX_IMAGE_SIZE:
        raise ValidationError("Image must not exceed 200 KB.")

    # EXTENSION VALIDATION
    extension = file.name.split(".")[-1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            "Unsupported image format. Allowed formats: JPG, JPEG, PNG."
        )

    # IMAGE HEADER + CONTENT VALIDATION
    try:
        image = Image.open(file)

        # Detect actual image type from header
        image_type = image.format.lower()

        if image_type not in ALLOWED_IMAGE_TYPES:
            raise ValidationError("Uploaded file is not a valid image format.")

        # Verify image integrity
        image.verify()

    except Exception:
        raise ValidationError("Invalid or corrupted image file.")

    # REOPEN IMAGE (verify() closes the file)
    file.seek(0)
    image = Image.open(file)

    width, height = image.size

    # MIN DIMENSION VALIDATION
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        raise ValidationError(
            f"Image dimensions must be at least {MIN_WIDTH}x{MIN_HEIGHT}px."
        )

    # MAX DIMENSION VALIDATION
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValidationError(
            f"Image dimensions must not exceed {MAX_WIDTH}x{MAX_HEIGHT}px."
        )
