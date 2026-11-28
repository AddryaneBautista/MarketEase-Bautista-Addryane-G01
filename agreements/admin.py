from django.contrib import admin
from .models import Agreement


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "stall", "start_date", "end_date", "status")
