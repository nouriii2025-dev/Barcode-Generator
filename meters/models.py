from django.db import models
from django.utils import timezone

class Meter(models.Model):
    barcode_id = models.CharField(max_length=40, unique=True, editable=False)
    serial_number = models.CharField("Meter serial number (MSN & ESN)", max_length=100, unique=True)
    size = models.CharField(max_length=50)
    meter_type = models.CharField("Type of meter", max_length=100)
    number_of_digits = models.PositiveSmallIntegerField()
    pre_decimal_digits = models.PositiveSmallIntegerField()
    decimal_digits = models.PositiveSmallIntegerField(default=6)
    multiplication_factor = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    unit_of_measurement = models.CharField(max_length=50, default="m³")
    maximum_reading = models.DecimalField(max_digits=18, decimal_places=4)
    model_number = models.CharField(max_length=100)
    date_of_manufacture = models.DateField()
    manufacturer_name = models.CharField(max_length=150)
    country_of_manufacture = models.CharField(max_length=100)
    contract_reference = models.CharField("EtihadWE contract reference number", max_length=100)
    storage_conditions = models.CharField(max_length=255)
    barcode_image = models.ImageField(upload_to="barcodes/", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.serial_number} ({self.barcode_id})"
