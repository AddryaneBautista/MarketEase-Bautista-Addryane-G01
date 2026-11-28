from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from .forms import ViolationForm
from .models import Violation

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class ViolationListView(StaffRequiredMixin, ListView):
    template_name = "violations/violation_list.html"
    context_object_name = "violations"
    paginate_by = 10

    def get_queryset(self):
        qs = Violation.objects.select_related("vendor", "stall")
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(Q(vendor__first_name__icontains=q) | Q(vendor__last_name__icontains=q)
                           | Q(stall__stall_number__icontains=q) | Q(description__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Violation.STATUS_CHOICES
        return ctx


class ViolationCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Violation
    form_class = ViolationForm
    template_name = "violations/violation_form.html"
    success_url = reverse_lazy("violations:list")
    success_message = "Violation recorded."


class ViolationUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Violation
    form_class = ViolationForm
    template_name = "violations/violation_form.html"
    success_url = reverse_lazy("violations:list")
    success_message = "Violation updated."


class ViolationDeleteView(StaffRequiredMixin, DeleteView):
    model = Violation
    template_name = "violations/violation_confirm_delete.html"
    success_url = reverse_lazy("violations:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this violation has related records.")
        else:
            messages.success(self.request, "Violation deleted.")
        return redirect(self.success_url)
