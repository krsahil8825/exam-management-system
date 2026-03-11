"""
accounts.forms
~~~~~~~~~~~~~

Forms for user registration, profile editing, and OTP verification in the accounts app.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.db import transaction
from django.utils import timezone

from .models import Address, Candidate, Employee, User, OTP
from .utils.validate import (
    country_code_validator,
    phone_validator,
    validate_profile_photo,
)
from .utils.otp import check_otp, send_email_otp
from .utils.totp import validate_totp, turn_on_totp, disable_totp

# ========================================
# Registration and Profile Edit Forms
# ========================================


class BaseAddressForm(forms.Form):
    """Shared address fields used by candidate and employee registration."""

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

    def _address_data(self):
        """Return cleaned address data as a dict."""
        return {
            "street1": self.cleaned_data["street1"].strip(),
            "street2": (self.cleaned_data.get("street2") or "").strip(),
            "city": self.cleaned_data["city"].strip(),
            "state": self.cleaned_data["state"].strip(),
            "country": self.cleaned_data["country"].strip(),
            "zip_code": self.cleaned_data["zip_code"].strip(),
        }


class BaseUserForm(UserCreationForm):
    """Shared user fields used by candidate and employee registration."""

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
    gender = forms.ChoiceField(
        label="Gender",
        choices=User.GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    profile_picture = forms.ImageField(
        label=(
            "Profile Photo (Format: JPG, JPEG, PNG | Size: 40-200 KB | "
            "Dimensions: 200x200 to 2000x2000 px)"
        ),
        required=True,
        validators=[validate_profile_photo],
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}
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
        """Meta class to specify the model and fields for the form."""

        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "country_code",
            "phone",
            "gender",
            "profile_picture",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Ensure email is unique and normalized."""
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_country_code(self):
        """Normalize country code."""
        return self.cleaned_data["country_code"].strip()

    def clean_phone(self):
        """Strip whitespace from phone number."""
        return self.cleaned_data["phone"].strip()

    def _build_user(self):
        """Construct a User instance from the form data without saving it."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.country_code = self.cleaned_data["country_code"]
        user.phone = self.cleaned_data["phone"]
        user.gender = self.cleaned_data["gender"]
        user.profile_picture = self.cleaned_data["profile_picture"]
        return user


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

    def clean_email(self):
        """Normalize email for authentication."""
        return self.cleaned_data["email"].strip().lower()


class CandidateRegistrationForm(BaseUserForm, BaseAddressForm):
    """Registration form for candidates."""

    education_level = forms.ChoiceField(
        label="Education Level",
        choices=Candidate.EducationLevel.choices,
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
        min_value=1,
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

    def clean_dob(self):
        """Validate that date of birth is in the past."""
        dob = self.cleaned_data["dob"]
        if dob >= timezone.localdate():
            raise forms.ValidationError("Date of birth must be in the past.")
        return dob

    @transaction.atomic
    def save(self, commit=True):
        """Handle user, address, and candidate profile creation in a single transaction."""
        user = self._build_user()
        if not commit:
            return user

        user.save()
        Address.objects.create(user=user, **self._address_data())
        Candidate.objects.create(
            user=user,
            education_level=self.cleaned_data["education_level"],
            university_name=self.cleaned_data["university_name"].strip(),
            enrollment_number=self.cleaned_data["enrollment_number"].strip(),
            course_name=self.cleaned_data["course_name"].strip(),
            semester=self.cleaned_data["semester"],
            father_name=self.cleaned_data["father_name"].strip(),
            mother_name=self.cleaned_data["mother_name"].strip(),
            dob=self.cleaned_data["dob"],
        )
        return user


class EmployeeRegistrationForm(BaseUserForm, BaseAddressForm):
    """Registration form for employees."""

    role = forms.ChoiceField(
        label="Role",
        choices=Employee.RoleChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    department = forms.ChoiceField(
        label="Department",
        choices=Employee.DepartmentChoices.choices,
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
        """Handle user, address, and employee profile creation in a single transaction."""
        user = self._build_user()
        if not commit:
            return user

        user.save()
        Address.objects.create(user=user, **self._address_data())
        Employee.objects.create(
            user=user,
            role=self.cleaned_data["role"],
            department=self.cleaned_data["department"],
            additional_info=self.cleaned_data["additional_info"].strip(),
        )
        return user


class BaseUserEditForm(forms.Form):
    """Shared user fields for profile editing."""

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
    gender = forms.ChoiceField(
        label="Gender",
        choices=User.GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    profile_picture = forms.ImageField(
        label=(
            "Profile Photo (Format: JPG, JPEG, PNG | Size: 40-200 KB | "
            "Dimensions: 200x200 to 2000x2000 px)"
        ),
        required=False,
        validators=[validate_profile_photo],
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}
        ),
    )

    def clean_email(self):
        """Ensure email is unique and normalized."""
        email = self.cleaned_data["email"].strip().lower()
        user = getattr(self, "user_instance", None)
        queryset = User.objects.filter(email__iexact=email)
        if user and user.pk:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_country_code(self):
        """Normalize country code."""
        return self.cleaned_data["country_code"].strip()

    def clean_phone(self):
        """Strip whitespace from phone number."""
        phone = self.cleaned_data["phone"].strip()
        user = getattr(self, "user_instance", None)
        queryset = User.objects.filter(phone=phone)
        if user and user.pk:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone


class BaseAddressEditForm(forms.Form):
    """Shared address fields for profile editing."""

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

    def _address_data(self):
        """Extract cleaned address data for saving."""
        return {
            "street1": self.cleaned_data["street1"].strip(),
            "street2": (self.cleaned_data.get("street2") or "").strip(),
            "city": self.cleaned_data["city"].strip(),
            "state": self.cleaned_data["state"].strip(),
            "country": self.cleaned_data["country"].strip(),
            "zip_code": self.cleaned_data["zip_code"].strip(),
        }


class EmployeeEditForm(BaseUserEditForm, BaseAddressEditForm):
    """Edit form for employee user + address + employee profile."""

    role = forms.ChoiceField(
        label="Role",
        choices=Employee.RoleChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    department = forms.ChoiceField(
        label="Department",
        choices=Employee.DepartmentChoices.choices,
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

    def __init__(
        self,
        *args,
        user_instance=None,
        address_instance=None,
        employee_instance=None,
        **kwargs,
    ):
        """Initialize form with existing user, address, and employee data."""
        self.employee_instance = employee_instance
        self.user_instance = user_instance or (
            employee_instance.user if employee_instance else None
        )
        self.address_instance = address_instance
        if not self.address_instance and self.user_instance:
            self.address_instance = getattr(self.user_instance, "address", None)
        super().__init__(*args, **kwargs)

        if self.user_instance and not self.is_bound:
            self.fields["first_name"].initial = self.user_instance.first_name
            self.fields["last_name"].initial = self.user_instance.last_name
            self.fields["email"].initial = self.user_instance.email
            self.fields["country_code"].initial = self.user_instance.country_code
            self.fields["phone"].initial = self.user_instance.phone
            self.fields["gender"].initial = self.user_instance.gender

        if self.address_instance and not self.is_bound:
            self.fields["street1"].initial = self.address_instance.street1
            self.fields["street2"].initial = self.address_instance.street2
            self.fields["city"].initial = self.address_instance.city
            self.fields["state"].initial = self.address_instance.state
            self.fields["country"].initial = self.address_instance.country
            self.fields["zip_code"].initial = self.address_instance.zip_code

        if self.employee_instance and not self.is_bound:
            self.fields["role"].initial = self.employee_instance.role
            self.fields["department"].initial = self.employee_instance.department
            self.fields[
                "additional_info"
            ].initial = self.employee_instance.additional_info

    @transaction.atomic
    def save(self):
        """Handle user, address, and employee profile updates in a single transaction."""
        if not self.user_instance or not self.employee_instance:
            raise ValueError("User and employee instances are required.")

        self.user_instance.first_name = self.cleaned_data["first_name"].strip()
        self.user_instance.last_name = self.cleaned_data["last_name"].strip()
        self.user_instance.email = self.cleaned_data["email"]
        self.user_instance.country_code = self.cleaned_data["country_code"]
        self.user_instance.phone = self.cleaned_data["phone"]
        self.user_instance.gender = self.cleaned_data["gender"]
        if self.cleaned_data.get("profile_picture"):
            self.user_instance.profile_picture = self.cleaned_data["profile_picture"]
        self.user_instance.save()

        address_data = self._address_data()
        if self.address_instance:
            for key, value in address_data.items():
                setattr(self.address_instance, key, value)
            self.address_instance.save()
        else:
            Address.objects.create(user=self.user_instance, **address_data)

        self.employee_instance.role = self.cleaned_data["role"]
        self.employee_instance.department = self.cleaned_data["department"]
        self.employee_instance.additional_info = self.cleaned_data[
            "additional_info"
        ].strip()
        self.employee_instance.save()

        return self.user_instance


class CandidateEditForm(BaseUserEditForm, BaseAddressEditForm):
    """Edit form for candidate user + address + candidate profile."""

    education_level = forms.ChoiceField(
        label="Education Level",
        choices=Candidate.EducationLevel.choices,
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
        min_value=1,
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

    def __init__(
        self,
        *args,
        user_instance=None,
        address_instance=None,
        candidate_instance=None,
        **kwargs,
    ):
        """Initialize form with existing user, address, and candidate data."""
        self.candidate_instance = candidate_instance
        self.user_instance = user_instance or (
            candidate_instance.user if candidate_instance else None
        )
        self.address_instance = address_instance
        if not self.address_instance and self.user_instance:
            self.address_instance = getattr(self.user_instance, "address", None)
        super().__init__(*args, **kwargs)

        if self.user_instance and not self.is_bound:
            self.fields["first_name"].initial = self.user_instance.first_name
            self.fields["last_name"].initial = self.user_instance.last_name
            self.fields["email"].initial = self.user_instance.email
            self.fields["country_code"].initial = self.user_instance.country_code
            self.fields["phone"].initial = self.user_instance.phone
            self.fields["gender"].initial = self.user_instance.gender

        if self.address_instance and not self.is_bound:
            self.fields["street1"].initial = self.address_instance.street1
            self.fields["street2"].initial = self.address_instance.street2
            self.fields["city"].initial = self.address_instance.city
            self.fields["state"].initial = self.address_instance.state
            self.fields["country"].initial = self.address_instance.country
            self.fields["zip_code"].initial = self.address_instance.zip_code

        if self.candidate_instance and not self.is_bound:
            self.fields[
                "education_level"
            ].initial = self.candidate_instance.education_level
            self.fields[
                "university_name"
            ].initial = self.candidate_instance.university_name
            self.fields[
                "enrollment_number"
            ].initial = self.candidate_instance.enrollment_number
            self.fields["course_name"].initial = self.candidate_instance.course_name
            self.fields["semester"].initial = self.candidate_instance.semester
            self.fields["father_name"].initial = self.candidate_instance.father_name
            self.fields["mother_name"].initial = self.candidate_instance.mother_name
            self.fields["dob"].initial = self.candidate_instance.dob

    def clean_dob(self):
        """Validate that date of birth is in the past."""
        dob = self.cleaned_data["dob"]
        if dob >= timezone.localdate():
            raise forms.ValidationError("Date of birth must be in the past.")
        return dob

    def clean_enrollment_number(self):
        """Ensure enrollment number is unique among candidates."""
        enrollment_number = self.cleaned_data["enrollment_number"].strip()
        queryset = Candidate.objects.filter(enrollment_number=enrollment_number)
        if self.candidate_instance and self.candidate_instance.pk:
            queryset = queryset.exclude(pk=self.candidate_instance.pk)
        if queryset.exists():
            raise forms.ValidationError(
                "A candidate with this enrollment number already exists."
            )
        return enrollment_number

    @transaction.atomic
    def save(self):
        """Handle user, address, and candidate profile updates in a single transaction."""
        if not self.user_instance or not self.candidate_instance:
            raise ValueError("User and candidate instances are required.")

        self.user_instance.first_name = self.cleaned_data["first_name"].strip()
        self.user_instance.last_name = self.cleaned_data["last_name"].strip()
        self.user_instance.email = self.cleaned_data["email"]
        self.user_instance.country_code = self.cleaned_data["country_code"]
        self.user_instance.phone = self.cleaned_data["phone"]
        self.user_instance.gender = self.cleaned_data["gender"]
        if self.cleaned_data.get("profile_picture"):
            self.user_instance.profile_picture = self.cleaned_data["profile_picture"]
        self.user_instance.save()

        address_data = self._address_data()
        if self.address_instance:
            for key, value in address_data.items():
                setattr(self.address_instance, key, value)
            self.address_instance.save()
        else:
            Address.objects.create(user=self.user_instance, **address_data)

        self.candidate_instance.education_level = self.cleaned_data["education_level"]
        self.candidate_instance.university_name = self.cleaned_data[
            "university_name"
        ].strip()
        self.candidate_instance.enrollment_number = self.cleaned_data[
            "enrollment_number"
        ]
        self.candidate_instance.course_name = self.cleaned_data["course_name"].strip()
        self.candidate_instance.semester = self.cleaned_data["semester"]
        self.candidate_instance.father_name = self.cleaned_data["father_name"].strip()
        self.candidate_instance.mother_name = self.cleaned_data["mother_name"].strip()
        self.candidate_instance.dob = self.cleaned_data["dob"]
        self.candidate_instance.save()

        return self.user_instance


# ========================================
# OTP Related Forms
# ========================================


# Base OTP Verification Form
class BaseOtpVerificationForm(forms.Form):
    """Shared OTP validation form for all OTP verification actions."""

    otp_purpose = None
    otp_label = "OTP"
    invalid_message = "Invalid OTP."

    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit OTP"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["otp"].label = self.otp_label

    def clean_otp(self):
        """Validate OTP using utility function."""

        otp = self.cleaned_data["otp"].strip()

        if not otp.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")

        if not check_otp(self.user, otp, self.otp_purpose):
            raise forms.ValidationError(self.invalid_message)

        return otp


# Email Verification
class EmailVerifyOtpForm(BaseOtpVerificationForm):
    """Verify user's email address."""

    otp_label = "Email OTP"
    otp_purpose = OTP.OTPPurpose.EMAIL_VERIFY

    def save(self):
        """Mark email as verified."""
        self.user.email_verified = True
        self.user.save(update_fields=["email_verified"])


# Phone Verification
class PhoneVerifyOtpForm(BaseOtpVerificationForm):
    """Verify user's phone number."""

    otp_label = "Phone OTP"
    otp_purpose = OTP.OTPPurpose.PHONE_VERIFY

    def save(self):
        """Mark phone as verified."""
        self.user.phone_verified = True
        self.user.save(update_fields=["phone_verified"])


# Password Reset with OTP
class PasswordResetOtpForm(BaseOtpVerificationForm):
    """Verify OTP and reset password."""

    otp_label = "Password Reset OTP"
    otp_purpose = OTP.OTPPurpose.PASSWORD_RESET

    new_password1 = forms.CharField(
        label="New Password",
        help_text="Enter a strong password.",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New password"}
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        help_text="Re-enter the new password for confirmation.",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm new password"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        if password1:
            password_validation.validate_password(password1, self.user)

        return cleaned_data

    def save(self):
        """Update user password."""
        password = self.cleaned_data["new_password1"]

        self.user.set_password(password)
        self.user.save(update_fields=["password"])


# Email Change
class EmailChangeOtpForm(BaseOtpVerificationForm):
    """Verify OTP before changing email."""

    otp_label = "Email Change OTP"
    otp_purpose = OTP.OTPPurpose.EMAIL_CHANGE

    new_email = forms.EmailField(
        label="New Email Address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "New email"}
        ),
    )

    def clean_new_email(self):
        """Validate that new email is not already in use and normalize it."""
        email = self.cleaned_data["new_email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return email

    def save(self):
        """Update email and mark unverified."""

        new_email = self.cleaned_data["new_email"]

        self.user.email = new_email
        self.user.email_verified = False

        self.user.save(update_fields=["email", "email_verified"])


# Phone Change
class PhoneChangeOtpForm(BaseOtpVerificationForm):
    """Verify OTP before changing phone number."""

    otp_label = "Phone Change OTP"
    otp_purpose = OTP.OTPPurpose.PHONE_CHANGE

    new_country_code = forms.CharField(
        label="New Country Code",
        max_length=5,
        validators=[country_code_validator],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91"}),
    )

    new_phone = forms.CharField(
        label="New Phone Number",
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "New phone number"}
        ),
    )

    def clean(self):
        """Validate new phone number and check for duplicates."""
        cleaned_data = super().clean()

        code = (cleaned_data.get("new_country_code") or "").strip()
        phone = (cleaned_data.get("new_phone") or "").strip()

        cleaned_data["new_country_code"] = code
        cleaned_data["new_phone"] = phone

        if (
            User.objects.filter(country_code=code, phone=phone)
            .exclude(pk=self.user.pk)
            .exists()
        ):
            raise forms.ValidationError("This phone number is already in use.")

        return cleaned_data

    def save(self):
        """Update phone and mark unverified."""

        code = self.cleaned_data["new_country_code"]
        phone = self.cleaned_data["new_phone"]

        self.user.country_code = code
        self.user.phone = phone
        self.user.phone_verified = False

        self.user.save(update_fields=["country_code", "phone", "phone_verified"])


# Enable 2FA
class Set2FAOtpForm(BaseOtpVerificationForm):
    """Enable two-factor authentication."""

    otp_label = "2FA Setup OTP"
    otp_purpose = OTP.OTPPurpose.SET_2FA

    # QR code generation is handled in the view, so we don't generate it here.
    # def __init__(self, user, *args, **kwargs):
    #     """Initialize form and generate QR code for authenticator app."""
    #     super().__init__(user, *args, **kwargs)
    #     self.image_label = "Scan the QR code below with your authenticator app:"
    #     self.image_qr_path = generate_totp(self.user)

    token = forms.CharField(
        label="Authenticator Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit code"}
        ),
    )

    def clean_token(self):
        """Validate TOTP token using utility function."""
        token = self.cleaned_data["token"].strip()

        if not token.isdigit():
            raise forms.ValidationError("Authenticator code must contain only digits.")
        return token

    def save(self):
        """Enable TOTP using utility function."""
        turn_on_totp(self.user, self.cleaned_data["token"].strip())


# Disable 2FA
class Remove2FAOtpForm(BaseOtpVerificationForm):
    """Disable two-factor authentication. Email OTP is sent."""

    otp_label = "2FA Removal OTP"
    otp_purpose = OTP.OTPPurpose.REMOVE_2FA

    def clean(self):
        cleaned_data = super().clean()

        if not self.user.is_2FA_enabled:
            raise forms.ValidationError("Two-factor authentication is not enabled.")

        return cleaned_data

    def save(self):
        """Disable TOTP using utility function."""

        disable_totp(self.user)


# Authenticator App Verification
class TOTPVerificationForm(forms.Form):
    """Verify authenticator app code."""

    token = forms.CharField(
        label="Authenticator Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit code"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """Initialize form with user for TOTP validation."""
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_token(self):
        """Validate TOTP token using utility function."""
        token = self.cleaned_data["token"].strip()

        if not token.isdigit():
            raise forms.ValidationError("Authenticator code must contain only digits.")

        if not validate_totp(self.user, token):
            raise forms.ValidationError("Invalid authenticator code.")

        return token


# Request Password Reset OTP
class PasswordResetRequestForm(forms.Form):
    """Request password reset OTP."""

    email = forms.EmailField(
        label="Email Address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email address"}
        ),
    )

    def clean_email(self):
        """Validate that email exists and normalize it."""
        email = self.cleaned_data["email"].strip().lower()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No account found with this email.")

        self.user = user
        return email

    def save(self):
        """Send password reset OTP using utility function."""
        send_email_otp(self.user, OTP.OTPPurpose.PASSWORD_RESET)
