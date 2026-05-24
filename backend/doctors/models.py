from django.db import models
from django.conf import settings


class Specialization(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'specializations'

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_number    = models.CharField(max_length=20, unique=True, editable=False)
    specialization   = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, related_name='doctors')
    license_number   = models.CharField(max_length=100, unique=True)
    years_experience = models.PositiveIntegerField(default=0)
    bio              = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available     = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctors'
        ordering = ['user__first_name']

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

    def save(self, *args, **kwargs):
        if not self.doctor_number:
            last = Doctor.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.doctor_number = f"DOC-{next_id:05d}"
        super().save(*args, **kwargs)


class Schedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'), ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
        ('friday', 'Friday'), ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day        = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time   = models.TimeField()
    is_active  = models.BooleanField(default=True)

    class Meta:
        db_table = 'schedules'
        unique_together = ['doctor', 'day']

    def __str__(self):
        return f"{self.doctor} - {self.day} ({self.start_time} to {self.end_time})"


class DoctorPatientAssignment(models.Model):
    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='assignments')
    patient    = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='doctor_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)
    notes      = models.TextField(blank=True)

    class Meta:
        db_table = 'doctor_patient_assignments'
        unique_together = ['doctor', 'patient']

    def __str__(self):
        return f"Dr. {self.doctor} -> {self.patient}"