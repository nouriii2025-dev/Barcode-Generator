from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from meters import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("scan/", views.scan_meter, name="scan_meter"),
    path("meters/new/", views.create_meter, name="create_meter"),
    path("meters/import/", views.import_csv, name="import_csv"),
    path("meters/<int:pk>/", views.meter_detail, name="meter_detail"),
    path("meters/<int:pk>/print/", views.print_label, name="print_label"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
