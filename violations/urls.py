from django.urls import path
from . import views

app_name = "violations"

urlpatterns = [
    path("", views.ViolationListView.as_view(), name="list"),
    path("new/", views.ViolationCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.ViolationUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ViolationDeleteView.as_view(), name="delete"),
]
