from django.db import models
from django.conf import settings


class MedicalRecord(models.Model):
    patient     = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='medical_records')
    doctor      = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    visit_date  = models.DateField(auto_now_add=True)
    symptoms    = models.TextField()
    diagnosis   = models.TextField()
    treatment   = models.TextField()
    notes       = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.patient} - {self.visit_date}"


class Prescription(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_daily', 'Three Times Daily'),
        ('four_daily', 'Four Times Daily'),
        ('as_needed', 'As Needed'),
        ('weekly', 'Weekly'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication     = models.ForeignKey('pharmacy.Medication', on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    dosage         = models.CharField(max_length=100)
    frequency      = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days  = models.PositiveIntegerField()
    instructions   = models.TextField(blank=True)
    is_dispensed   = models.BooleanField(default=False)

    class Meta:
        db_table = 'prescriptions'

    def __str__(self):
        return f"{self.medication} - {self.dosage} ({self.frequency})"


class LabTest(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('sample_collected', 'Sample Collected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_tests')
    test_name      = models.CharField(max_length=200)
    ordered_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='lab_orders')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    result         = models.TextField(blank=True)
    result_file    = models.FileField(upload_to='lab_results/', blank=True, null=True)
    ordered_at     = models.DateTimeField(auto_now_add=True)
    completed_at   = models.DateTimeField(null=True, blank=True)
    notes          = models.TextField(blank=True)

    class Meta:
        db_table = 'lab_tests'
        ordering = ['-ordered_at']

    def __str__(self):
        return f"{self.test_name} - {self.status}"