from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Patient, EmergencyContact, Admission
from .serializers import (
    PatientSerializer, PatientCreateSerializer,
    EmergencyContactSerializer, AdmissionSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrDoctor, IsAdminOrReceptionist


class PatientListCreateView(generics.ListCreateAPIView):
    """List all patients or register a new one"""
    queryset         = Patient.objects.select_related('user').prefetch_related('emergency_contacts')
    permission_classes = [IsAdminOrReceptionist]
    filterset_fields = ['gender', 'blood_group']
    search_fields    = ['user__first_name', 'user__last_name', 'user__email', 'patient_number']
    ordering_fields  = ['created_at', 'user__first_name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        serializer = PatientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        return Response(
            PatientSerializer(patient).data,
            status=status.HTTP_201_CREATED
        )


class PatientDetailView(generics.RetrieveUpdateAPIView):
    """Get or update a specific patient"""
    queryset           = Patient.objects.select_related('user').prefetch_related('emergency_contacts')
    serializer_class   = PatientSerializer
    permission_classes = [IsAdminOrDoctor]


class PatientPortalView(generics.RetrieveAPIView):
    """Patients can view their own profile"""
    serializer_class   = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Patient.objects.get(user=self.request.user)


class EmergencyContactView(generics.ListCreateAPIView):
    """List or add emergency contacts for a patient"""
    serializer_class   = EmergencyContactSerializer
    permission_classes = [IsAdminOrReceptionist]

    def get_queryset(self):
        return EmergencyContact.objects.filter(patient_id=self.kwargs['patient_id'])

    def perform_create(self, serializer):
        patient = Patient.objects.get(id=self.kwargs['patient_id'])
        serializer.save(patient=patient)


class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = EmergencyContactSerializer
    permission_classes = [IsAdminOrReceptionist]

    def get_queryset(self):
        return EmergencyContact.objects.filter(patient_id=self.kwargs['patient_id'])


class AdmitPatientView(generics.CreateAPIView):
    """Admit a patient"""
    serializer_class   = AdmissionSerializer
    permission_classes = [IsAdminOrReceptionist]

    def perform_create(self, serializer):
        patient = Patient.objects.get(id=self.kwargs['patient_id'])
        serializer.save(patient=patient, admitted_by=self.request.user)


class DischargePatientView(APIView):
    """Discharge an admitted patient"""
    permission_classes = [IsAdminOrReceptionist]

    def post(self, request, patient_id):
        try:
            admission = Admission.objects.filter(
                patient_id=patient_id, status='admitted'
            ).latest('admission_date')
            admission.status         = 'discharged'
            admission.discharge_date = timezone.now()
            admission.discharge_notes = request.data.get('discharge_notes', '')
            admission.save()
            return Response(AdmissionSerializer(admission).data)
        except Admission.DoesNotExist:
            return Response(
                {'error': 'No active admission found for this patient'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdmissionHistoryView(generics.ListAPIView):
    """View admission history for a patient"""
    serializer_class   = AdmissionSerializer
    permission_classes = [IsAdminOrDoctor]

    def get_queryset(self):
        return Admission.objects.filter(patient_id=self.kwargs['patient_id'])