from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Payment(models.Model):
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    OVERDUE = "OVERDUE"
    STATUS_CHOICES = [(PAID, "Paid"), (PARTIAL, "Partial"), (OVERDUE, "Overdue")]

    rental_agreement = models.ForeignKey(
        "agreements.RentalAgreement", on_delete=models.PROTECT, related_name="payments",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="received_payments",
    )
    billing_month = models.DateField()
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PARTIAL)

    class Meta:
        ordering = ["-billing_month", "-pk"]
        constraints = [
            models.UniqueConstraint(fields=["rental_agreement", "billing_month"],
                                    name="uq_payment_agreement_month"),
            models.CheckConstraint(condition=Q(amount_due__gt=0), name="ck_pay_due_pos"),
            models.CheckConstraint(condition=Q(amount_paid__gte=0), name="ck_pay_paid_nonneg"),
            models.CheckConstraint(condition=Q(status__in=["PAID", "PARTIAL", "OVERDUE"]),
                                   name="ck_pay_status"),
        ]

    def __str__(self):
        return f"Payment #{self.pk} - {self.rental_agreement} ({self.billing_month:%b %Y})"

    def compute_status(self, today=None):
        today = today or timezone.localdate()
        if self.amount_paid >= self.amount_due:
            return self.PAID
        if self.due_date < today:
            return self.OVERDUE
        return self.PARTIAL

    def save(self, *args, **kwargs):
        self.status = self.compute_status()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"status"}
        super().save(*args, **kwargs)

    @classmethod
    def refresh_overdue(cls, today=None):
        today = today or timezone.localdate()
        return cls.objects.filter(status=cls.PARTIAL, due_date__lt=today).update(status=cls.OVERDUE)
