from django.db import models
from django.conf import settings


class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    patient_number   = models.CharField(max_length=20, unique=True, editable=False)
    date_of_birth    = models.DateField()
    gender           = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group      = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    marital_status   = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    address          = models.TextField(blank=True)
    city             = models.CharField(max_length=100, blank=True)
    nationality      = models.CharField(max_length=100, blank=True)
    id_number        = models.CharField(max_length=50, blank=True)
    profile_picture  = models.ImageField(upload_to='patients/', blank=True, null=True)
    allergies        = models.TextField(blank=True)
    chronic_diseases = models.TextField(blank=True)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_number} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.patient_number:
            last = Patient.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.patient_number = f"PAT-{next_id:05d}"
        super().save(*args, **kwargs)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'), ('parent', 'Parent'),
        ('sibling', 'Sibling'), ('child', 'Child'),
        ('friend', 'Friend'), ('other', 'Other'),
    ]

    patient      = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name         = models.CharField(max_length=200)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    phone_number = models.CharField(max_length=20)
    email        = models.EmailField(blank=True)
    address      = models.TextField(blank=True)

    class Meta:
        db_table = 'emergency_contacts'

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.patient}"


class Admission(models.Model):
    STATUS_CHOICES = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
    ]

    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    admitted_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='admissions_made')
    admission_date   = models.DateTimeField(auto_now_add=True)
    discharge_date   = models.DateTimeField(null=True, blank=True)
    reason           = models.TextField()
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='admitted')
    discharge_notes  = models.TextField(blank=True)

    class Meta:
        db_table = 'admissions'
        ordering = ['-admission_date']

    def __str__(self):
        return f"{self.patient} - {self.status}"