from rest_framework import serializers
from .models import Salary, Allowance, Deduction, Payroll, Payslip

class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = "__all__"

class AllowanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allowance
        fields = "__all__"

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = "__all__"

class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = "__all__"

class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = "__all__"