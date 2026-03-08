"""
createsuperuser.py
~~~~~~~~~~~~~~~~~~

Custom management command to create a superuser with address details.
"""

from django.contrib.auth.management.commands.createsuperuser import (
    Command as BaseCommand,
)
from accounts.models import Address


class Command(BaseCommand):
    """Custom command to create a superuser and prompt for address details."""

    def handle(self, *args, **options):
        """Handle the command execution."""

        self.stdout.write("Creating superuser account...")

        # Run default Django superuser creation
        super().handle(*args, **options)

        # Get latest created superuser
        User = self.UserModel
        user = User.objects.filter(is_superuser=True).latest("id")

        self.stdout.write("\nEnter address details")

        street1 = input("Street1: ")
        street2 = input("Street2 (optional): ")
        city = input("City: ")
        state = input("State: ")
        country = input("Country: ")
        zip_code = input("Zip code: ")

        Address.objects.create(
            user=user,
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            country=country,
            zip_code=zip_code,
        )

        self.stdout.write(self.style.SUCCESS("Superuser address saved successfully."))
