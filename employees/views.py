from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer
from accounts.permissions import IsAdminOrHR


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    def get_queryset(self):
        if user.role == 'super_admin':
            return Employee.objects.all()
        return Employee.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)