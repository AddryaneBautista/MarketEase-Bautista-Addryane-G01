from django import forms
from .models import StallType


class StallTypeForm(forms.ModelForm):
    class Meta:
        model = StallType
        fields = ["name", "description"]
