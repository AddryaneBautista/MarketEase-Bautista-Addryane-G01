from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from .forms import VendorForm
from .models import Vendor

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class VendorListView(StaffRequiredMixin, ListView):
    template_name = "vendors/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 10

    def get_queryset(self):
        qs = Vendor.objects.select_related("user").order_by("last_name", "first_name")
        q = self.request.GET.get("q", "").strip()
        active = self.request.GET.get("active", "")
        if q:
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q)
                           | Q(business_name__icontains=q) | Q(contact_number__icontains=q))
        if active in ("1", "0"):
            qs = qs.filter(is_active=active == "1")
        return qs


class VendorCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = "vendors/vendor_form.html"
    success_url = reverse_lazy("vendors:list")
    success_message = "Vendor created."


class VendorUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = "vendors/vendor_form.html"
    success_url = reverse_lazy("vendors:list")
    success_message = "Vendor updated."


class VendorDeleteView(StaffRequiredMixin, DeleteView):
    model = Vendor
    template_name = "vendors/vendor_confirm_delete.html"
    success_url = reverse_lazy("vendors:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this vendor has agreements or violations. Deactivate the vendor instead.")
        else:
            messages.success(self.request, "Vendor deleted.")
        return redirect(self.success_url)
