from django import forms
from .models import Meter

class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        exclude = ["barcode_id", "barcode_image", "created_at"]
        widgets = {
            "date_of_manufacture": forms.DateInput(attrs={"type": "date"}),
            "storage_conditions": forms.TextInput(attrs={"placeholder": "e.g. Store indoors, dry conditions"}),
        }

    def clean(self):
        cleaned = super().clean()
        total = cleaned.get("number_of_digits")
        pre = cleaned.get("pre_decimal_digits")
        decimal = cleaned.get("decimal_digits")
        if total is not None and pre is not None and pre > total:
            self.add_error("pre_decimal_digits", "Pre-decimal digits cannot exceed total number of digits.")
        if total is not None and decimal is not None and decimal > total:
            self.add_error("decimal_digits", "Decimal digits cannot exceed total number of digits.")
        if total is not None and pre is not None and decimal is not None and pre + decimal > total:
            self.add_error("decimal_digits", "Pre-decimal plus decimal digits cannot exceed total digits.")
        return cleaned
