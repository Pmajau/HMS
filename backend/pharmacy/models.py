from django.db import models
from django.conf import settings


class Medication(models.Model):
    CATEGORY_CHOICES = [
        ('antibiotic', 'Antibiotic'),
        ('analgesic', 'Analgesic'),
        ('antiviral', 'Antiviral'),
        ('antifungal', 'Antifungal'),
        ('antihistamine', 'Antihistamine'),
        ('vitamin', 'Vitamin/Supplement'),
        ('other', 'Other'),
    ]

    name             = models.CharField(max_length=200)
    generic_name     = models.CharField(max_length=200, blank=True)
    category         = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description      = models.TextField(blank=True)
    unit             = models.CharField(max_length=50)
    unit_price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity   = models.PositiveIntegerField(default=0)
    reorder_level    = models.PositiveIntegerField(default=10)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medications'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level


class DispensingRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled'),
    ]

    prescription   = models.OneToOneField('medical_records.Prescription', on_delete=models.CASCADE, related_name='dispensing_record')
    medication     = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='dispensing_records')
    quantity       = models.PositiveIntegerField()
    dispensed_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='dispensed_medications')
    dispensed_at   = models.DateTimeField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes          = models.TextField(blank=True)

    class Meta:
        db_table = 'dispensing_records'
        ordering = ['-dispensed_at']

    def __str__(self):
        return f"{self.medication} - {self.status}"