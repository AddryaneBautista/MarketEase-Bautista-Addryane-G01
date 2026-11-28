from django.test import TestCase
from django.utils import timezone

from locations.models import Location
from sections.models import Section
from stall_types.models import StallType
from stalls.models import Stall
from vendors.models import Vendor
from .models import Violation


class ViolationModelTests(TestCase):
    def test_violation_uses_vendor_and_stall_models(self):
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

        violation = Violation.objects.create(
            vendor=vendor,
            stall=stall,
            violation_date=timezone.localdate(),
            description="Test violation",
        )

        self.assertEqual(violation.vendor, vendor)
        self.assertEqual(violation.stall, stall)
