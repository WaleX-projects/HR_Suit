from rest_framework import serializers
from companies.models import Company 
from employees.models import Employee 
from attendance.models import Attendance,  Holiday
from .models import (
    
    PositionSalary,
    SalaryComponent,
    PositionSalaryComponent,
    PayrollRun,
    Payslip,
    PayslipItem,
    
)


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = "__all__"

class PositionSalaryComponentSerializer(serializers.ModelSerializer):
    component_id = serializers.UUIDField(write_only=True)
    component = SalaryComponentSerializer(read_only=True)

    class Meta:
        model = PositionSalaryComponent
        fields = ["id", "component", "component_id"]


class PositionSalarySerializer(serializers.ModelSerializer):
    components = PositionSalaryComponentSerializer(many=True)

    class Meta:
        model = PositionSalary
        fields = ["id", "basic_salary", "components"]

    def create(self, validated_data):
        components_data = validated_data.pop("components", [])
        position = self.context.get("position")
        company = self.context.get("company")

        position_salary = PositionSalary.objects.create(
            position=position,
            company=company,
            **validated_data
        )

        for comp in components_data:
            PositionSalaryComponent.objects.create(
                position_salary=position_salary,
                component_id=comp["component_id"]
            )

        return position_salary


class EmployeeSerializer(serializers.ModelSerializer):
    position_salary = PositionSalarySerializer(read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = "__all__"


class PayslipItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayslipItem
        fields = "__all__"

class PayslipSerializerAll(serializers.ModelSerializer):
    items = PayslipItemSerializer(many=True, read_only=True)
    employee_name = serializers.SerializerMethodField()
    payroll_month = serializers.IntegerField(source="payroll.month", read_only=True)
    payroll_year = serializers.IntegerField(source="payroll.year", read_only=True)
    payroll_status = serializers.CharField(source="payroll.status", read_only=True)

    class Meta:
        model = Payslip
        fields = [
            "id",
            "employee_name",
            "payroll",
            "payroll_month",
            "payroll_year",
            "payroll_status",
            "basic_salary",
            "total_allowance",
            "total_deduction",
            "net_salary",
            "items",   
            "created_at",
        ]
        
    def get_employee_name(self, obj):
        return (
            f"{obj.employee.first_name or ''} "
            f"{obj.employee.last_name or ''}"
        ).strip()
        
class PayslipSerializer(serializers.ModelSerializer):
    payroll_month = serializers.IntegerField(source="payroll.month", read_only=True)
    payroll_year = serializers.IntegerField(source="payroll.year", read_only=True)
    payroll_status = serializers.CharField(source="payroll.status", read_only=True)

    class Meta:
        model = Payslip
        fields = [
            "id",
            "payroll",
            "payroll_month",
            "payroll_year",
            "payroll_status",
            "basic_salary",
            "total_allowance",
            "total_deduction",
            "net_salary",
            "created_at",
        ]

class PayrollRunSerializer(serializers.ModelSerializer):
    payslips = PayslipSerializerAll(many=True, read_only=True)

    class Meta:
        model = PayrollRun
        fields = "__all__"