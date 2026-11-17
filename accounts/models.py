from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        STAFF = "STAFF", "Staff"
        VENDOR = "VENDOR", "Vendor"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VENDOR)

    def __str__(self):
        return self.username
