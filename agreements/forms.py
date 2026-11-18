from django import forms
from django.db import transaction
from django.db.models import Q

from .models import RentalAgreement, Stall, Vendor

class RentalAgreementForm(forms.ModelForm):
    class Meta:
        model = RentalAgreement
        fields = ["vendor", "stall", "start_date", "end_date", "monthly_rate", "status"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_stall_id = self.instance.stall_id if self.instance.pk else None
        stall_q, vendor_q = Q(status=Stall.AVAILABLE), Q(is_active=True)
        if self.instance.pk:
            stall_q |= Q(pk=self.instance.stall_id)
            vendor_q |= Q(pk=self.instance.vendor_id)
        self.fields["stall"].queryset = Stall.objects.filter(stall_q).select_related("section")
        self.fields["vendor"].queryset = Vendor.objects.filter(vendor_q)

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        rate, stall, status = cleaned.get("monthly_rate"), cleaned.get("stall"), cleaned.get("status")
        if start and end and end <= start:
            self.add_error("end_date", "End date must be later than the start date.")
        if rate is not None and rate <= 0:
            self.add_error("monthly_rate", "Monthly rate must be greater than zero.")
        if stall and status == RentalAgreement.ACTIVE:
            if stall.status == Stall.MAINTENANCE:
                self.add_error("stall", "This stall is under maintenance.")
            elif (RentalAgreement.objects
                  .filter(stall=stall, status=RentalAgreement.ACTIVE)
                  .exclude(pk=self.instance.pk).exists()):
                self.add_error("stall", "This stall already has an active agreement.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        agreement = super().save(commit=False)
        agreement.save()
        if self._old_stall_id and self._old_stall_id != agreement.stall_id:
            Stall.objects.filter(pk=self._old_stall_id, status=Stall.OCCUPIED) \
                .update(status=Stall.AVAILABLE)
        stall = agreement.stall
        if agreement.status == RentalAgreement.ACTIVE:
            stall.status = Stall.OCCUPIED
            stall.save(update_fields=["status"])
        elif stall.status == Stall.OCCUPIED:
            stall.status = Stall.AVAILABLE
            stall.save(update_fields=["status"])
        return agreement
