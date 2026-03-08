"""
forms.py
~~~~~~~~

This module contains the forms used in the accounts app.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from .models import User, Candidate, Address, Employee
from .utils.validate import phone_validator, country_code_validator, validate_profile_photo

# =========================================================
# Authentication Forms
# =========================================================


class BaseAddressForm(forms.Form):
    """Base form for address fields."""

    street1 = forms.CharField(
        label="Street Address Line 1",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "House number, street"}
        ),
    )

    street2 = forms.CharField(
        label="Street Address Line 2",
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Apartment, suite"}
        ),
    )

    city = forms.CharField(
        label="City",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
    )

    state = forms.CharField(
        label="State",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
    )

    country = forms.CharField(
        label="Country",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Country"}
        ),
    )

    zip_code = forms.CharField(
        label="Zip Code",
        max_length=20,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Postal code"}
        ),
    )


class BaseUserForm(UserCreationForm):
    """Base form containing all User related fields."""

    first_name = forms.CharField(
        label="First Name",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First name"}
        ),
    )

    last_name = forms.CharField(
        label="Last Name",
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last name"}
        ),
    )

    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com"}
        ),
    )

    country_code = forms.CharField(
        label="Country Code",
        max_length=5,
        validators=[country_code_validator],
        initial="+91",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91"}),
    )

    phone = forms.CharField(
        label="Phone Number",
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "9876543210"}
        ),
    )

    profile_picture = forms.ImageField(
        label="Profile Photo (Format: JPG, JPEG, PNG | Size: 40-200 KB | Dimensions: 200x200 to 2000x2000 px)",
        required=True,
        validators=[validate_profile_photo],
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "placeholder": "Select the image",
                "accept": ".jpg,.jpeg,.png",
            }
        ),
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm password"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "country_code",
            "phone",
            "profile_picture",
            "password1",
            "password2",
        )


class LoginForm(forms.Form):
    """Form for user login."""

    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com"}
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )


class CandidateRegistrationForm(BaseUserForm, BaseAddressForm):
    """Complete candidate registration form."""

    education_level = forms.ChoiceField(
        label="Education Level",
        choices=Candidate.EDUCATION_LEVEL_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    university_name = forms.CharField(
        label="University Name",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "University name"}
        ),
    )

    enrollment_number = forms.CharField(
        label="Enrollment Number",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enrollment number"}
        ),
    )

    course_name = forms.CharField(
        label="Course Name",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Course name"}
        ),
    )

    semester = forms.IntegerField(
        label="Semester",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )

    father_name = forms.CharField(
        label="Father's Name",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Father name"}
        ),
    )

    mother_name = forms.CharField(
        label="Mother's Name",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Mother name"}
        ),
    )

    dob = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    gender = forms.ChoiceField(
        label="Gender",
        choices=Candidate.gender_choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    @transaction.atomic
    def save(self, commit=True):

        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]
        user.country_code = self.cleaned_data["country_code"]
        user.phone = self.cleaned_data["phone"]
        user.profile_picture = self.cleaned_data["profile_picture"]

        if commit:
            user.save()

            Address.objects.create(
                user=user,
                street1=self.cleaned_data["street1"],
                street2=self.cleaned_data["street2"],
                city=self.cleaned_data["city"],
                state=self.cleaned_data["state"],
                country=self.cleaned_data["country"],
                zip_code=self.cleaned_data["zip_code"],
            )

            Candidate.objects.create(
                user=user,
                education_level=self.cleaned_data["education_level"],
                university_name=self.cleaned_data["university_name"],
                enrollment_number=self.cleaned_data["enrollment_number"],
                course_name=self.cleaned_data["course_name"],
                semester=self.cleaned_data["semester"],
                father_name=self.cleaned_data["father_name"],
                mother_name=self.cleaned_data["mother_name"],
                dob=self.cleaned_data["dob"],
                gender=self.cleaned_data["gender"],
            )

        return user


class EmployeeRegistrationForm(BaseUserForm, BaseAddressForm):
    """Complete employee registration form."""

    gender = forms.ChoiceField(
        label="Gender",
        choices=Employee.gender_choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    role = forms.ChoiceField(
        label="Role",
        choices=Employee.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    department = forms.ChoiceField(
        label="Department",
        choices=Employee.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    additional_info = forms.CharField(
        label="Additional Information",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Optional notes about employee",
                "rows": 3,
            }
        ),
    )

    @transaction.atomic
    def save(self, commit=True):
        """Create User, Address and Employee profile."""

        user = super().save(commit=False)

        user.email = self.cleaned_data["email"]
        user.country_code = self.cleaned_data["country_code"]
        user.phone = self.cleaned_data["phone"]
        user.profile_picture = self.cleaned_data["profile_picture"]

        if commit:
            # Save user
            user.save()

            # Create address
            Address.objects.create(
                user=user,
                street1=self.cleaned_data["street1"],
                street2=self.cleaned_data["street2"],
                city=self.cleaned_data["city"],
                state=self.cleaned_data["state"],
                country=self.cleaned_data["country"],
                zip_code=self.cleaned_data["zip_code"],
            )

            # Create employee profile
            Employee.objects.create(
                user=user,
                gender=self.cleaned_data["gender"],
                role=self.cleaned_data["role"],
                department=self.cleaned_data["department"],
                additional_info=self.cleaned_data["additional_info"],
            )

        return user


class EmailOtpVerificationForm(forms.Form):
    """Form for verifying email OTP."""

    OTP_EXPIRATION_MINUTES = 10

    otp = forms.CharField(
        label="Email OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit OTP"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Accept the user instance for OTP validation.
        """
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_otp(self):
        """
        Validate email OTP.
        """
        otp = self.cleaned_data["otp"]

        # Ensure OTP exists
        if not self.user.email_OTP:
            raise forms.ValidationError("No email OTP found. Please request a new OTP.")

        # Prevent runtime errors if timestamp is missing
        if not self.user.email_OTP_created_at:
            raise forms.ValidationError(
                "OTP timestamp missing. Please request a new OTP."
            )

        # Validate OTP value
        if otp != self.user.email_OTP:
            raise forms.ValidationError("Invalid email OTP.")

        # Validate OTP expiration
        expiration_time = self.user.email_OTP_created_at + timedelta(
            minutes=self.OTP_EXPIRATION_MINUTES
        )

        if timezone.now() > expiration_time:
            raise forms.ValidationError("Email OTP has expired.")

        return otp


class PhoneOtpVerificationForm(forms.Form):
    """Form for verifying phone OTP."""

    OTP_EXPIRATION_MINUTES = 10

    otp = forms.CharField(
        label="Phone OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit OTP"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Accept the user instance for OTP validation.
        """
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_otp(self):
        """
        Validate phone OTP.
        """
        otp = self.cleaned_data["otp"]

        # Ensure OTP exists
        if not self.user.phone_OTP:
            raise forms.ValidationError("No phone OTP found. Please request a new OTP.")

        # Prevent runtime errors if timestamp is missing
        if not self.user.phone_OTP_created_at:
            raise forms.ValidationError(
                "OTP timestamp missing. Please request a new OTP."
            )

        # Validate OTP value
        if otp != self.user.phone_OTP:
            raise forms.ValidationError("Invalid phone OTP.")

        # Validate expiration
        expiration_time = self.user.phone_OTP_created_at + timedelta(
            minutes=self.OTP_EXPIRATION_MINUTES
        )

        if timezone.now() > expiration_time:
            raise forms.ValidationError("Phone OTP has expired.")

        return otp


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset."""

    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com"}
        ),
    )

    def clean_email(self):
        """Ensure user with this email exists."""
        email = self.cleaned_data["email"]

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")

        return email


class SetNewPasswordForm(forms.Form):
    """Form for setting a new password using OTP."""

    OTP_EXPIRATION_MINUTES = 10

    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter OTP"}
        ),
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter new password"}
        ),
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """Accept the user instance for OTP validation."""
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        """Validate OTP and passwords."""
        cleaned_data = super().clean()

        otp = cleaned_data.get("otp")
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        # Check password match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        # Ensure OTP exists
        if not self.user.password_otp:
            raise forms.ValidationError("No password reset OTP found.")

        # Ensure timestamp exists
        if not self.user.password_otp_created_at:
            raise forms.ValidationError("OTP timestamp missing. Request a new OTP.")

        # Validate OTP
        if otp != self.user.password_otp:
            raise forms.ValidationError("Invalid OTP.")

        # Validate expiration
        expiration_time = self.user.password_otp_created_at + timedelta(
            minutes=self.OTP_EXPIRATION_MINUTES
        )

        if timezone.now() > expiration_time:
            raise forms.ValidationError("OTP has expired.")

        return cleaned_data
