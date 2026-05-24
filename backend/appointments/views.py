from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Appointment, AppointmentStatusHistory
from .serializers import AppointmentSerializer, AppointmentStatusUpdateSerializer
from accounts.permissions import IsAdminOrReceptionist, IsAdminOrDoctor
from patients.models import Patient
from doctors.models import Doctor


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class   = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields   = ['status', 'appointment_type', 'doctor', 'patient']
    search_fields      = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name']
    ordering_fields    = ['appointment_date', 'appointment_time', 'status']

    def get_queryset(self):
        user = self.request.user
        qs   = Appointment.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__specialization'
        ).prefetch_related('status_history')

        if user.is_patient:
            return qs.filter(patient__user=user)
        if user.is_doctor:
            return qs.filter(doctor__user=user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_patient:
            patient = Patient.objects.get(user=user)
            serializer.save(patient=patient, created_by=user)
        else:
            serializer.save(created_by=user)


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class   = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs   = Appointment.objects.select_related(
            'patient__user', 'doctor__user'
        ).prefetch_related('status_history')
        if user.is_patient:
            return qs.filter(patient__user=user)
        if user.is_doctor:
            return qs.filter(doctor__user=user)
        return qs


class UpdateAppointmentStatusView(APIView):
    """Receptionist/Admin: confirm, cancel, or reschedule appointments"""
    permission_classes = [IsAdminOrReceptionist]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = appointment.status
        new_status = serializer.validated_data['status']

        appointment.status = new_status
        if 'appointment_date' in serializer.validated_data:
            appointment.appointment_date = serializer.validated_data['appointment_date']
        if 'appointment_time' in serializer.validated_data:
            appointment.appointment_time = serializer.validated_data['appointment_time']
        appointment.save()

        AppointmentStatusHistory.objects.create(
            appointment=appointment,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            reason=serializer.validated_data.get('reason', '')
        )

        return Response(AppointmentSerializer(appointment).data)


class DoctorCalendarView(generics.ListAPIView):
    """Doctor's appointment calendar"""
    serializer_class   = AppointmentSerializer
    permission_classes = [IsAdminOrDoctor]

    def get_queryset(self):
        user = self.request.user
        date = self.request.query_params.get('date')
        if user.is_doctor:
            qs = Appointment.objects.filter(doctor__user=user)
        else:
            doctor_id = self.request.query_params.get('doctor_id')
            qs = Appointment.objects.filter(doctor_id=doctor_id) if doctor_id else Appointment.objects.all()
        if date:
            qs = qs.filter(appointment_date=date)
        return qs.select_related('patient__user', 'doctor__user')


class TodayAppointmentsView(generics.ListAPIView):
    """All appointments for today"""
    serializer_class   = AppointmentSerializer
    permission_classes = [IsAdminOrReceptionist]

    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return Appointment.objects.filter(
            appointment_date=today
        ).select_related('patient__user', 'doctor__user')