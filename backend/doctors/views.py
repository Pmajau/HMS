from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Doctor, Specialization, Schedule, DoctorPatientAssignment
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, SpecializationSerializer,
    ScheduleSerializer, DoctorPatientAssignmentSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrDoctor, IsAdminOrReceptionist


class SpecializationListCreateView(generics.ListCreateAPIView):
    queryset           = Specialization.objects.all()
    serializer_class   = SpecializationSerializer
    permission_classes = [IsAdmin]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]


class DoctorListCreateView(generics.ListCreateAPIView):
    queryset           = Doctor.objects.select_related('user', 'specialization').prefetch_related('schedules')
    permission_classes = [IsAdminOrReceptionist]
    filterset_fields   = ['specialization', 'is_available']
    search_fields      = ['user__first_name', 'user__last_name', 'doctor_number']
    ordering_fields    = ['user__first_name', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DoctorCreateSerializer
        return DoctorSerializer

    def create(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        return Response(DoctorSerializer(doctor).data, status=status.HTTP_201_CREATED)


class DoctorDetailView(generics.RetrieveUpdateAPIView):
    queryset           = Doctor.objects.select_related('user', 'specialization')
    serializer_class   = DoctorSerializer
    permission_classes = [IsAdminOrReceptionist]


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    """Doctors can view and update their own profile"""
    serializer_class   = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Doctor.objects.get(user=self.request.user)


class ScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class   = ScheduleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Schedule.objects.filter(doctor_id=self.kwargs['doctor_id'])

    def perform_create(self, serializer):
        doctor = Doctor.objects.get(id=self.kwargs['doctor_id'])
        serializer.save(doctor=doctor)


class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ScheduleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Schedule.objects.filter(doctor_id=self.kwargs['doctor_id'])


class DoctorPatientAssignmentView(generics.ListCreateAPIView):
    serializer_class   = DoctorPatientAssignmentSerializer
    permission_classes = [IsAdminOrDoctor]

    def get_queryset(self):
        return DoctorPatientAssignment.objects.filter(
            doctor_id=self.kwargs['doctor_id'], is_active=True
        )

    def perform_create(self, serializer):
        doctor = Doctor.objects.get(id=self.kwargs['doctor_id'])
        serializer.save(doctor=doctor)


class AvailableDoctorsView(generics.ListAPIView):
    """List all available doctors — accessible to all authenticated users"""
    serializer_class   = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        specialization_id = self.request.query_params.get('specialization')
        qs = Doctor.objects.filter(is_available=True).select_related('user', 'specialization')
        if specialization_id:
            qs = qs.filter(specialization_id=specialization_id)
        return qs