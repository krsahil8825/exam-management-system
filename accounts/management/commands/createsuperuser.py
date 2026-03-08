"""Custom createsuperuser command that can also capture address details."""

from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management.base import CommandError

from ...models import Address


class Command(BaseCommand):
    """Create a superuser and optionally create the related address record."""

    help = "Create a superuser and optionally capture address details."

    ADDRESS_FIELDS = ("street1", "street2", "city", "state", "country", "zip_code")

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--street1", default="")
        parser.add_argument("--street2", default="")
        parser.add_argument("--city", default="")
        parser.add_argument("--state", default="")
        parser.add_argument("--country", default="")
        parser.add_argument("--zip-code", dest="zip_code", default="")
        parser.add_argument(
            "--skip-address",
            action="store_true",
            help="Skip address creation for the new superuser.",
        )

    def _resolve_created_superuser(self, before_ids):
        return (
            self.UserModel.objects.filter(is_superuser=True)
            .exclude(id__in=before_ids)
            .order_by("-id")
            .first()
        )

    def _prompt(self, label, required=False):
        value = input(f"{label}: ").strip()
        if required and not value:
            raise CommandError(f"{label} is required.")
        return value

    def _collect_address_data(self, options):
        interactive = options.get("interactive", True)

        if interactive:
            self.stdout.write("\nEnter address details")
            return {
                "street1": self._prompt("Street1", required=True),
                "street2": self._prompt("Street2 (optional)", required=False),
                "city": self._prompt("City", required=True),
                "state": self._prompt("State", required=True),
                "country": self._prompt("Country", required=True),
                "zip_code": self._prompt("Zip code", required=True),
            }

        data = {field: (options.get(field) or "").strip() for field in self.ADDRESS_FIELDS}
        required_fields = ("street1", "city", "state", "country", "zip_code")
        missing = [field for field in required_fields if not data[field]]
        if missing:
            joined = ", ".join(missing)
            raise CommandError(
                "Missing required address fields in non-interactive mode: "
                f"{joined}. Use --skip-address to skip."
            )
        return data

    def handle(self, *args, **options):
        self.stdout.write("Creating superuser account...")

        before_ids = set(
            self.UserModel.objects.filter(is_superuser=True).values_list("id", flat=True)
        )

        super().handle(*args, **options)

        user = self._resolve_created_superuser(before_ids)
        if not user:
            self.stdout.write(self.style.WARNING("No new superuser was created."))
            return

        if options.get("skip_address"):
            self.stdout.write(self.style.WARNING("Address creation skipped."))
            return

        if Address.objects.filter(user=user).exists():
            self.stdout.write(self.style.WARNING("Address already exists for this superuser."))
            return

        address_data = self._collect_address_data(options)
        Address.objects.create(user=user, **address_data)
        self.stdout.write(self.style.SUCCESS("Superuser address saved successfully."))
