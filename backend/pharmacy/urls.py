from django.urls import path
from . import views

urlpatterns = [
    path('medications/',                        views.MedicationListCreateView.as_view(),   name='medication_list'),
    path('medications/<int:pk>/',               views.MedicationDetailView.as_view(),       name='medication_detail'),
    path('medications/<int:pk>/stock/',         views.UpdateStockView.as_view(),            name='update_stock'),
    path('medications/low-stock/',              views.LowStockAlertsView.as_view(),         name='low_stock'),
    path('dispensing/',                         views.DispensingRecordListView.as_view(),   name='dispensing_records'),
    path('dispense/<int:prescription_id>/',     views.DispensePrescriptionView.as_view(),   name='dispense'),
]