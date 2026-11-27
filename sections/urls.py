from django.urls import path
from . import views

app_name = "sections"

urlpatterns = [
    path("", views.SectionListView.as_view(), name="list"),
    path("new/", views.SectionCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.SectionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.SectionDeleteView.as_view(), name="delete"),
]
