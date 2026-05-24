from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Patient, EmergencyContact, Admission
from accounts.serializers import RegisterSerializer

User = get_user_model()


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmergencyContact
        fields = '__all__'
        read_only_fields = ['patient']


class AdmissionSerializer(serializers.ModelSerializer):
    admitted_by_name = serializers.CharField(source='admitted_by.get_full_name', read_only=True)

    class Meta:
        model  = Admission
        fields = '__all__'
        read_only_fields = ['patient', 'admitted_by', 'admission_date']


class PatientSerializer(serializers.ModelSerializer):
    full_name         = serializers.CharField(source='user.get_full_name', read_only=True)
    email             = serializers.CharField(source='user.email', read_only=True)
    phone_number      = serializers.CharField(source='user.phone_number', read_only=True)
    age               = serializers.IntegerField(read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)

    class Meta:
        model  = Patient
        fields = [
            'id', 'patient_number', 'full_name', 'email', 'phone_number',
            'date_of_birth', 'age', 'gender', 'blood_group', 'marital_status',
            'address', 'city', 'nationality', 'id_number', 'profile_picture',
            'allergies', 'chronic_diseases', 'notes',
            'emergency_contacts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['patient_number', 'created_at', 'updated_at']


class PatientCreateSerializer(serializers.Serializer):
    """Creates a User + Patient profile in one request"""
    email        = serializers.EmailField()
    first_name   = serializers.CharField()
    last_name    = serializers.CharField()
    phone_number = serializers.CharField(required=False)
    password     = serializers.CharField(write_only=True)
    password2    = serializers.CharField(write_only=True)

    date_of_birth    = serializers.DateField()
    gender           = serializers.ChoiceField(choices=['male', 'female', 'other'])
    blood_group      = serializers.CharField(required=False)
    marital_status   = serializers.CharField(required=False)
    address          = serializers.CharField(required=False)
    city             = serializers.CharField(required=False)
    nationality      = serializers.CharField(required=False)
    id_number        = serializers.CharField(required=False)
    allergies        = serializers.CharField(required=False)
    chronic_diseases = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        return attrs

    def create(self, validated_data):
        user_fields = ['email', 'first_name', 'last_name', 'phone_number', 'password', 'password2']
        user_data   = {k: validated_data.pop(k) for k in user_fields if k in validated_data}
        user_data['role'] = 'patient'
        user_data.pop('password2')

        user    = User.objects.create_user(**user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient