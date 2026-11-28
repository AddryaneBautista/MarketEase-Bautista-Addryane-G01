from django.urls import path
from . import views

app_name = "stall_types"

urlpatterns = [
    path("", views.StallTypeListView.as_view(), name="list"),
    path("new/", views.StallTypeCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.StallTypeUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.StallTypeDeleteView.as_view(), name="delete"),
]
