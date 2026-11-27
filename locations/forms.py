from django import forms
from agreements.models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description"]
