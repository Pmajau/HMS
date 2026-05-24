from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Invoice, InvoiceItem, Payment
from .serializers import (
    InvoiceSerializer, InvoiceCreateSerializer,
    InvoiceItemSerializer, PaymentSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrReceptionist


class InvoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReceptionist]
    filterset_fields   = ['status', 'patient']
    search_fields      = ['invoice_number', 'patient__user__first_name', 'patient__user__last_name']
    ordering_fields    = ['created_at', 'due_date', 'total_amount']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.select_related('patient__user').prefetch_related('items', 'payments')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InvoiceDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrReceptionist]
    queryset           = Invoice.objects.select_related('patient__user').prefetch_related('items', 'payments')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceCreateSerializer
        return InvoiceSerializer


class PatientInvoicesView(generics.ListAPIView):
    """View all invoices for a specific patient"""
    serializer_class   = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_patient:
            return Invoice.objects.filter(patient__user=user).prefetch_related('items', 'payments')
        return Invoice.objects.filter(
            patient_id=self.kwargs['patient_id']
        ).prefetch_related('items', 'payments')


class AddInvoiceItemView(generics.CreateAPIView):
    serializer_class   = InvoiceItemSerializer
    permission_classes = [IsAdminOrReceptionist]

    def perform_create(self, serializer):
        invoice = Invoice.objects.get(id=self.kwargs['invoice_id'])
        item    = serializer.save(invoice=invoice)
        invoice.total_amount = sum(i.total_price for i in invoice.items.all())
        invoice.save()


class RecordPaymentView(generics.CreateAPIView):
    """Record a payment against an invoice"""
    serializer_class   = PaymentSerializer
    permission_classes = [IsAdminOrReceptionist]

    def perform_create(self, serializer):
        invoice = Invoice.objects.get(id=self.kwargs['invoice_id'])
        serializer.save(invoice=invoice, received_by=self.request.user)


class FinancialSummaryView(APIView):
    """Admin financial summary report"""
    permission_classes = [IsAdmin]

    def get(self, request):
        today  = timezone.now().date()
        month  = today.month
        year   = today.year

        summary = {
            'total_invoices'     : Invoice.objects.count(),
            'total_revenue'      : Invoice.objects.aggregate(t=Sum('paid_amount'))['t'] or 0,
            'outstanding_balance': Invoice.objects.aggregate(
                t=Sum('total_amount') - Sum('paid_amount')
            )['t'] or 0,
            'monthly_revenue'    : Invoice.objects.filter(
                issued_date__month=month, issued_date__year=year
            ).aggregate(t=Sum('paid_amount'))['t'] or 0,
            'invoices_by_status' : {
                s: Invoice.objects.filter(status=s).count()
                for s, _ in Invoice.STATUS_CHOICES
            },
            'recent_payments'    : PaymentSerializer(
                Payment.objects.select_related('invoice__patient__user')
                .order_by('-payment_date')[:10],
                many=True
            ).data,
        }
        return Response(summary)