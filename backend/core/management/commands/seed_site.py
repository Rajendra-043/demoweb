"""
Creates the initial site structure: settings, every page, navigation links,
socials and a few editable example sections.

Safe to re-run -- it only fills in what is missing.

    python manage.py seed_site
    python manage.py seed_site --reset-content   (wipes demo events etc.)

Note: the same provisioning also runs automatically as part of the
``core.0003_provision_default_pages`` migration, so a brand new database is
never left without pages.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Accommodation, Competition, Event, Workshop
from core.seeding import provision_site


class Command(BaseCommand):
    help = "Create the initial TECNO site structure (pages, navigation, settings)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-content",
            action="store_true",
            help="Also delete existing events, workshops, competitions and accommodation.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Windows consoles default to cp1252 and choke on the ✓ / · glyphs.
        try:
            self.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

        def log(message):
            self.stdout.write(message)

        provision_site(log=log)

        if options["reset_content"]:
            Event.objects.all().delete()
            Workshop.objects.all().delete()
            Competition.objects.all().delete()
            Accommodation.objects.all().delete()
            self.stdout.write(self.style.WARNING("• Cleared existing content rows"))
            return

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed complete. Start the server: python manage.py runserver"))