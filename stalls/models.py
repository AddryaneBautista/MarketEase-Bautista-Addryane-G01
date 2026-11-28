from django.db import models
from django.db.models import Q


class Stall(models.Model):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "UNDER_MAINTENANCE"
    STATUS_CHOICES = [
        (AVAILABLE, "Available"),
        (OCCUPIED, "Occupied"),
        (MAINTENANCE, "Under maintenance"),
    ]

    section = models.ForeignKey("sections.Section", on_delete=models.PROTECT, related_name="stalls")
    stall_type = models.ForeignKey("stall_types.StallType", on_delete=models.PROTECT, related_name="stalls")
    stall_number = models.CharField(max_length=20, unique=True)
    area_sqm = models.DecimalField(max_digits=6, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(area_sqm__gt=0), name="ck_stall_area_pos"),
            models.CheckConstraint(condition=Q(monthly_rate__gt=0), name="ck_stall_rate_pos"),
        ]

    def __str__(self):
        return self.stall_number
