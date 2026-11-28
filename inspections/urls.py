from django.urls import path
from . import views

app_name = "inspections"

urlpatterns = [
    path("", views.InspectionListView.as_view(), name="list"),
    path("new/", views.InspectionCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.InspectionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.InspectionDeleteView.as_view(), name="delete"),
]
