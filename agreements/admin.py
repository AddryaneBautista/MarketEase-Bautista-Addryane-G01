from django.contrib import admin
from .models import Location, Section, StallType, Stall, Vendor, RentalAgreement

# Register your models here.
@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ("stall_number", "section", "stall_type", "monthly_rate", "status")

@admin.register(RentalAgreement)
class RentalAgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "stall", "start_date", "end_date", "status")

admin.site.register(Location)
admin.site.register(Section)
admin.site.register(StallType)
admin.site.register(Vendor)
