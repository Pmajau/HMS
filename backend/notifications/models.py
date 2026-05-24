from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('appointment', 'Appointment'),
        ('lab_result', 'Lab Result'),
        ('billing', 'Billing'),
        ('admission', 'Admission'),
        ('discharge', 'Discharge'),
        ('prescription', 'Prescription'),
        ('general', 'General'),
    ]

    recipient   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=255)
    message     = models.TextField()
    notif_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read     = models.BooleanField(default=False)
    link        = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient} - {self.title}"