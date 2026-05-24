from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.http import HttpResponse
from .models import MedicalRecord, Prescription, LabTest
from .serializers import MedicalRecordSerializer, PrescriptionSerializer, LabTestSerializer
from accounts.permissions import IsAdminOrDoctor, IsMedicalStaff


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class   = MedicalRecordSerializer
    permission_classes = [IsMedicalStaff]
    filterset_fields   = ['patient', 'doctor']
    search_fields      = ['patient__user__first_name', 'diagnosis']
    ordering_fields    = ['visit_date']

    def get_queryset(self):
        user = self.request.user
        qs   = MedicalRecord.objects.select_related(
            'patient__user', 'doctor__user'
        ).prefetch_related('prescriptions', 'lab_tests')
        if user.is_doctor:
            return qs.filter(doctor__user=user)
        return qs

    def perform_create(self, serializer):
        from doctors.models import Doctor
        doctor = Doctor.objects.get(user=self.request.user)
        serializer.save(doctor=doctor)


class MedicalRecordDetailView(generics.RetrieveUpdateAPIView):
    serializer_class   = MedicalRecordSerializer
    permission_classes = [IsMedicalStaff]

    def get_queryset(self):
        user = self.request.user
        qs   = MedicalRecord.objects.select_related('patient__user', 'doctor__user')
        if user.is_doctor:
            return qs.filter(doctor__user=user)
        return qs


class PatientMedicalHistoryView(generics.ListAPIView):
    """Full medical history for a specific patient"""
    serializer_class   = MedicalRecordSerializer
    permission_classes = [IsAdminOrDoctor]

    def get_queryset(self):
        return MedicalRecord.objects.filter(
            patient_id=self.kwargs['patient_id']
        ).select_related('doctor__user').prefetch_related('prescriptions', 'lab_tests')


class PatientOwnRecordsView(generics.ListAPIView):
    """Patients viewing their own medical records"""
    serializer_class   = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MedicalRecord.objects.filter(
            patient__user=self.request.user
        ).select_related('doctor__user').prefetch_related('prescriptions', 'lab_tests')


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class   = PrescriptionSerializer
    permission_classes = [IsMedicalStaff]

    def get_queryset(self):
        return Prescription.objects.filter(medical_record_id=self.kwargs['record_id'])

    def perform_create(self, serializer):
        record = MedicalRecord.objects.get(id=self.kwargs['record_id'])
        serializer.save(medical_record=record)


class LabTestListCreateView(generics.ListCreateAPIView):
    serializer_class   = LabTestSerializer
    permission_classes = [IsMedicalStaff]

    def get_queryset(self):
        return LabTest.objects.filter(medical_record_id=self.kwargs['record_id'])

    def perform_create(self, serializer):
        record = MedicalRecord.objects.get(id=self.kwargs['record_id'])
        serializer.save(medical_record=record, ordered_by=self.request.user)


class LabTestUpdateView(generics.RetrieveUpdateAPIView):
    """Update lab test results"""
    serializer_class   = LabTestSerializer
    permission_classes = [IsMedicalStaff]
    queryset           = LabTest.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'completed' and not instance.completed_at:
            instance.completed_at = timezone.now()
            instance.save()


class ExportMedicalHistoryView(APIView):
    """Export patient medical history as plain text (PDF library optional)"""
    permission_classes = [IsAdminOrDoctor]

    def get(self, request, patient_id):
        records = MedicalRecord.objects.filter(
            patient_id=patient_id
        ).select_related('doctor__user', 'patient__user').prefetch_related('prescriptions', 'lab_tests')

        if not records.exists():
            return Response({'error': 'No records found'}, status=status.HTTP_404_NOT_FOUND)

        patient = records.first().patient
        lines   = [
            f"MEDICAL HISTORY REPORT",
            f"Patient: {patient.user.get_full_name()}",
            f"Patient No: {patient.patient_number}",
            f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            f"{'='*50}",
        ]

        for record in records:
            lines += [
                f"\nVisit Date: {record.visit_date}",
                f"Doctor: Dr. {record.doctor.user.get_full_name()}",
                f"Symptoms: {record.symptoms}",
                f"Diagnosis: {record.diagnosis}",
                f"Treatment: {record.treatment}",
            ]
            if record.prescriptions.exists():
                lines.append("Prescriptions:")
                for p in record.prescriptions.all():
                    lines.append(f"  - {p.medication} | {p.dosage} | {p.frequency} | {p.duration_days} days")
            if record.lab_tests.exists():
                lines.append("Lab Tests:")
                for t in record.lab_tests.all():
                    lines.append(f"  - {t.test_name}: {t.status}")
            lines.append("-"*50)

        content  = "\n".join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="medical_history_{patient.patient_number}.txt"'
        return response