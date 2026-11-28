from django.db import models
from django.db.models import Q
from django.utils import timezone


class Violation(models.Model):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    STATUS_CHOICES = [(OPEN, "Open"), (RESOLVED, "Resolved")]

    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.PROTECT, related_name="violations")
    stall = models.ForeignKey("stalls.Stall", on_delete=models.PROTECT, related_name="violations")
    inspection = models.ForeignKey("inspections.Inspection", null=True, blank=True,
                                   on_delete=models.PROTECT, related_name="violations")
    description = models.CharField(max_length=255)
    violation_date = models.DateField(default=timezone.localdate)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)

    class Meta:
        ordering = ["-violation_date", "-pk"]
        constraints = [
            models.CheckConstraint(condition=Q(fine_amount__gte=0), name="ck_viol_fine_nonneg"),
            models.CheckConstraint(condition=Q(status__in=["OPEN", "RESOLVED"]), name="ck_viol_status"),
        ]

    def __str__(self):
        return f"Violation #{self.pk} - {self.vendor} ({self.stall})"
