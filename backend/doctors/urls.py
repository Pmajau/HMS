from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.DoctorListCreateView.as_view(),       name='doctor_list'),
    path('available/',                              views.AvailableDoctorsView.as_view(),        name='available_doctors'),
    path('profile/',                                views.DoctorProfileView.as_view(),           name='doctor_profile'),
    path('specializations/',                        views.SpecializationListCreateView.as_view(), name='specializations'),
    path('<int:pk>/',                               views.DoctorDetailView.as_view(),            name='doctor_detail'),
    path('<int:doctor_id>/schedules/',              views.ScheduleListCreateView.as_view(),      name='doctor_schedules'),
    path('<int:doctor_id>/schedules/<int:pk>/',     views.ScheduleDetailView.as_view(),          name='schedule_detail'),
    path('<int:doctor_id>/patients/',               views.DoctorPatientAssignmentView.as_view(), name='doctor_patients'),
]