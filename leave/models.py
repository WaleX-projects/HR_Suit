import uuid
from django.db import models
from employees.models import Employee
from accounts.models import User


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    days_allowed = models.IntegerField()


class LeaveRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    reason = models.TextField()

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)