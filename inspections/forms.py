from django import forms
from .models import Inspection


class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ["stall", "inspection_date", "findings", "result"]
        widgets = {"inspection_date": forms.DateInput(attrs={"type": "date"})}
