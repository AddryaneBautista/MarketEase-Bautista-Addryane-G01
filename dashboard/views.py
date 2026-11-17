from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView
from accounts.models import CustomUser

# Create your views here.
Role = CustomUser.Role

class RoleDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    role = None

    def test_func(self):
        return self.request.user.role == self.role  # wrong role -> 403

    def get_template_names(self):
        return [f"dashboard/{self.role.lower()}.html"]


class AdminDashboardView(RoleDashboardView):
    role = Role.ADMIN


class StaffDashboardView(RoleDashboardView):
    role = Role.STAFF


class VendorDashboardView(RoleDashboardView):
    role = Role.VENDOR


class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse(f"dashboard_{self.request.user.role.lower()}")
