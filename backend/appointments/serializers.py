from rest_framework import serializers
from .models import Appointment, AppointmentStatusHistory


class AppointmentStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)

    class Meta:
        model  = AppointmentStatusHistory
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name     = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name      = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    specialization   = serializers.CharField(source='doctor.specialization.name', read_only=True)
    status_history   = AppointmentStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model  = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'specialization', 'appointment_date', 'appointment_time',
            'appointment_type', 'status', 'reason', 'notes',
            'status_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        doctor = attrs.get('doctor')
        date   = attrs.get('appointment_date')
        time   = attrs.get('appointment_time')
        qs = Appointment.objects.filter(
            doctor=doctor, appointment_date=date, appointment_time=time
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "This doctor already has an appointment at this date and time."
            )
        return attrs


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        'pending', 'confirmed', 'completed', 'cancelled', 'rescheduled'
    ])
    reason           = serializers.CharField(required=False, allow_blank=True)
    appointment_date = serializers.DateField(required=False)
    appointment_time = serializers.TimeField(required=False)