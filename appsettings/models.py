# settings/models.py
from django.db import models
from django.core.exceptions import ValidationError

class CompanySettings(models.Model):
    # General
    company_name = models.CharField(max_length=255, default="HR Suit")
    timezone = models.CharField(max_length=50, default="Africa/Lagos")
    date_format = models.CharField(max_length=20, default="DD/MM/YYYY")
    currency = models.CharField(max_length=10, default="NGN")

    # Attendance
    work_hours_per_day = models.PositiveIntegerField(default=8)
    allow_late_arrival = models.BooleanField(default=True)
    late_arrival_grace_minutes = models.PositiveIntegerField(default=15)
    require_face_verification = models.BooleanField(default=True)
    geo_fencing_enabled = models.BooleanField(default=False)
    work_latitude = models.FloatField(null=True, blank=True)
    work_longitude = models.FloatField(null=True, blank=True)
    work_radius_meters = models.PositiveIntegerField(default=100)  # Default 100m radius
    
    # Payroll
    payroll_day = models.PositiveIntegerField(default=25)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=7.5)
    allow_manual_payslip = models.BooleanField(default=True)

    # Leave
    carry_forward_leave = models.BooleanField(default=True)
    max_carry_forward_days = models.PositiveIntegerField(default=10)
    leave_approval_required = models.BooleanField(default=True)

    # Notifications
    email_notifications = models.BooleanField(default=True)
    slack_notifications = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def clean(self):
        if CompanySettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Only one Company Settings record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        # Force only one instance
        if not self.pk and CompanySettings.objects.exists():
            existing = CompanySettings.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Company Settings - {self.company_name}"