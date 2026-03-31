from rest_framework import serializers
from .models import Attendance, Shift, EmployeeShift

from django.utils.timezone import localtime


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.first_name", read_only=True)
    clock_in_time = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "status",
            "date",
            "clock_in",
            "clock_in_time",
            "created_at",
        ]
        read_only_fields = ["id", "status", "date", "clock_in", "created_at"]

    def get_clock_in_time(self, obj):
        return localtime(obj.clock_in).strftime("%I:%M %p")
        
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = "__all__"

class EmployeeShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShift
        fields = "__all__"