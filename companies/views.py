from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.decorators import api_view

from django.utils import timezone
from django.db.models import Sum

from .models import Company, CompanySettings
from .serializers import CompanySerializer, CompanySettingsSerializer

from appsettings.models import CompanySettings
from employees.models import Employee
from payroll.models import PayrollRun, Payslip
from leave.models import LeaveRequest  # if you have it

class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    def get_queryset(self):
        user = self.request.user
        if user.role == 'super_admin':
            return Company.objects.all()
        return Company.objects.filter(id=self.request.user.company_id)
        
        
        


@api_view(["GET"])
def dashboard_stats(request):
    user = request.user
    company_id = user.company_id
    today = timezone.localdate()
    current_year = today.year
    current_month = today.month
    # Employees
    total_employees = Employee.objects.filter(
        company_id=company_id,
        status="active"
    ).count()

    # Payroll runs
    total_payroll = Payslip.objects.filter(
        payroll__company_id=company_id,
        payroll__month=current_month,
        payroll__year=current_year,
        payroll__status="processed"
    ).aggregate(total=Sum("net_salary"))["total"] or 0

    # Leaves (SAFE)
    active_leaves = 0
    if 'LeaveRequest' in globals():
        active_leaves = LeaveRequest.objects.filter(
            employee__company_id=company_id,
            status="approved"
        ).count()
    if user.role == 'super_admin':
        active_companies = Company.objects.all().count()
        
        return Response({
            "totalEmployees": total_employees,
            "activeLeaves": active_leaves,
            "totalPayroll": total_payroll,
            "activeCompanies": active_companies,
        })
    return Response({
        "totalEmployees": total_employees,
        "activeLeaves": active_leaves,
        "totalPayroll": total_payroll,
    })
    
    
    



class CompanySettingsView(RetrieveUpdateAPIView):
    serializer_class = CompanySettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # refactor this with user roles latter
        return self.request.user.company.settings