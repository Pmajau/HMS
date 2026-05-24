from rest_framework import serializers
from .models import MedicalRecord, Prescription, LabTest


class PrescriptionSerializer(serializers.ModelSerializer):
    medication_name = serializers.CharField(source='medication.name', read_only=True)

    class Meta:
        model  = Prescription
        fields = '__all__'
        read_only_fields = ['medical_record']


class LabTestSerializer(serializers.ModelSerializer):
    ordered_by_name = serializers.CharField(source='ordered_by.get_full_name', read_only=True)

    class Meta:
        model  = LabTest
        fields = '__all__'
        read_only_fields = ['medical_record', 'ordered_by', 'ordered_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name  = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name   = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_tests     = LabTestSerializer(many=True, read_only=True)

    class Meta:
        model  = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'appointment', 'visit_date', 'symptoms', 'diagnosis',
            'treatment', 'notes', 'follow_up_date',
            'prescriptions', 'lab_tests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['visit_date', 'created_at', 'updated_at']