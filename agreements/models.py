from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Q
from django.utils import timezone

from stalls.models import Stall


class Agreement(models.Model):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    STATUS_CHOICES = [(ACTIVE, "Active"), (EXPIRED, "Expired"), (TERMINATED, "Terminated")]

    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.PROTECT, related_name="agreements")
    stall = models.ForeignKey("stalls.Stall", on_delete=models.PROTECT, related_name="agreements")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name="created_agreements",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(end_date__gt=F("start_date")), name="ck_agr_dates"),
            models.CheckConstraint(condition=Q(monthly_rate__gt=0), name="ck_agr_rate_pos"),
            models.UniqueConstraint(
                fields=["stall"], condition=Q(status="ACTIVE"), name="uq_one_active_per_stall",
            ),
        ]

    def __str__(self):
        return f"Agreement #{self.pk}: {self.vendor} - {self.stall}"

    @classmethod
    def expire_past_due(cls, today=None):
        today = today or timezone.localdate()
        with transaction.atomic():
            qs = cls.objects.filter(status=cls.ACTIVE, end_date__lt=today)
            stall_ids = list(qs.values_list("stall_id", flat=True))
            count = qs.update(status=cls.EXPIRED)
            Stall.objects.filter(pk__in=stall_ids, status=Stall.OCCUPIED).update(status=Stall.AVAILABLE)
        return count
