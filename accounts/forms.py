from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q

from agreements.models import Vendor
from .models import CustomUser


def _vendor_queryset(user=None):
    q = Q(user__isnull=True)
    if user is not None and user.pk:
        q |= Q(user=user)
    return Vendor.objects.filter(q).order_by("last_name", "first_name")


def _link_vendor(user, vendor):
    if user.role != CustomUser.Role.VENDOR:
        vendor = None
    Vendor.objects.filter(user=user).exclude(pk=getattr(vendor, "pk", None)).update(user=None)
    if vendor:
        vendor.user = user
        vendor.save(update_fields=["user"])


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")


class AdminUserCreateForm(UserCreationForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.none(), required=False,
                                    label="Link to vendor record")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vendor"].queryset = _vendor_queryset()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("vendor") and cleaned.get("role") != CustomUser.Role.VENDOR:
            self.add_error("vendor", "Only VENDOR accounts can be linked to a vendor record.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        _link_vendor(user, self.cleaned_data.get("vendor"))
        return user


class AdminUserUpdateForm(forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.none(), required=False,
                                    label="Link to vendor record")

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "role", "is_active")

    def __init__(self, *args, acting_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.acting_user = acting_user
        self.fields["vendor"].queryset = _vendor_queryset(self.instance)
        self.fields["vendor"].initial = Vendor.objects.filter(user=self.instance).first()

    def clean(self):
        cleaned = super().clean()
        role, vendor = cleaned.get("role"), cleaned.get("vendor")
        if vendor and role != CustomUser.Role.VENDOR:
            self.add_error("vendor", "Only VENDOR accounts can be linked to a vendor record.")
        if self.acting_user and self.instance.pk == self.acting_user.pk:
            if cleaned.get("is_active") is False:
                self.add_error("is_active", "You cannot deactivate your own account.")
            if role and role != self.instance.role:
                self.add_error("role", "You cannot change your own role.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=True)
        _link_vendor(user, self.cleaned_data.get("vendor"))
        return user
