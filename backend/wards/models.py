from django.db import models
from django.conf import settings


class Ward(models.Model):
    WARD_TYPE_CHOICES = [
        ('general', 'General'),
        ('private', 'Private'),
        ('icu', 'ICU'),
        ('maternity', 'Maternity'),
        ('pediatric', 'Pediatric'),
        ('emergency', 'Emergency'),
    ]

    name        = models.CharField(max_length=100)
    ward_type   = models.CharField(max_length=20, choices=WARD_TYPE_CHOICES, default='general')
    description = models.TextField(blank=True)
    floor       = models.CharField(max_length=20, blank=True)
    total_beds  = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wards'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.ward_type})"

    @property
    def available_beds(self):
        return self.beds.filter(is_occupied=False, is_active=True).count()

    @property
    def occupied_beds(self):
        return self.beds.filter(is_occupied=True).count()

    @property
    def occupancy_rate(self):
        if self.total_beds == 0:
            return 0
        return round((self.occupied_beds / self.total_beds) * 100, 1)


class Bed(models.Model):
    ward        = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds')
    bed_number  = models.CharField(max_length=20)
    is_occupied = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    notes       = models.TextField(blank=True)

    class Meta:
        db_table      = 'beds'
        unique_together = ['ward', 'bed_number']
        ordering      = ['bed_number']

    def __str__(self):
        status = 'Occupied' if self.is_occupied else 'Available'
        return f"{self.ward.name} - Bed {self.bed_number} ({status})"


class BedAssignment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('released', 'Released'),
    ]

    bed          = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='assignments')
    patient      = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='bed_assignments')
    admission    = models.ForeignKey('patients.Admission', on_delete=models.SET_NULL, null=True, blank=True, related_name='bed_assignment')
    assigned_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    assigned_at  = models.DateTimeField(auto_now_add=True)
    released_at  = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes        = models.TextField(blank=True)

    class Meta:
        db_table = 'bed_assignments'
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.patient} -> {self.bed}"