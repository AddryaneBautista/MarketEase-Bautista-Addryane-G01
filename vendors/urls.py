from django.urls import path
from . import views

app_name = "vendors"

urlpatterns = [
    path("", views.VendorListView.as_view(), name="list"),
    path("new/", views.VendorCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.VendorUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.VendorDeleteView.as_view(), name="delete"),
]
