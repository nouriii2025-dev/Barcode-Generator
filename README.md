# MeterFlow — Meter Barcode Management

A Django starter application for registering water-meter information, generating unique Code 128 barcodes, importing records from CSV, searching saved meters, and printing labels.

## Requirements
- Python 3.10+
- pip

## Run on Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py makemigrations meters
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Open http://127.0.0.1:8000/

## Features
- Manual meter entry with validation
- Unique barcode ID generated for each saved meter
- Code 128 barcode image generation
- Dashboard, search, pagination, meter detail view
- Print-friendly label page
- CSV bulk import
- Django admin for internal record management

## CSV import format
The first row must use these exact column names:

`serial_number, size, meter_type, number_of_digits, pre_decimal_digits, decimal_digits, multiplication_factor, unit_of_measurement, maximum_reading, model_number, date_of_manufacture, manufacturer_name, country_of_manufacture, contract_reference, storage_conditions`

Use ISO date format `YYYY-MM-DD`. Duplicate serial numbers and invalid rows are skipped and reported in the success message count.

## Important production notes
- Replace `SECRET_KEY`, set `DEBUG = False`, and configure `ALLOWED_HOSTS`.
- Add authentication and permissions before exposing the system to a network.
- Configure a persistent media directory and database backups.
- Confirm the required label dimensions, barcode symbology, data encoding, and durability with the barcode scanner/label supplier.
- The barcode encodes a unique system ID, not all meter fields. The ID maps to the full saved record in the dashboard.


## Scanning and automatic record retrieval

Open `/scan/` from the navigation menu.

- **Handheld USB/Bluetooth scanner:** click the Barcode ID field, scan the Code 128 label, and submit the value. Most scanners type the scanned value like a keyboard; configure the scanner's suffix as Enter if available.
- **Phone camera:** open `/scan/` in a supported mobile browser, select **Start camera scanner**, grant camera permission, and point it at the Code 128 barcode. A successful scan submits the ID and redirects to the saved meter details.
- The barcode carries the unique `barcode_id`; Django uses it to retrieve the full record. All 15 fields do not need to be encoded in the bars themselves.

### Office network and phone camera requirements

1. Run Django on the office host with a LAN-accessible server configuration, firewall rules, and a stable internal hostname/IP. `runserver` is for development/testing only.
2. For camera scanning from a phone, browsers normally require a secure context (HTTPS) for camera access. Configure HTTPS on the internal hostname using your IT team's certificate/reverse proxy, then open the HTTPS URL from the phone. Plain HTTP on a LAN IP usually will not permit camera access.
3. Keep the database and media folder on persistent storage and back them up. Restrict the application to authorized users before production deployment.
4. The phone and office host must be able to communicate over the company network. Do not expose the app to the public internet unless approved and secured.

The browser camera library is loaded from the `@zxing/browser` CDN; an internet connection may be needed for that script unless your IT team hosts a reviewed copy internally.
