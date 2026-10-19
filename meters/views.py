import csv
import io
import uuid
import barcode
from barcode.writer import ImageWriter
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from .forms import MeterForm
from .models import Meter

def create_barcode(meter):
    # Barcode contains a unique system ID; meter data remains stored in the database.
    code = "MTR" + uuid.uuid4().hex[:16].upper()
    meter.barcode_id = code
    image_buffer = io.BytesIO()
    barcode.get("code128", code, writer=ImageWriter()).write(
        image_buffer, options={"module_height": 16, "font_size": 10, "text_distance": 3, "quiet_zone": 4}
    )
    meter.barcode_image.save(f"{code}.png", ContentFile(image_buffer.getvalue()), save=False)

def dashboard(request):
    query = request.GET.get("q", "").strip()
    meters = Meter.objects.all()
    if query:
        from django.db.models import Q
        meters = meters.filter(
            Q(serial_number__icontains=query) | Q(barcode_id__icontains=query) |
            Q(model_number__icontains=query) | Q(manufacturer_name__icontains=query)
        )
    page = Paginator(meters, 12).get_page(request.GET.get("page"))
    return render(request, "meters/dashboard.html", {"page": page, "query": query, "total": Meter.objects.count()})


def scan_meter(request):
    """Accept a Code 128 value from a handheld scanner or camera scan and find its record."""
    scanned_value = ""
    error = ""
    if request.method == "POST":
        scanned_value = request.POST.get("barcode_value", "").strip()
        if not scanned_value:
            error = "Scan a barcode or enter its ID first."
        else:
            try:
                meter = Meter.objects.get(barcode_id__iexact=scanned_value)
                return redirect("meter_detail", pk=meter.pk)
            except Meter.DoesNotExist:
                error = f"No meter record was found for barcode: {scanned_value}"
            except Meter.MultipleObjectsReturned:
                error = "More than one meter matches this barcode. Contact an administrator."
    return render(request, "meters/scan.html", {"scanned_value": scanned_value, "scan_error": error})


def create_meter(request):
    if request.method == "POST":
        form = MeterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    meter = form.save(commit=False)
                    create_barcode(meter)
                    meter.save()
                messages.success(request, f"Meter saved. Unique barcode: {meter.barcode_id}")
                return redirect("meter_detail", pk=meter.pk)
            except IntegrityError:
                form.add_error("serial_number", "This meter serial number already exists.")
    else:
        form = MeterForm()
    return render(request, "meters/meter_form.html", {"form": form})

def meter_detail(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    return render(request, "meters/meter_detail.html", {"meter": meter})


def print_label(request, pk):
    meter = get_object_or_404(Meter, pk=pk)
    return render(request, "meters/print_label.html", {"meter": meter})

def import_csv(request):
    if request.method == "POST":
        upload = request.FILES.get("file")
        if not upload or not upload.name.lower().endswith(".csv"):
            messages.error(request, "Please select a CSV file.")
            return redirect("import_csv")
        try:
            content = upload.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            required = [
                "serial_number", "size", "meter_type", "number_of_digits", "pre_decimal_digits",
                "decimal_digits", "multiplication_factor", "unit_of_measurement", "maximum_reading",
                "model_number", "date_of_manufacture", "manufacturer_name", "country_of_manufacture",
                "contract_reference", "storage_conditions"
            ]
            missing = [column for column in required if column not in (reader.fieldnames or [])]
            if missing:
                messages.error(request, "CSV is missing columns: " + ", ".join(missing))
                return redirect("import_csv")
            created, skipped = 0, 0
            for row in reader:
                try:
                    data = {key: row.get(key, "").strip() for key in required}
                    data["date_of_manufacture"] = parse_date(data["date_of_manufacture"])
                    if not data["date_of_manufacture"] or not data["serial_number"]:
                        skipped += 1
                        continue
                    with transaction.atomic():
                        meter = Meter(**data)
                        create_barcode(meter)
                        meter.save()
                    created += 1
                except Exception:
                    skipped += 1
            messages.success(request, f"Import complete: {created} created, {skipped} skipped. Check skipped rows for missing/invalid values or duplicate serial numbers.")
        except UnicodeDecodeError:
            messages.error(request, "Could not read the file. Save it as UTF-8 CSV and try again.")
        return redirect("dashboard")
    return render(request, "meters/import_csv.html")
