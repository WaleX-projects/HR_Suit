from rest_framework import serializers
from .models import LeaveType, LeaveRequest
from employees.models import Employee  # adjust import if needed


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "days_allowed"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.username", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "company",
            "employee",
            "employee_name",
            "leave_type",
            "leave_type_name",
            "start_date",
            "end_date",
            "status",
            "reason",
            "approved_by",
            "approved_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "approved_by", "company", "employee_name", "leave_type_name"]

    def get_employee_name(self, obj):
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}".strip()
        return "Unknown"

    # Validation
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    """Separate serializer for creation to allow admin/HR to choose any employee"""
    
    class Meta:
        model = LeaveRequest
        fields = ["employee", "leave_type", "start_date", "end_date", "reason"]
    
    def validate_employee(self, employee):
        user = self.context['request'].user
        # Optional: Restrict to same company
        if employee.company != user.company:
            raise serializers.ValidationError("You can only create leaves for employees in your company.")
        return employee