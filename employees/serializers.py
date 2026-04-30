

from rest_framework import serializers
from .models import Employee, Position, Department
from companies.models import IDCounter
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
        source="salary.basic_salary",
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
        try:
            
            salary = obj.salary
        except PositionSalary.DoesNotExist:
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
from rest_framework import serializers
from django.db import transaction
from django.utils.dateparse import parse_date

from .models import Employee, Department, Position


class BulkEmployeeUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, file):
        if not file.name.lower().endswith((".xlsx", ".xls", ".csv")):
            raise serializers.ValidationError(
                "Only Excel (.xlsx, .xls) or CSV files are allowed."
            )
        return file

    def create(self, validated_data):
        file = validated_data["file"]

        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Request context is required")

        company = request.user.company

        # =========================
        # READ FILE
        # =========================
        try:
            if file.name.lower().endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to read file: {str(e)}")

        employees_to_create = []
        errors = []

        # =========================
        # PRELOAD DATA (OPTIMIZATION)
        # =========================
        departments = {
            d.name.lower(): d
            for d in Department.objects.filter(company=company)
        }

        positions = {
            p.title.lower(): p
            for p in Position.objects.filter(company=company)
        }

        existing_emails = set(
            Employee.objects.filter(company=company)
            .values_list("email", flat=True)
        )

        # =========================
        # PROCESS ROWS
        # =========================
        with transaction.atomic():
            for index, row in df.iterrows():
                counter_obj, _ = IDCounter.objects.select_for_update().get_or_create(name=company.name)
                current_val = counter_obj.last_value
                row_num = index + 2

                try:
                    # Department
                    dept_name = str(
                        row.get("department") or row.get("Department") or ""
                    ).strip().lower()

                    if not dept_name:
                        raise ValueError("Department is required")

                    department = departments.get(dept_name)
                    if not department:
                        department = Department.objects.create(
                            company=company,
                            name=dept_name.title()
                        )
                        departments[dept_name] = department
                    
                                        # Position
                    pos_name = str(
                        row.get("position") or row.get("Position") or ""
                    ).strip().lower()

                    position = positions.get(pos_name)
                    if not position:
                        position = Position.objects.create(
                            company=company,
                            title=pos_name.title(),
                            department=department
                        )
                        positions[pos_name] = position
                    # Hire Date
                    hire_date_str = row.get("hire_date") or row.get("Hire Date")
                    hire_date = (
                        parse_date(str(hire_date_str)) if hire_date_str else None
                    )

                    if not hire_date:
                        raise ValueError(
                            "Valid hire_date is required (YYYY-MM-DD)"
                        )

                    # Basic Fields
                    first_name = str(
                        row.get("first_name") or row.get("First Name") or ""
                    ).strip()

                    last_name = str(
                        row.get("last_name") or row.get("Last Name") or ""
                    ).strip()

                    email = str(
                        row.get("email") or row.get("Email") or ""
                    ).strip().lower()

                    if not first_name or not last_name or not email:
                        raise ValueError(
                            "First name, last name and email are required"
                        )

                    if email in existing_emails:
                        raise ValueError("Email already exists")
                    current_val += 1
                    custom_id = f"{company.name.upper()}-EMP-{current_val:04d}"    

                    employee = Employee(
                        employee_id=custom_id,
                        company=company,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=str(row.get("phone") or row.get("Phone") or "").strip(),
                        hire_date=hire_date,
                        department=department,
                        position=position,
                        status=str(row.get("status", "active")).strip().lower(),

                        # Bank details
                        bank_name=str(row.get("bank_name") or "").strip() or None,
                        bank_account_name=str(row.get("bank_account_name") or "").strip() or None,
                        bank_account_number=str(row.get("bank_account_number") or "").strip() or None,
                        bank_code=str(row.get("bank_code") or "").strip() or None,
                        bank_account_type=str(
                            row.get("bank_account_type", "savings")
                        ).strip().lower(),
                        currency=str(row.get("currency", "NGN")).strip().upper(),
                    )

                    employees_to_create.append(employee)
                    existing_emails.add(email)  # prevent duplicates in same file
                    counter_obj.last_value = current_val
                    counter_obj.save()

                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")

            # =========================
            # HANDLE ERRORS
            # =========================
            if errors:
                raise serializers.ValidationError({
                    "message": "Some rows failed",
                    "errors": errors[:20]
                })

            # =========================
            # BULK INSERT
            # =========================
            if employees_to_create:
                Employee.objects.bulk_create(
                    employees_to_create,
                    batch_size=500
                )

        # =========================
        # RESPONSE
        # =========================
        return {
            "message": "Bulk upload successful",
            "total_rows": len(df),
            "created": len(employees_to_create),
        }