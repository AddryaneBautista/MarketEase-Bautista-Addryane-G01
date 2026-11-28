from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportIndexView.as_view(), name="index"),
    path("occupancy/", views.OccupancyReportView.as_view(), name="occupancy"),
    path("payments/", views.PaymentReportView.as_view(), name="payments"),
    path("inspections/", views.InspectionViolationReportView.as_view(), name="inspections"),
]
