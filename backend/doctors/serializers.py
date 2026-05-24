from rest_framework import serializers
from .models import Doctor, Specialization, Schedule, DoctorPatientAssignment


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Specialization
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Schedule
        fields = '__all__'
        read_only_fields = ['doctor']


class DoctorSerializer(serializers.ModelSerializer):
    full_name        = serializers.CharField(source='user.get_full_name', read_only=True)
    email            = serializers.CharField(source='user.email', read_only=True)
    phone_number     = serializers.CharField(source='user.phone_number', read_only=True)
    specialization   = SpecializationSerializer(read_only=True)
    specialization_id = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(), source='specialization', write_only=True
    )
    schedules        = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model  = Doctor
        fields = [
            'id', 'doctor_number', 'full_name', 'email', 'phone_number',
            'specialization', 'specialization_id', 'license_number',
            'years_experience', 'bio', 'consultation_fee',
            'is_available', 'schedules', 'created_at'
        ]
        read_only_fields = ['doctor_number', 'created_at']


class DoctorCreateSerializer(serializers.Serializer):
    """Creates a User + Doctor profile in one request"""
    email            = serializers.EmailField()
    first_name       = serializers.CharField()
    last_name        = serializers.CharField()
    phone_number     = serializers.CharField(required=False)
    password         = serializers.CharField(write_only=True)
    password2        = serializers.CharField(write_only=True)
    specialization_id = serializers.IntegerField()
    license_number   = serializers.CharField()
    years_experience = serializers.IntegerField(required=False, default=0)
    bio              = serializers.CharField(required=False)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)

    def validate(self, attrs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        return attrs

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        specialization_id = validated_data.pop('specialization_id')
        user_fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password2']
        user_data   = {k: validated_data.pop(k) for k in user_fields if k in validated_data}
        user_data['role'] = 'doctor'
        user_data.pop('password2')
        user   = User.objects.create_user(**user_data)
        doctor = Doctor.objects.create(
            user=user,
            specialization_id=specialization_id,
            **validated_data
        )
        return doctor


class DoctorPatientAssignmentSerializer(serializers.ModelSerializer):
    doctor_name  = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model  = DoctorPatientAssignment
        fields = '__all__'