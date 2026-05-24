from rest_framework import serializers
from .models import Ward, Bed, BedAssignment


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Bed
        fields = '__all__'
        read_only_fields = ['ward']


class WardSerializer(serializers.ModelSerializer):
    beds            = BedSerializer(many=True, read_only=True)
    available_beds  = serializers.IntegerField(read_only=True)
    occupied_beds   = serializers.IntegerField(read_only=True)
    occupancy_rate  = serializers.FloatField(read_only=True)

    class Meta:
        model  = Ward
        fields = [
            'id', 'name', 'ward_type', 'description', 'floor',
            'total_beds', 'available_beds', 'occupied_beds',
            'occupancy_rate', 'is_active', 'beds', 'created_at'
        ]
        read_only_fields = ['created_at']


class BedAssignmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    bed_number   = serializers.CharField(source='bed.bed_number', read_only=True)
    ward_name    = serializers.CharField(source='bed.ward.name', read_only=True)

    class Meta:
        model  = BedAssignment
        fields = '__all__'
        read_only_fields = ['assigned_by', 'assigned_at', 'released_at']