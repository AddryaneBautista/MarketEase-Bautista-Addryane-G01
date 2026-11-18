from django.urls import path
from . import views

app_name = "agreements"

urlpatterns = [
    path("", views.AgreementListView.as_view(), name="list"),
    path("new/", views.AgreementCreateView.as_view(), name="create"),
    path("<int:pk>/", views.AgreementDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.AgreementUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.AgreementDeleteView.as_view(), name="delete"),
]
