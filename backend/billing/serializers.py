from rest_framework import serializers
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = InvoiceItem
        fields = '__all__'
        read_only_fields = ['invoice', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

    class Meta:
        model  = Payment
        fields = '__all__'
        read_only_fields = ['invoice', 'received_by', 'payment_date']


class InvoiceSerializer(serializers.ModelSerializer):
    patient_name   = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    patient_number = serializers.CharField(source='patient.patient_number', read_only=True)
    items          = InvoiceItemSerializer(many=True, read_only=True)
    payments       = PaymentSerializer(many=True, read_only=True)
    balance_due    = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = Invoice
        fields = [
            'id', 'invoice_number', 'patient', 'patient_name', 'patient_number',
            'appointment', 'status', 'issued_date', 'due_date',
            'total_amount', 'paid_amount', 'balance_due',
            'notes', 'items', 'payments', 'created_at'
        ]
        read_only_fields = ['invoice_number', 'total_amount', 'paid_amount', 'issued_date', 'created_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model  = Invoice
        fields = ['patient', 'appointment', 'due_date', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice    = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        # Recalculate total
        invoice.total_amount = sum(item.total_price for item in invoice.items.all())
        invoice.status = 'issued'
        invoice.save()
        return invoice