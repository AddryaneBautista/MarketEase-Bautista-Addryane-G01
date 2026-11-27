from django.urls import path
from . import views

app_name = "stalls"

urlpatterns = [
    path("", views.StallListView.as_view(), name="list"),
    path("new/", views.StallCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.StallUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.StallDeleteView.as_view(), name="delete"),
]
