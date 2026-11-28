from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import AdminUserCreateForm, AdminUserUpdateForm, CustomUserCreationForm
from .models import CustomUser

Role = CustomUser.Role


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == Role.ADMIN


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
    success_message = "Account created. Please log in."


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    fields = ("first_name", "last_name", "email")
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")
    success_message = "Profile updated."

    def get_object(self):
        return self.request.user


class UserListView(AdminRequiredMixin, ListView):
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 10

    def get_queryset(self):
        qs = CustomUser.objects.select_related("vendor").order_by("username")
        g = self.request.GET
        q = g.get("q", "").strip()
        if q:
            qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q)
                           | Q(last_name__icontains=q) | Q(email__icontains=q))
        if g.get("role") in Role.values:
            qs = qs.filter(role=g["role"])
        if g.get("active") in ("1", "0"):
            qs = qs.filter(is_active=g["active"] == "1")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = Role.choices
        return ctx


class UserCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = CustomUser
    form_class = AdminUserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")
    success_message = "User account created."


class UserUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = AdminUserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")
    success_message = "User account updated."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["acting_user"] = self.request.user
        return kwargs
