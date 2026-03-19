from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Salary, Allowance, Deduction, Payroll, Payslip
from .serializers import SalarySerializer, AllowanceSerializer, DeductionSerializer, PayrollSerializer, PayslipSerializer
from accounts.permissions import IsAdminOrHR

class SalaryViewSet(viewsets.ModelViewSet):
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = Salary.objects.all()

class AllowanceViewSet(viewsets.ModelViewSet):
    serializer_class = AllowanceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = Allowance.objects.all()

class DeductionViewSet(viewsets.ModelViewSet):
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    queryset = Deduction.objects.all()
class PayrollViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrHR]
class PayrollViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return Payroll.objects.filter(company=self.request.user.company)

class PayslipViewSet(viewsets.ModelViewSet):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        return Payslip.objects.filter(employee__company=self.request.user.company)