

from rest_framework import serializers
from .models import Employee, Position, Department
from payroll.models import PositionSalary,SalaryComponent,PositionSalaryComponent
from payroll.serializers import (PositionSalarySerializer,
        PositionSalaryComponentSerializer,
        SalaryComponentSerializer)

        
class DepartmentSerializer(serializers.ModelSerializer):
    # This matches the name we used in .annotate() in the view
    total_positions = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "company", "total_positions"]
        read_only_fields = ("id", "company")


class ComponentInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
class PositionSerializer(serializers.ModelSerializer):
    # WRITE
    components = ComponentInputSerializer(many=True, write_only=True)

    # READ
    components_display = serializers.SerializerMethodField()

    # WRITE
    basic_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        write_only=True
    )

    # READ
    basic_salary_display = serializers.DecimalField(
        source="salary.first.basic_salary",
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Position
        fields = [
            "id",
            "title",
            "department",
            "is_single_role",

            "components",           # write
            "components_display",   # read

            "basic_salary",         # write
            "basic_salary_display"  # read
        ]

    def get_components_display(self, obj):
        salary = obj.salary.first()
        if not salary:
            return []

        return PositionSalaryComponentSerializer(
            salary.components.all(),
            many=True
        ).data
    def create(self, validated_data):
        components_data = validated_data.pop("components", [])
        basic_salary = validated_data.pop("basic_salary")

        # Create Position
        position = Position.objects.create(**validated_data)
        company = position.department.company

        # Create PositionSalary
        position_salary = PositionSalary.objects.create(
            position=position,
            company=company,
            basic_salary=basic_salary,
        )

        # Create components
        for comp in components_data:
            component, _ = SalaryComponent.objects.get_or_create(
                company=company,
                name=comp["name"]
            )

            PositionSalaryComponent.objects.create(
                position_salary=position_salary,
                component=component,
                value=comp["value"]   # ✅ value should be here (IMPORTANT)
            )

        return position
    

    
            
    
    def update(self, instance, validated_data):
        components_data = validated_data.pop("components", [])
        basic_salary = validated_data.pop("basic_salary", None)

        # Update Position fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        company = instance.department.company

        # Get or create salary
        position_salary, _ = PositionSalary.objects.get_or_create(
            position=instance,
            company=company,
            basic_salary=basic_salary,
        )

        # Update basic salary
        if basic_salary is not None:
            position_salary.basic_salary = basic_salary
            position_salary.save()

        # ❌ Remove old components (important)
        position_salary.components.all().delete()

        # ✅ Recreate components
        for comp in components_data:
            component, _ = SalaryComponent.objects.get_or_create(
                company=company,
                name=comp["name"]
            )

            PositionSalaryComponent.objects.create(
                position_salary=position_salary,
                component=component,
                value=comp["value"]
            )

        return instance        

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
        
        
        
        
import pandas as pd
from io import BytesIO
from rest_framework import serializers
from django.db import transaction
from django.utils.dateparse import parse_date
from .models import Employee, Department, Position
from companies.models import Company


class BulkEmployeeUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)

    def validate_file(self, file):
        if not file.name.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise serializers.ValidationError("Only Excel (.xlsx, .xls) or CSV files are allowed.")
        return file

    def create(self, validated_data):
        file = validated_data['file']
        company = validated_data['company']

        # Read file
        try:
            if file.name.lower().endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to read file: {str(e)}")

        employees_to_create = []
        errors = []

        with transaction.atomic():
            for index, row in df.iterrows():
                row_num = index + 2  # Excel row number for better error messages

                try:
                    # Get Department
                    dept_name = str(row.get('department') or row.get('Department') or '').strip()
                    if not dept_name:
                        raise ValueError("Department is required")

                    department = Department.objects.get(
                        company=company,
                        name__iexact=dept_name
                    )

                    # Get Position
                    pos_name = str(row.get('position') or row.get('Position') or '').strip()
                    if not pos_name:
                        raise ValueError("Position is required")

                    position = Position.objects.get(
                        company=company,
                        title__iexact=pos_name
                    )

                    # Parse hire_date safely
                    hire_date_str = row.get('hire_date') or row.get('Hire Date')
                    hire_date = parse_date(str(hire_date_str)) if hire_date_str else None
                    if not hire_date:
                        raise ValueError("Valid hire_date is required (format: YYYY-MM-DD)")

                    # Create Employee instance
                    employee = Employee(
                        company=company,
                        first_name=str(row.get('first_name') or row.get('First Name', '')).strip(),
                        last_name=str(row.get('last_name') or row.get('Last Name', '')).strip(),
                        email=str(row.get('email') or row.get('Email', '')).strip(),
                        phone=str(row.get('phone') or row.get('Phone', '')).strip(),
                        hire_date=hire_date,
                        department=department,
                        position=position,
                        status=str(row.get('status', 'active')).strip().lower(),

                        # Bank details (optional)
                        bank_name=str(row.get('bank_name') or '').strip() or None,
                        bank_account_name=str(row.get('bank_account_name') or '').strip() or None,
                        bank_account_number=str(row.get('bank_account_number') or '').strip() or None,
                        bank_code=str(row.get('bank_code') or '').strip() or None,
                        bank_account_type=str(row.get('bank_account_type', 'savings')).strip().lower(),
                        currency=str(row.get('currency', 'NGN')).strip().upper(),
                    )

                    # Basic validation
                    if not employee.first_name or not employee.last_name or not employee.email:
                        raise ValueError("First name, Last name and Email are required")

                    employees_to_create.append(employee)

                except Department.DoesNotExist:
                    errors.append(f"Row {row_num}: Department '{dept_name}' not found.")
                except Position.DoesNotExist:
                    errors.append(f"Row {row_num}: Position '{pos_name}' not found.")
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")

            if errors:
                raise serializers.ValidationError({
                    "detail": "Some rows failed to process",
                    "errors": errors[:20]  # Show max 20 errors
                })

            # Bulk create - much faster
            if employees_to_create:
                Employee.objects.bulk_create(employees_to_create)

        return {
            "message": "Bulk upload successful",
            "total_rows": len(df),
            "created": len(employees_to_create),
            "failed": len(errors)
        }   