from django.core.management.base import BaseCommand

from agreements.models import RentalAgreement


class Command(BaseCommand):
    help = "Mark ACTIVE agreements past their end date as EXPIRED and free their stalls."

    def handle(self, *args, **options):
        count = RentalAgreement.expire_past_due()
        self.stdout.write(self.style.SUCCESS(f"{count} agreement(s) expired."))
