

from rest_framework import serializers
from .models import Employee, Position, Department
from payroll.serializers import (PositionSalarySerializer,
        PositionSalaryComponentSerializer,
        SalaryComponentSerializer)


class DepartmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id","company")
    
    
class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    salaries = PositionSalarySerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Position
        fields = [
            "id",
            "title",
            "department",
            "department_name",
            "salaries",
        ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        salaries_data = validated_data.pop("salaries", [])

        position = Position.objects.create(**validated_data)

        company = position.department.company

        for salary_data in salaries_data:
            PositionSalarySerializer().create({
                **salary_data,
            }, context={
                "position": position,
                "company": company
            })

        return position




class EmployeeSerializer(serializers.ModelSerializer):
    #  Write (input)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        write_only=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True
    )

    # 💳 BANK (write-only input)
    bank_account_number = serializers.CharField(write_only=True)
    bank_code = serializers.CharField(write_only=True)
    #  Read (output)
    department_detail = serializers.CharField(source="department.name", read_only=True)
    position_detail = serializers.CharField(source="position.title", read_only=True)
    company_detail = serializers.CharField(source="company.name", read_only=True)
    face_verified = serializers.BooleanField(read_only=True) 
    masked_account_number = serializers.SerializerMethodField()
    

    def get_masked_account_number(self, obj):
        if obj.bank_account_number:
            return "****" + obj.bank_account_number[-4:]
        return None

    class Meta:
        model = Employee
        fields = [
            "id",
            "company",
            "company_detail",
            "first_name",
            "last_name",
            "email",
            "phone",
            "hire_date",
            "status",
            "face_verified",
            

            # write-only inputs
            "department",
            "position",
            "bank_account_number",
            "bank_code",

            # read-only outputs
            "department_detail",
            "position_detail",

            # 💳 bank outputs
            "bank_name",
            "bank_account_type",
            "currency",
            "masked_account_number",
            "bank_account_name",
        ]
        read_only_fields = ["id", "company"]