from django.core.management.base import BaseCommand

from bookings.services.legal import seed_legal_documents


class Command(BaseCommand):
    help = "Seed backend-managed legal documents from docs/legal without printing document content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--activate",
            action="store_true",
            help="Explicitly publish seeded documents as active business-approved policies.",
        )

    def handle(self, *args, **options):
        seed_legal_documents(activate=options["activate"], stdout=self.stdout)
