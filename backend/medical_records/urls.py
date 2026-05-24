from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.MedicalRecordListCreateView.as_view(),  name='medical_record_list'),
    path('<int:pk>/',                           views.MedicalRecordDetailView.as_view(),       name='medical_record_detail'),
    path('my-records/',                         views.PatientOwnRecordsView.as_view(),         name='my_records'),
    path('patient/<int:patient_id>/',           views.PatientMedicalHistoryView.as_view(),     name='patient_history'),
    path('patient/<int:patient_id>/export/',    views.ExportMedicalHistoryView.as_view(),      name='export_history'),
    path('<int:record_id>/prescriptions/',      views.PrescriptionListCreateView.as_view(),    name='prescriptions'),
    path('<int:record_id>/lab-tests/',          views.LabTestListCreateView.as_view(),         name='lab_tests'),
    path('lab-tests/<int:pk>/',                 views.LabTestUpdateView.as_view(),             name='lab_test_detail'),
]