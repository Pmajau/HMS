from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Medication, DispensingRecord
from .serializers import MedicationSerializer, DispensingRecordSerializer, StockUpdateSerializer
from accounts.permissions import IsAdmin, IsAdminOrDoctor, IsMedicalStaff


class MedicationListCreateView(generics.ListCreateAPIView):
    serializer_class   = MedicationSerializer
    filterset_fields   = ['category', 'is_active']
    search_fields      = ['name', 'generic_name']
    ordering_fields    = ['name', 'stock_quantity', 'unit_price']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = Medication.objects.all()
        low_stock = self.request.query_params.get('low_stock')
        if low_stock == 'true':
            from django.db.models import F
            qs = qs.filter(stock_quantity__lte=F('reorder_level'))
        return qs


class MedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MedicationSerializer
    queryset         = Medication.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]


class UpdateStockView(APIView):
    """Add or remove stock for a medication"""
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            medication = Medication.objects.get(pk=pk)
        except Medication.DoesNotExist:
            return Response({'error': 'Medication not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity             = serializer.validated_data['quantity']
        medication.stock_quantity += quantity

        if medication.stock_quantity < 0:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )

        medication.save()
        return Response(MedicationSerializer(medication).data)


class LowStockAlertsView(generics.ListAPIView):
    """List all medications below reorder level"""
    serializer_class   = MedicationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        from django.db.models import F
        return Medication.objects.filter(stock_quantity__lte=F('reorder_level'))


class DispensingRecordListView(generics.ListAPIView):
    serializer_class   = DispensingRecordSerializer
    permission_classes = [IsMedicalStaff]
    filterset_fields   = ['status', 'medication']
    ordering_fields    = ['dispensed_at']

    def get_queryset(self):
        return DispensingRecord.objects.select_related(
            'medication', 'dispensed_by', 'prescription__medical_record__patient__user'
        )


class DispensePrescriptionView(APIView):
    """Dispense a prescription and update stock"""
    permission_classes = [IsMedicalStaff]

    def post(self, request, prescription_id):
        from medical_records.models import Prescription

        try:
            prescription = Prescription.objects.get(id=prescription_id)
        except Prescription.DoesNotExist:
            return Response({'error': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(prescription, 'dispensing_record'):
            return Response(
                {'error': 'Prescription already dispensed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        medication = prescription.medication
        if medication.stock_quantity < 1:
            return Response(
                {'error': 'Medication out of stock'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record = DispensingRecord.objects.create(
            prescription=prescription,
            medication=medication,
            quantity=1,
            dispensed_by=request.user,
            dispensed_at=timezone.now(),
            status='dispensed'
        )

        medication.stock_quantity -= 1
        medication.save()

        prescription.is_dispensed = True
        prescription.save()

        return Response(DispensingRecordSerializer(record).data, status=status.HTTP_201_CREATED)