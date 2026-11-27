from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from agreements.models import StallType
from .forms import StallTypeForm

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class StallTypeListView(StaffRequiredMixin, ListView):
    template_name = "stall_types/stall_type_list.html"
    context_object_name = "stall_types"
    paginate_by = 10

    def get_queryset(self):
        qs = StallType.objects.annotate(stall_count=Count("stalls")).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs


class StallTypeCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = StallType
    form_class = StallTypeForm
    template_name = "stall_types/stall_type_form.html"
    success_url = reverse_lazy("stall_types:list")
    success_message = "Stall type created."


class StallTypeUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StallType
    form_class = StallTypeForm
    template_name = "stall_types/stall_type_form.html"
    success_url = reverse_lazy("stall_types:list")
    success_message = "Stall type updated."


class StallTypeDeleteView(StaffRequiredMixin, DeleteView):
    model = StallType
    template_name = "stall_types/stall_type_confirm_delete.html"
    success_url = reverse_lazy("stall_types:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this stall type is used by stalls.")
        else:
            messages.success(self.request, "Stall type deleted.")
        return redirect(self.success_url)
