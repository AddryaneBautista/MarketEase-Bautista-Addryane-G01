from django import forms
from agreements.models import Section


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["location", "name"]
