"""
communication.forms
~~~~~~~~~~~~~~~~~~~

Forms for creating and editing employee messages.
"""

from django import forms

from accounts.models import Employee
from .models import Messages


class BaseMessageForm(forms.Form):
    """Shared fields and validation used by message forms."""

    subject = forms.CharField(
        label="Subject",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter message subject",
            }
        ),
    )

    content = forms.CharField(
        label="Message",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write your message here",
            }
        ),
    )

    attachment = forms.FileField(
        label="Attachment",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    def clean_subject(self):
        """Normalize subject."""
        subject = self.cleaned_data["subject"].strip()

        if not subject:
            raise forms.ValidationError("Subject cannot be empty.")

        return subject

    def clean_content(self):
        """Normalize content."""
        content = self.cleaned_data["content"].strip()

        if not content:
            raise forms.ValidationError("Message content cannot be empty.")

        return content

    def clean_attachment(self):
        """Validate attachment size (max 5MB)."""

        MAX_SIZE = 5 * 1024 * 1024
        file = self.cleaned_data.get("attachment")

        if not file:
            return file

        if file.size > MAX_SIZE:
            raise forms.ValidationError("Attachment size cannot exceed 5 MB.")

        return file


class MessageCreateForm(BaseMessageForm):
    """Form used for sending a new message."""

    receiver = forms.ModelChoiceField(
        label="Send To",
        queryset=Employee.objects.none(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, sender=None, **kwargs):
        """Limit receiver choices so sender cannot message themselves."""
        super().__init__(*args, **kwargs)

        self.sender = sender

        if sender:
            self.fields["receiver"].queryset = (
                Employee.objects.select_related("user")
                .exclude(pk=sender.pk)
                .order_by("user__first_name")
            )

    def clean_receiver(self):
        """Prevent sending message to self."""
        receiver = self.cleaned_data["receiver"]

        if self.sender and receiver.pk == self.sender.pk:
            raise forms.ValidationError("You cannot send a message to yourself.")

        return receiver

    def save(self):
        """Create and save a new message."""

        if not self.sender:
            raise ValueError("Sender must be provided.")

        message = Messages.objects.create(
            sender=self.sender,
            receiver=self.cleaned_data["receiver"],
            subject=self.cleaned_data["subject"],
            content=self.cleaned_data["content"],
            attachment=self.cleaned_data.get("attachment"),
        )

        return message


class MessageEditForm(BaseMessageForm):
    """Form for editing an existing message."""

    def __init__(self, *args, message_instance=None, **kwargs):
        """Initialize form with existing message."""
        super().__init__(*args, **kwargs)

        self.message_instance = message_instance

        if self.message_instance and not self.is_bound:
            self.fields["subject"].initial = self.message_instance.subject
            self.fields["content"].initial = self.message_instance.content

    def save(self):
        """Update the existing message."""

        if not self.message_instance:
            raise ValueError("Message instance is required.")

        self.message_instance.subject = self.cleaned_data["subject"]
        self.message_instance.content = self.cleaned_data["content"]

        if self.cleaned_data.get("attachment"):
            self.message_instance.attachment = self.cleaned_data["attachment"]

        self.message_instance.save()

        return self.message_instance
