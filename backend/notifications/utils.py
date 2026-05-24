from django.core.mail import send_mail
from django.conf import settings
from .models import Notification


def send_notification(recipient, title, message, notif_type='general', link=''):
    """Create an in-app notification"""
    Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notif_type=notif_type,
        link=link
    )


def send_email_notification(recipient, subject, message):
    """Send an email notification"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient.email],
            fail_silently=True,
        )
    except Exception:
        pass


def notify_appointment_confirmed(appointment):
    patient_user = appointment.patient.user
    doctor_user  = appointment.doctor.user

    send_notification(
        recipient=patient_user,
        title='Appointment Confirmed',
        message=f'Your appointment with Dr. {doctor_user.get_full_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.',
        notif_type='appointment',
    )
    send_email_notification(
        recipient=patient_user,
        subject='Appointment Confirmed - HMS',
        message=f'Dear {patient_user.get_full_name()},\n\nYour appointment with Dr. {doctor_user.get_full_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.\n\nThank you.'
    )


def notify_appointment_cancelled(appointment):
    patient_user = appointment.patient.user
    send_notification(
        recipient=patient_user,
        title='Appointment Cancelled',
        message=f'Your appointment on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled.',
        notif_type='appointment',
    )


def notify_lab_result_ready(lab_test):
    patient_user = lab_test.medical_record.patient.user
    send_notification(
        recipient=patient_user,
        title='Lab Result Ready',
        message=f'Your {lab_test.test_name} result is now available.',
        notif_type='lab_result',
    )


def notify_invoice_issued(invoice):
    patient_user = invoice.patient.user
    send_notification(
        recipient=patient_user,
        title='Invoice Issued',
        message=f'Invoice {invoice.invoice_number} for KES {invoice.total_amount} has been issued. Due date: {invoice.due_date}.',
        notif_type='billing',
    )


def notify_low_stock(medication):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admins = User.objects.filter(role='admin', is_active=True)
    for admin in admins:
        send_notification(
            recipient=admin,
            title='Low Stock Alert',
            message=f'{medication.name} is running low. Current stock: {medication.stock_quantity} {medication.unit}.',
            notif_type='general',
        )