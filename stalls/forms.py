from django import forms
from agreements.models import Stall


class StallForm(forms.ModelForm):
    class Meta:
        model = Stall
        fields = ["section", "stall_type", "stall_number", "area_sqm", "monthly_rate", "status"]

    def clean(self):
        cleaned = super().clean()
        area, rate, status = cleaned.get("area_sqm"), cleaned.get("monthly_rate"), cleaned.get("status")
        if area is not None and area <= 0:
            self.add_error("area_sqm", "Area must be greater than zero.")
        if rate is not None and rate <= 0:
            self.add_error("monthly_rate", "Monthly rate must be greater than zero.")
        if status:
            has_active = bool(self.instance.pk) and self.instance.agreements.filter(status="ACTIVE").exists()
            if has_active and status != Stall.OCCUPIED:
                self.add_error("status", "This stall has an active agreement. End the agreement first.")
            elif not has_active and status == Stall.OCCUPIED:
                self.add_error("status", "Occupied status is set by creating an active agreement.")
        return cleaned
