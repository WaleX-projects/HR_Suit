# models.py
from django.db import models

from companies.models import Company 

class Plan(models.Model):
    name = models.CharField(max_length=100) # e.g., 'Pro'
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_employees = models.IntegerField(null=True)
    has_payroll = models.BooleanField(default=False)

class Subscription(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20) # 'active', 'past_due', 'canceled'
    next_billing_date = models.DateField(null=True)
