from django.db import models
from django.conf import settings


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    patient        = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='invoices')
    appointment    = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issued_date    = models.DateField(auto_now_add=True)
    due_date       = models.DateField()
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.patient}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{next_id:06d}"
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.update_status()
        super().save(*args, **kwargs)

    def update_status(self):
        if self.paid_amount >= self.total_amount and self.total_amount > 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partially_paid'

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount


class InvoiceItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('room_charge', 'Room Charge'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    ]

    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type   = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    quantity    = models.PositiveIntegerField(default=1)
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        db_table = 'invoice_items'

    def __str__(self):
        return f"{self.description} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
    ]

    invoice        = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference      = models.CharField(max_length=100, blank=True)
    received_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    payment_date   = models.DateTimeField(auto_now_add=True)
    notes          = models.TextField(blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.invoice} - {self.amount} ({self.method})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice paid amount
        invoice = self.invoice
        invoice.paid_amount = sum(p.amount for p in invoice.payments.all())
        invoice.update_status()
        Invoice.objects.filter(pk=invoice.pk).update(
            paid_amount=invoice.paid_amount,
            status=invoice.status
        )