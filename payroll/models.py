import uuid
from django.db import models
from employees.models import Employee
from companies.models import Company


class Salary(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)


class Allowance(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Deduction(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Payroll(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    processed_at = models.DateTimeField(auto_now_add=True)


class Payslip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE)

    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)