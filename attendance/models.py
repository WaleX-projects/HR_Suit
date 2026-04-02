import uuid
from django.db import models
from employees.models import Employee

from companies.models import Company 


class Attendance(models.Model):
    class StatusChoices(models.TextChoices):
        PRESENT = "present", "Present"
        LATE = "late", "Late"
        ABSENT = "absent", "Absent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendances"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PRESENT
    )

    date = models.DateField(auto_now_add=True)

    clock_in = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "date")
        
class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()


class EmployeeShift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    
    
import uuid
from django.db import models
from companies.models import Company


class Holiday(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255)
    date = models.DateField()

    is_global = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=True)

    def __str__(self):
        return self.name