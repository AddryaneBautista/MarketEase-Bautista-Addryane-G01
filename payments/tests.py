from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from agreements.models import Agreement
from locations.models import Location
from sections.models import Section
from stall_types.models import StallType
from stalls.models import Stall
from vendors.models import Vendor
from .models import Payment


class PaymentModelTests(TestCase):
    def test_payment_status_is_saved_when_amount_is_paid(self):
        location = Location.objects.create(name="Main Market")
        section = Section.objects.create(location=location, name="A")
        stall_type = StallType.objects.create(name="Regular")
        stall = Stall.objects.create(
            section=section,
            stall_type=stall_type,
            stall_number="A-1",
            area_sqm="10.00",
            monthly_rate="1000.00",
        )
        vendor = Vendor.objects.create(
            first_name="Test",
            last_name="Vendor",
            contact_number="09170000000",
            address="Test address",
        )
        today = timezone.localdate()
        agreement = Agreement.objects.create(
            vendor=vendor,
            stall=stall,
            start_date=today,
            end_date=today + timedelta(days=365),
            monthly_rate=Decimal("1000.00"),
        )

        payment = Payment.objects.create(
            agreement=agreement,
            billing_month=today.replace(day=1),
            due_date=today + timedelta(days=7),
            amount_due=Decimal("1000.00"),
            amount_paid=Decimal("1000.00"),
        )

        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.PAID)
