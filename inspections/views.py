from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import CustomUser
from .forms import InspectionForm
from .models import Inspection

Role = CustomUser.Role
MANAGER_ROLES = (Role.ADMIN, Role.STAFF)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in MANAGER_ROLES


class InspectionListView(StaffRequiredMixin, ListView):
    template_name = "inspections/inspection_list.html"
    context_object_name = "inspections"
    paginate_by = 10

    def get_queryset(self):
        qs = Inspection.objects.select_related("stall__section", "inspector")
        q = self.request.GET.get("q", "").strip()
        result = self.request.GET.get("result", "")
        if q:
            qs = qs.filter(Q(stall__stall_number__icontains=q) | Q(inspector__username__icontains=q)
                           | Q(findings__icontains=q))
        if result:
            qs = qs.filter(result=result)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["results"] = Inspection.RESULT_CHOICES
        return ctx


class InspectionCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Inspection
    form_class = InspectionForm
    template_name = "inspections/inspection_form.html"
    success_url = reverse_lazy("inspections:list")
    success_message = "Inspection recorded."

    def form_valid(self, form):
        form.instance.inspector = self.request.user
        return super().form_valid(form)


class InspectionUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Inspection
    form_class = InspectionForm
    template_name = "inspections/inspection_form.html"
    success_url = reverse_lazy("inspections:list")
    success_message = "Inspection updated."


class InspectionDeleteView(StaffRequiredMixin, DeleteView):
    model = Inspection
    template_name = "inspections/inspection_confirm_delete.html"
    success_url = reverse_lazy("inspections:list")

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, "Cannot delete: violations reference this inspection.")
        else:
            messages.success(self.request, "Inspection deleted.")
        return redirect(self.success_url)
