import uuid
from django.db import models
from companies.models import Company


class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    employee_limit = models.IntegerField(default=10)


class Subscription(models.Model):
    STATUS = [
        ("trial", "Trial"),
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=20, choices=STATUS)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()