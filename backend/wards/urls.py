from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.WardListCreateView.as_view(),         name='ward_list'),
    path('occupancy/',                              views.WardOccupancyView.as_view(),           name='ward_occupancy'),
    path('<int:pk>/',                               views.WardDetailView.as_view(),              name='ward_detail'),
    path('<int:ward_id>/beds/',                     views.BedListCreateView.as_view(),           name='bed_list'),
    path('beds/<int:bed_id>/assign/',               views.AssignBedView.as_view(),               name='assign_bed'),
    path('beds/<int:bed_id>/release/',              views.ReleaseBedView.as_view(),              name='release_bed'),
    path('patients/<int:patient_id>/history/',      views.BedAssignmentHistoryView.as_view(),    name='bed_history'),
]