from rest_framework import serializers
from .models import Medication, DispensingRecord


class MedicationSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Medication
        fields = [
            'id', 'name', 'generic_name', 'category', 'description',
            'unit', 'unit_price', 'stock_quantity', 'reorder_level',
            'is_low_stock', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StockUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    notes    = serializers.CharField(required=False, allow_blank=True)


class DispensingRecordSerializer(serializers.ModelSerializer):
    medication_name  = serializers.CharField(source='medication.name', read_only=True)
    dispensed_by_name = serializers.CharField(source='dispensed_by.get_full_name', read_only=True)
    patient_name     = serializers.CharField(source='prescription.medical_record.patient.user.get_full_name', read_only=True)

    class Meta:
        model  = DispensingRecord
        fields = [
            'id', 'prescription', 'medication', 'medication_name',
            'quantity', 'dispensed_by', 'dispensed_by_name',
            'patient_name', 'dispensed_at', 'status', 'notes'
        ]
        read_only_fields = ['dispensed_by', 'dispensed_at']