from django.contrib import admin
from .models import Stall


@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ("stall_number", "section", "stall_type", "monthly_rate", "status")
