from django.contrib import admin
from .models import Meter

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "barcode_id", "size", "meter_type", "manufacturer_name", "created_at")
    search_fields = ("serial_number", "barcode_id", "model_number", "manufacturer_name", "contract_reference")
    list_filter = ("meter_type", "size", "country_of_manufacture")
    readonly_fields = ("barcode_id", "barcode_image", "created_at")
