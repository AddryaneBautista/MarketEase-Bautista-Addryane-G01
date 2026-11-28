from django import forms
from django.db.models import Q

from accounts.models import CustomUser
from .models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["user", "first_name", "last_name", "business_name",
                  "contact_number", "address", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        free = Q(vendor__isnull=True)
        if self.instance.user_id:
            free |= Q(pk=self.instance.user_id)
        self.fields["user"].queryset = CustomUser.objects.filter(role=CustomUser.Role.VENDOR).filter(free)
        self.fields["user"].label = "Login account"
