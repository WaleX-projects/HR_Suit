

from rest_framework import serializers
from .models import Employee, Position, Department
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




class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    
    salary = PositionSalarySerializer(many=True, required=False, allow_null=True)

    total_employees = serializers.IntegerField(read_only=True)
    total_salary_cost = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Position
        fields = [
            "id", "title", "department", "department_name",
            "salary", "total_employees", "total_salary_cost", "is_single_role"
        ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        salaries_data = validated_data.pop('salary', [])

        position = Position.objects.create(**validated_data)
        company = position.department.company

        for salary_data in salaries_data:
            serializer = PositionSalarySerializer(
                data=salary_data,
                context={"position": position, "company": company}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return position

    def update(self, instance, validated_data):
        salaries_data = validated_data.pop('salary', None)

        # Update Position fields
        instance.title = validated_data.get('title', instance.title)
        instance.department = validated_data.get('department', instance.department)
        instance.is_single_role = validated_data.get('is_single_role', instance.is_single_role)
        instance.save()

        if salaries_data is not None:
            company = instance.department.company

            for salary_data in salaries_data:
                salary_id = salary_data.get('id')

                if salary_id:  
                    # === UPDATE existing PositionSalary ===
                    try:
                        position_salary = PositionSalary.objects.get(
                            id=salary_id, 
                            position=instance
                        )
                        # Update basic_salary
                        position_salary.basic_salary = salary_data.get('basic_salary', position_salary.basic_salary)
                        position_salary.save()

                        # Replace components (simple approach)
                        position_salary.components.all().delete()

                        components_data = salary_data.get('components', [])
                        for comp in components_data:
                            # Handle both formats: if frontend sends full component or just component_id
                            if isinstance(comp, dict):
                                comp_id = comp.get('component_id') or comp.get('component', {}).get('id')
                            else:
                                comp_id = comp

                            if comp_id:
                                PositionSalaryComponent.objects.create(
                                    position_salary=position_salary,
                                    component_id=comp_id
                                )

                    except PositionSalary.DoesNotExist:
                        # If id is invalid, treat as create
                        salary_id = None

                if not salary_id:
                    # === CREATE new PositionSalary ===
                    serializer = PositionSalarySerializer(
                        data=salary_data,
                        context={"position": instance, "company": company}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

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