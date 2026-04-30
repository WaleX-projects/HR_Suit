from rest_framework import serializers
from .models import Attendance, Shift, EmployeeShift,Holiday

from django.utils.timezone import localtime

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ["id", "name", "date", "is_global"]
        
        
        
from rest_framework import serializers
from datetime import datetime, timedelta

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.first_name", read_only=True)
    total_hours = serializers.SerializerMethodField()   # New field

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "status",
            "date",
            "clock_in",
            "clock_out",
            "total_hours",          # Added
            "created_at",
        ]
        read_only_fields = ["id", "status", "date", "created_at", "total_hours"]

    def get_clock_in(self, obj):
        """Format clock_in time nicely (e.g., '09:30')"""
        if obj.clock_in:
            return obj.clock_in.strftime("%H:%M")
        return None

    def get_clock_out(self, obj):
        """Format clock_in time nicely (e.g., '09:30')"""
        if obj.clock_in:
            return obj.clock_in.strftime("%H:%M")
        return None
    def get_total_hours(self, obj):
        """Calculate total hours between clock_in and clock_out (TimeField)"""
        if not obj.clock_in or not obj.clock_out:
            return None

        # Convert TimeField to datetime for calculation (using the same date)
        today = obj.date if hasattr(obj, 'date') and obj.date else datetime.now().date()

        clock_in_dt = datetime.combine(today, obj.clock_in)
        clock_out_dt = datetime.combine(today, obj.clock_out)
        """
        # Handle overnight shifts (clock out is earlier than clock in → next day)
        if clock_out_dt < clock_in_dt:
            clock_out_dt += timedelta(days=1)
        """    

        duration = clock_out_dt - clock_in_dt
        total_hours = duration.total_seconds() / 3600

        return round(total_hours, 2)   # Returns e.g. 8.5   
        
        
         
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = "__all__"

class EmployeeShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShift
        fields = "__all__"
        
        
        
        
from rest_framework import serializers
from .models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True
    )

    class Meta:
        model = Holiday
        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "date",
            "is_global",
            "is_recurring",
        ]
        read_only_fields = ["id", "company"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Holiday name cannot be empty."
            )
        return value        