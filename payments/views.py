from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from .forms import PaymentForm
from .models import Payment

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class PaymentListView(LoginRequiredMixin, ListView):
    template_name = "payments/payment_list.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        Payment.refresh_overdue()
        qs = Payment.objects.select_related("rental_agreement__vendor", "rental_agreement__stall")
        if self.request.user.role not in MANAGER_ROLES:
            qs = qs.filter(rental_agreement__vendor__user=self.request.user)
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(Q(rental_agreement__vendor__first_name__icontains=q)
                           | Q(rental_agreement__vendor__last_name__icontains=q)
                           | Q(rental_agreement__stall__stall_number__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Payment.STATUS_CHOICES
        ctx["can_manage"] = self.request.user.role in MANAGER_ROLES
        return ctx


class PaymentCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"
    success_url = reverse_lazy("payments:list")
    success_message = "Payment recorded."

    def form_valid(self, form):
        form.instance.received_by = self.request.user
        return super().form_valid(form)


class PaymentUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = "payments/payment_form.html"
    success_url = reverse_lazy("payments:list")
    success_message = "Payment updated."

    def form_valid(self, form):
        form.instance.received_by = self.request.user
        return super().form_valid(form)


class PaymentDeleteView(StaffRequiredMixin, DeleteView):
    model = Payment
    template_name = "payments/payment_confirm_delete.html"
    success_url = reverse_lazy("payments:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this payment has related records.")
        else:
            messages.success(self.request, "Payment deleted.")
        return redirect(self.success_url)
