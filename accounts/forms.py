"""
accounts.forms
~~~~~~~~~~~~~

Forms for user registration, login, profile editing, and OTP verification.
"""

from datetime import timedelta

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.utils import timezone

from .models import Address, Candidate, Employee, GenderChoices, User
from .utils.validate import (
    country_code_validator,
    phone_validator,
    validate_profile_photo,
)


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
    gender = forms.ChoiceField(
        label="Gender",
        choices=GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
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
            gender=self.cleaned_data["gender"],
        )
        return user


class EmployeeRegistrationForm(BaseUserForm, BaseAddressForm):
    """Registration form for employees."""

    gender = forms.ChoiceField(
        label="Gender",
        choices=GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
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
            gender=self.cleaned_data["gender"],
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

    gender = forms.ChoiceField(
        label="Gender",
        choices=GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
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

        if self.address_instance and not self.is_bound:
            self.fields["street1"].initial = self.address_instance.street1
            self.fields["street2"].initial = self.address_instance.street2
            self.fields["city"].initial = self.address_instance.city
            self.fields["state"].initial = self.address_instance.state
            self.fields["country"].initial = self.address_instance.country
            self.fields["zip_code"].initial = self.address_instance.zip_code

        if self.employee_instance and not self.is_bound:
            self.fields["gender"].initial = self.employee_instance.gender
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

        self.employee_instance.gender = self.cleaned_data["gender"]
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
    gender = forms.ChoiceField(
        label="Gender",
        choices=GenderChoices.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
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
            self.fields["gender"].initial = self.candidate_instance.gender

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
        self.candidate_instance.gender = self.cleaned_data["gender"]
        self.candidate_instance.save()

        return self.user_instance


class BaseOtpVerificationForm(forms.Form):
    """Shared OTP validation form for timestamp-based OTP fields."""

    OTP_EXPIRATION_MINUTES = 10
    otp_label = "OTP"
    otp_field_name = ""
    otp_timestamp_field_name = ""
    invalid_message = "Invalid OTP."
    missing_message = "No OTP found. Please request a new OTP."
    expired_message = "OTP has expired."

    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit OTP"}
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """Initialize form with user and set OTP field label."""
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["otp"].label = self.otp_label

    def clean_otp(self):
        """Validate OTP against user's stored OTP and check expiration."""
        otp = self.cleaned_data["otp"].strip()
        expected_otp = getattr(self.user, self.otp_field_name, None)
        created_at = getattr(self.user, self.otp_timestamp_field_name, None)

        if not expected_otp:
            raise forms.ValidationError(self.missing_message)
        if not created_at:
            raise forms.ValidationError(
                "OTP timestamp missing. Please request a new OTP."
            )
        if otp != expected_otp:
            raise forms.ValidationError(self.invalid_message)

        expires_at = created_at + timedelta(minutes=self.OTP_EXPIRATION_MINUTES)
        if timezone.now() > expires_at:
            raise forms.ValidationError(self.expired_message)
        return otp


class EmailOtpVerificationForm(BaseOtpVerificationForm):
    """Form for verifying email OTP."""

    otp_label = "Email OTP"
    otp_field_name = "email_OTP"
    otp_timestamp_field_name = "email_OTP_created_at"
    invalid_message = "Invalid email OTP."
    missing_message = "No email OTP found. Please request a new OTP."
    expired_message = "Email OTP has expired."


class PhoneOtpVerificationForm(BaseOtpVerificationForm):
    """Form for verifying phone OTP."""

    otp_label = "Phone OTP"
    otp_field_name = "phone_OTP"
    otp_timestamp_field_name = "phone_OTP_created_at"
    invalid_message = "Invalid phone OTP."
    missing_message = "No phone OTP found. Please request a new OTP."
    expired_message = "Phone OTP has expired."


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset OTP."""

    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com"}
        ),
    )

    def clean_email(self):
        """Validate that email exists in the system."""
        email = self.cleaned_data["email"].strip().lower()
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email


class SetNewPasswordForm(forms.Form):
    """Form for validating OTP and setting a new password."""

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
        """Initialize form with user for OTP validation."""
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        """Validate OTP, check expiration, and ensure new passwords match."""
        cleaned_data = super().clean()
        otp = (cleaned_data.get("otp") or "").strip()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        if not self.user.password_otp:
            raise forms.ValidationError("No password reset OTP found.")
        if not self.user.password_otp_created_at:
            raise forms.ValidationError("OTP timestamp missing. Request a new OTP.")
        if otp != self.user.password_otp:
            raise forms.ValidationError("Invalid OTP.")

        expiration_time = self.user.password_otp_created_at + timedelta(
            minutes=self.OTP_EXPIRATION_MINUTES
        )
        if timezone.now() > expiration_time:
            raise forms.ValidationError("OTP has expired.")

        if password1:
            password_validation.validate_password(password1, self.user)

        return cleaned_data
