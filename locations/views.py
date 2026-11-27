from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from agreements.models import Location
from .forms import LocationForm

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class LocationListView(StaffRequiredMixin, ListView):
    template_name = "locations/location_list.html"
    context_object_name = "locations"
    paginate_by = 10

    def get_queryset(self):
        qs = Location.objects.annotate(section_count=Count("sections")).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs


class LocationCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    success_url = reverse_lazy("locations:list")
    success_message = "Location created."


class LocationUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "locations/location_form.html"
    success_url = reverse_lazy("locations:list")
    success_message = "Location updated."


class LocationDeleteView(StaffRequiredMixin, DeleteView):
    model = Location
    template_name = "locations/location_confirm_delete.html"
    success_url = reverse_lazy("locations:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: this location still has sections.")
        else:
            messages.success(self.request, "Location deleted.")
        return redirect(self.success_url)
