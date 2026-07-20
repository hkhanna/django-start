from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Seed local db for development purposes"

    @transaction.atomic
    def handle(self, *args, **options):
        # -- Users -- #
        email = "admin@localhost"
        password = "admin"  # noqa: S105
        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(
            f"\n**--> Created superuser {email} with password {password} <--**\n"
        )
