from django import forms
from django.db.models import Q

from agreements.models import Vendor
from .models import Violation


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ["vendor", "stall", "inspection", "description",
                  "violation_date", "fine_amount", "status"]
        widgets = {"violation_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        q = Q(is_active=True)
        if self.instance.pk:
            q |= Q(pk=self.instance.vendor_id)
        self.fields["vendor"].queryset = Vendor.objects.filter(q)

    def clean(self):
        cleaned = super().clean()
        fine, stall, inspection = cleaned.get("fine_amount"), cleaned.get("stall"), cleaned.get("inspection")
        if fine is not None and fine < 0:
            self.add_error("fine_amount", "Fine cannot be negative.")
        if stall and inspection and inspection.stall_id != stall.pk:
            self.add_error("inspection", "This inspection belongs to a different stall.")
        return cleaned
