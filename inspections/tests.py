from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from locations.models import Location
from sections.models import Section
from stall_types.models import StallType
from stalls.models import Stall
from .models import Inspection


class InspectionModelTests(TestCase):
    def test_inspection_uses_stalls_model(self):
        inspector = get_user_model().objects.create_user(username="inspector")
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

        inspection = Inspection.objects.create(
            stall=stall,
            inspector=inspector,
            inspection_date=timezone.localdate(),
            result=Inspection.PASSED,
        )

        self.assertEqual(inspection.stall, stall)
        self.assertEqual(stall.inspections.get(), inspection)
