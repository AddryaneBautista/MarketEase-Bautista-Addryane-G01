from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from locations.models import Location
from .forms import SectionForm
from .models import Section

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class SectionListView(StaffRequiredMixin, ListView):
    template_name = "sections/section_list.html"
    context_object_name = "sections"
    paginate_by = 10

    def get_queryset(self):
        qs = (Section.objects.select_related("location")
              .annotate(stall_count=Count("stalls"))
              .order_by("location__name", "name"))
        q = self.request.GET.get("q", "").strip()
        location = self.request.GET.get("location", "")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(location__name__icontains=q))
        if location.isdigit():
            qs = qs.filter(location_id=location)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["locations"] = Location.objects.order_by("name")
        return ctx


class SectionCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Section
    form_class = SectionForm
    template_name = "sections/section_form.html"
    success_url = reverse_lazy("sections:list")
    success_message = "Section created."


class SectionUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Section
    form_class = SectionForm
    template_name = "sections/section_form.html"
    success_url = reverse_lazy("sections:list")
    success_message = "Section updated."


class SectionDeleteView(StaffRequiredMixin, DeleteView):
    model = Section
    template_name = "sections/section_confirm_delete.html"
    success_url = reverse_lazy("sections:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this section still has stalls.")
        else:
            messages.success(self.request, "Section deleted.")
        return redirect(self.success_url)
