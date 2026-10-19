from django.test import TestCase
from django.urls import reverse

from .models import Meter


class BarcodeScanningTests(TestCase):
    def setUp(self):
        self.meter = Meter.objects.create(
            barcode_id="MTR8A72F19C4D6E2A",
            serial_number="SERIAL-TEST-1",
            size="DN 20",
            meter_type="Water",
            number_of_digits=8,
            pre_decimal_digits=5,
            decimal_digits=3,
            multiplication_factor=1,
            unit_of_measurement="m³",
            maximum_reading=99999,
            model_number="MODEL-1",
            date_of_manufacture="2024-01-15",
            manufacturer_name="Meter Manufacturer",
            country_of_manufacture="UAE",
            contract_reference="CONTRACT-1",
            storage_conditions="Store dry",
        )

    def test_handheld_post_redirects_to_matching_meter(self):
        response = self.client.post(
            reverse("scan_meter"),
            {"barcode_value": f"  {self.meter.barcode_id.lower()}  "},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            reverse("meter_detail", kwargs={"pk": self.meter.pk}),
        )

    def test_unknown_barcode_displays_error(self):
        response = self.client.post(
            reverse("scan_meter"),
            {"barcode_value": "MTR-UNKNOWN"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No meter record was found")

    def test_empty_barcode_displays_error(self):
        response = self.client.post(reverse("scan_meter"), {"barcode_value": "  "})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scan a barcode or enter its ID first.")

    def test_camera_scanner_uses_one_dimensional_zxing_reader(self):
        response = self.client.get(reverse("scan_meter"))
        self.assertContains(response, "@zxing/browser@0.2.1")
        self.assertContains(response, "BrowserMultiFormatOneDReader")
        self.assertContains(response, "HTTPS")
        self.assertNotContains(response, "BrowserQRCodeReader")
