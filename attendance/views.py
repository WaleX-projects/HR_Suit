from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, Shift, EmployeeShift
from .serializers import AttendanceSerializer, ShiftSerializer, EmployeeShiftSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attendance.objects.filter(employee__company=self.request.user.company)

class ShiftViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    queryset = Shift.objects.all()

class EmployeeShiftViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmployeeShift.objects.filter(employee__company=self.request.user.company)