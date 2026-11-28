from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Q
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="sections")
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["location", "name"], name="uq_section_location_name"),
        ]

    def __str__(self):
        return f"{self.location} - {self.name}"


class StallType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Stall(models.Model):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "UNDER_MAINTENANCE"
    STATUS_CHOICES = [
        (AVAILABLE, "Available"),
        (OCCUPIED, "Occupied"),
        (MAINTENANCE, "Under maintenance"),
    ]

    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="stalls")
    stall_type = models.ForeignKey(StallType, on_delete=models.PROTECT, related_name="stalls")
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


class RentalAgreement(models.Model):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    STATUS_CHOICES = [(ACTIVE, "Active"), (EXPIRED, "Expired"), (TERMINATED, "Terminated")]

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="agreements")
    stall = models.ForeignKey(Stall, on_delete=models.PROTECT, related_name="agreements")
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

    @classmethod
    def expire_past_due(cls, today=None):
        today = today or timezone.localdate()
        with transaction.atomic():
            qs = cls.objects.filter(status=cls.ACTIVE, end_date__lt=today)
            stall_ids = list(qs.values_list("stall_id", flat=True))
            count = qs.update(status=cls.EXPIRED)
            Stall.objects.filter(pk__in=stall_ids, status=Stall.OCCUPIED).update(status=Stall.AVAILABLE)
        return count

    def __str__(self):
        return f"Agreement #{self.pk}: {self.vendor} - {self.stall}"
