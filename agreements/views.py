from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.models import CustomUser
from .forms import RentalAgreementForm
from .models import RentalAgreement, Stall

# Create your views here.
Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)

def visible_agreements(user):
    qs = RentalAgreement.objects.select_related("vendor", "stall", "stall__section", "created_by")
    if user.role in MANAGER_ROLES:
        return qs
    return qs.filter(vendor__user=user)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class AgreementListView(LoginRequiredMixin, ListView):
    template_name = "agreements/agreement_list.html"
    context_object_name = "agreements"
    paginate_by = 10

    def get_queryset(self):
        qs = visible_agreements(self.request.user)
        status, q = self.request.GET.get("status"), self.request.GET.get("q")
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(
                Q(vendor__first_name__icontains=q)
                | Q(vendor__last_name__icontains=q)
                | Q(stall__stall_number__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = RentalAgreement.STATUS_CHOICES
        ctx["can_manage"] = self.request.user.role in MANAGER_ROLES
        return ctx


class AgreementDetailView(LoginRequiredMixin, DetailView):
    template_name = "agreements/agreement_detail.html"
    context_object_name = "agreement"

    def get_queryset(self):
        return visible_agreements(self.request.user)


class AgreementCreateView(StaffRequiredMixin, CreateView):
    form_class = RentalAgreementForm
    template_name = "agreements/agreement_form.html"
    success_url = reverse_lazy("agreements:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Rental agreement created.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class AgreementUpdateView(StaffRequiredMixin, UpdateView):
    model = RentalAgreement
    form_class = RentalAgreementForm
    template_name = "agreements/agreement_form.html"
    success_url = reverse_lazy("agreements:list")

    def form_valid(self, form):
        messages.success(self.request, "Rental agreement updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class AgreementDeleteView(StaffRequiredMixin, DeleteView):
    model = RentalAgreement
    template_name = "agreements/agreement_confirm_delete.html"
    success_url = reverse_lazy("agreements:list")

    def form_valid(self, form):
        agreement = self.object
        try:
            with transaction.atomic():
                stall_id = agreement.stall_id
                was_active = agreement.status == RentalAgreement.ACTIVE
                agreement.delete()
                if was_active:
                    Stall.objects.filter(pk=stall_id, status=Stall.OCCUPIED) \
                        .update(status=Stall.AVAILABLE)
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this agreement has related records (e.g., payments).")
            return redirect("agreements:list")
        messages.success(self.request, "Rental agreement deleted.")
        return redirect(self.success_url)
