from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from sections.models import Section
from stall_types.models import StallType
from .forms import StallForm
from .models import Stall

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class StallListView(StaffRequiredMixin, ListView):
    template_name = "stalls/stall_list.html"
    context_object_name = "stalls"
    paginate_by = 10

    def get_queryset(self):
        qs = Stall.objects.select_related("section__location", "stall_type").order_by("stall_number")
        g = self.request.GET
        q = g.get("q", "").strip()
        if q:
            qs = qs.filter(Q(stall_number__icontains=q) | Q(section__name__icontains=q)
                           | Q(stall_type__name__icontains=q))
        if g.get("status"):
            qs = qs.filter(status=g["status"])
        if g.get("section", "").isdigit():
            qs = qs.filter(section_id=g["section"])
        if g.get("type", "").isdigit():
            qs = qs.filter(stall_type_id=g["type"])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Stall.STATUS_CHOICES
        ctx["sections"] = Section.objects.select_related("location").order_by("location__name", "name")
        ctx["types"] = StallType.objects.order_by("name")
        return ctx


class StallCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Stall
    form_class = StallForm
    template_name = "stalls/stall_form.html"
    success_url = reverse_lazy("stalls:list")
    success_message = "Stall created."


class StallUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Stall
    form_class = StallForm
    template_name = "stalls/stall_form.html"
    success_url = reverse_lazy("stalls:list")
    success_message = "Stall updated."


class StallDeleteView(StaffRequiredMixin, DeleteView):
    model = Stall
    template_name = "stalls/stall_confirm_delete.html"
    success_url = reverse_lazy("stalls:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this stall has agreements, inspections, or violations.")
        else:
            messages.success(self.request, "Stall deleted.")
        return redirect(self.success_url)
