import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from employees.models import Employee
from accounts.models import User
from companies.models import Company


# ==========================================
# LEAVE TYPE / POLICY
# ==========================================
class LeaveType(models.Model):
    """
    Example:
    Annual Leave
    Sick Leave
    Casual Leave
    Maternity Leave
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_types"
    )

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30, unique=True)

    days_allowed = models.PositiveIntegerField(default=0)

    carry_forward = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=True)
    paid_leave = models.BooleanField(default=True)

    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["company", "name"]

    def __str__(self):
        return self.name


# ==========================================
# EMPLOYEE LEAVE BALANCE
# ==========================================
class LeaveBalance(models.Model):
    """
    Stores yearly balance per employee
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_balances"
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name="balances"
    )

    year = models.PositiveIntegerField(default=timezone.now().year)

    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ["employee", "leave_type", "year"]

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days - self.pending_days

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.year})"


# ==========================================
# LEAVE REQUEST
# ==========================================
class LeaveRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    total_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leave_requests"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    rejection_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def save(self, *args, **kwargs):
        self.total_days = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"


# ==========================================
# LEAVE APPROVAL HISTORY
# ==========================================
class LeaveApprovalLog(models.Model):
    ACTIONS = [
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    action = models.CharField(max_length=20, choices=ACTIONS)

    action_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.leave_request} - {self.action}"


# ==========================================
# COMPANY LEAVE POLICY
# ==========================================
class LeavePolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="leave_policy"
    )

    weekends_count_as_leave = models.BooleanField(default=False)
    allow_half_day = models.BooleanField(default=True)
    max_consecutive_days = models.PositiveIntegerField(default=30)
    require_attachment_for_sick_leave = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} Leave Policy"