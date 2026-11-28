from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Inspection(models.Model):
    PASSED = "PASSED"
    FAILED = "FAILED"
    FOLLOW_UP = "NEEDS_FOLLOW_UP"
    RESULT_CHOICES = [(PASSED, "Passed"), (FAILED, "Failed"), (FOLLOW_UP, "Needs follow-up")]

    stall = models.ForeignKey("agreements.Stall", on_delete=models.PROTECT, related_name="inspections")
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                  related_name="inspections_conducted")
    inspection_date = models.DateField(default=timezone.localdate)
    findings = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)

    class Meta:
        ordering = ["-inspection_date", "-pk"]
        constraints = [
            models.CheckConstraint(condition=Q(result__in=["PASSED", "FAILED", "NEEDS_FOLLOW_UP"]),
                                   name="ck_insp_result"),
        ]

    def __str__(self):
        return f"Inspection #{self.pk} - {self.stall} ({self.inspection_date})"
