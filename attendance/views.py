from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, Shift, EmployeeShift
from .serializers import AttendanceSerializer, ShiftSerializer, EmployeeShiftSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 👑 Admin & HR see all
        if user.role in ["admin", "hr"]:
            return Attendance.objects.filter(employee__company=user.company)

        # 👤 Employee sees only theirs
        return Attendance.objects.filter(employee__user=user)
class ShiftViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    queryset = Shift.objects.all()

class EmployeeShiftViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmployeeShift.objects.filter(employee__company=self.request.user.company)