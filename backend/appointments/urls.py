from django.urls import path
from . import views

urlpatterns = [
    path('',            views.AppointmentListCreateView.as_view(),   name='appointment_list'),
    path('<int:pk>/',   views.AppointmentDetailView.as_view(),       name='appointment_detail'),
    path('<int:pk>/status/', views.UpdateAppointmentStatusView.as_view(), name='update_status'),
    path('calendar/',   views.DoctorCalendarView.as_view(),          name='doctor_calendar'),
    path('today/',      views.TodayAppointmentsView.as_view(),       name='today_appointments'),
]