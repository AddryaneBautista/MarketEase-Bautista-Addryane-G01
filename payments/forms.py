from django import forms
from django.db.models import Q
from django.utils import timezone

from agreements.models import RentalAgreement
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["rental_agreement", "billing_month", "due_date",
                  "payment_date", "amount_due", "amount_paid"]
        widgets = {
            "billing_month": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        q = Q(status=RentalAgreement.ACTIVE)
        if self.instance.pk:
            q |= Q(pk=self.instance.rental_agreement_id)
        self.fields["rental_agreement"].queryset = (
            RentalAgreement.objects.filter(q).select_related("vendor", "stall")
        )
        self.fields["billing_month"].help_text = "Normalized to the first day of the month."
        self.fields["amount_paid"].initial = 0

    def clean_billing_month(self):
        return self.cleaned_data["billing_month"].replace(day=1)

    def clean(self):
        cleaned = super().clean()
        due, paid = cleaned.get("amount_due"), cleaned.get("amount_paid")
        if due is not None and due <= 0:
            self.add_error("amount_due", "Amount due must be greater than zero.")
        if paid is not None and paid < 0:
            self.add_error("amount_paid", "Amount paid cannot be negative.")
        if due and paid is not None and paid > due:
            self.add_error("amount_paid", "Amount paid cannot exceed the amount due.")
        if paid and paid > 0 and not cleaned.get("payment_date"):
            cleaned["payment_date"] = timezone.localdate()
        return cleaned
