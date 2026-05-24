from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.PatientListCreateView.as_view(),    name='patient_list'),
    path('<int:pk>/',                               views.PatientDetailView.as_view(),        name='patient_detail'),
    path('portal/',                                 views.PatientPortalView.as_view(),        name='patient_portal'),
    path('<int:patient_id>/emergency-contacts/',    views.EmergencyContactView.as_view(),     name='emergency_contacts'),
    path('<int:patient_id>/emergency-contacts/<int:pk>/', views.EmergencyContactDetailView.as_view(), name='emergency_contact_detail'),
    path('<int:patient_id>/admit/',                 views.AdmitPatientView.as_view(),         name='admit_patient'),
    path('<int:patient_id>/discharge/',             views.DischargePatientView.as_view(),     name='discharge_patient'),
    path('<int:patient_id>/admissions/',            views.AdmissionHistoryView.as_view(),     name='admission_history'),
]