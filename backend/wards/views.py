from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Ward, Bed, BedAssignment
from .serializers import WardSerializer, BedSerializer, BedAssignmentSerializer
from accounts.permissions import IsAdmin, IsAdminOrReceptionist, IsAdminOrDoctor


class WardListCreateView(generics.ListCreateAPIView):
    serializer_class   = WardSerializer
    filterset_fields   = ['ward_type', 'is_active']
    search_fields      = ['name']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        return Ward.objects.prefetch_related('beds')


class WardDetailView(generics.RetrieveUpdateAPIView):
    queryset         = Ward.objects.prefetch_related('beds')
    serializer_class = WardSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [IsAdmin()]


class BedListCreateView(generics.ListCreateAPIView):
    serializer_class   = BedSerializer
    permission_classes = [IsAdminOrReceptionist]

    def get_queryset(self):
        return Bed.objects.filter(ward_id=self.kwargs['ward_id'])

    def perform_create(self, serializer):
        ward = Ward.objects.get(id=self.kwargs['ward_id'])
        serializer.save(ward=ward)
        ward.total_beds = ward.beds.count()
        ward.save()


class AssignBedView(generics.CreateAPIView):
    """Assign a bed to a patient"""
    serializer_class   = BedAssignmentSerializer
    permission_classes = [IsAdminOrReceptionist]

    def perform_create(self, serializer):
        bed = Bed.objects.get(id=self.kwargs['bed_id'])

        if bed.is_occupied:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('This bed is already occupied.')

        assignment = serializer.save(
            bed=bed,
            assigned_by=self.request.user
        )
        bed.is_occupied = True
        bed.save()
        return assignment


class ReleaseBedView(APIView):
    """Release a bed from a patient"""
    permission_classes = [IsAdminOrReceptionist]

    def post(self, request, bed_id):
        try:
            bed        = Bed.objects.get(id=bed_id)
            assignment = BedAssignment.objects.filter(
                bed=bed, status='active'
            ).latest('assigned_at')
        except (Bed.DoesNotExist, BedAssignment.DoesNotExist):
            return Response(
                {'error': 'No active assignment found for this bed'},
                status=status.HTTP_404_NOT_FOUND
            )

        assignment.status      = 'released'
        assignment.released_at = timezone.now()
        assignment.notes       = request.data.get('notes', '')
        assignment.save()

        bed.is_occupied = False
        bed.save()

        return Response(BedAssignmentSerializer(assignment).data)


class WardOccupancyView(APIView):
    """Dashboard showing occupancy for all wards"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wards = Ward.objects.filter(is_active=True).prefetch_related('beds')
        data  = [{
            'ward_id'       : w.id,
            'ward_name'     : w.name,
            'ward_type'     : w.ward_type,
            'total_beds'    : w.total_beds,
            'available_beds': w.available_beds,
            'occupied_beds' : w.occupied_beds,
            'occupancy_rate': w.occupancy_rate,
        } for w in wards]
        return Response(data)


class BedAssignmentHistoryView(generics.ListAPIView):
    serializer_class   = BedAssignmentSerializer
    permission_classes = [IsAdminOrDoctor]

    def get_queryset(self):
        return BedAssignment.objects.filter(
            patient_id=self.kwargs['patient_id']
        ).select_related('bed__ward')