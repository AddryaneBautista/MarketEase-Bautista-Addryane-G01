from django.conf import settings
from django.db import models


class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="vendor",
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    business_name = models.CharField(max_length=150, blank=True)
    contact_number = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
