from django.urls import path
from . import views

urlpatterns = [
    path("", views.DashboardRedirectView.as_view(), name="dashboard"),
    path("dashboard/admin/", views.AdminDashboardView.as_view(), name="dashboard_admin"),
    path("dashboard/staff/", views.StaffDashboardView.as_view(), name="dashboard_staff"),
    path("dashboard/vendor/", views.VendorDashboardView.as_view(), name="dashboard_vendor"),
]
