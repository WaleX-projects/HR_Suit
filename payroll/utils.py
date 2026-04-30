import calendar
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from employees.models import Employee
from attendance.models import Holiday
from payroll.models import (
    PayrollRun,
    CompanySalaryStructure,
    PositionSalary,
    PositionSalaryComponent,
    EmployeeSalaryOverride,
    PayrollInput,
    Payslip,
    PayslipItem,
)


# =========================
# 📅 WORKING DAYS
# =========================
def get_working_days(company, year, month):
    total_days = calendar.monthrange(year, month)[1]

    holidays = set(
        Holiday.objects.filter(
            company=company,
            date__year=year,
            date__month=month
        ).values_list("date", flat=True)
    )

    working_days = []

    for d in range(1, total_days + 1):
        current = date(year, month, d)

        # skip weekends
        if current.weekday() >= 5:
            continue

        # skip holidays
        if current in holidays:
            continue

        working_days.append(current)

    return working_days


# =========================
# 💰 PAYROLL SERVICE
# =========================
class PayrollService:
    """
    Priority:
    Company Structure
    ↓
    Position Structure
    ↓
    Employee Override
    ↓
    Payroll Inputs
    ↓
    Payslip Snapshot
    """

    @staticmethod
    @transaction.atomic
    def run_payroll(company_id, month, year):
        """
        Run payroll for a company/month/year
        """

        # =========================
        # GET OR CREATE PAYROLL RUN
        # =========================
        payroll, created = PayrollRun.objects.get_or_create(
            company_id=company_id,
            month=month,
            year=year,
            defaults={"status": "draft"}
        )

        if payroll.status != "draft":
            raise ValidationError("Only draft payroll can be processed.")

        # remove old payslips if rerun
        payroll.payslips.all().delete()

        # =========================
        # ACTIVE EMPLOYEES
        # =========================
        employees = Employee.objects.filter(
            company_id=company_id,
            status="active"
        ).select_related("position")

        for employee in employees:

            # =========================
            # POSITION SALARY
            # =========================
            try:
                position_salary = PositionSalary.objects.prefetch_related(
                    "components__component"
                ).get(
                    company_id=company_id,
                    position=employee.position
                )
            except PositionSalary.DoesNotExist:
                continue

            basic_salary = Decimal(position_salary.basic_salary)

            total_allowance = Decimal("0.00")
            total_deduction = Decimal("0.00")

            items = []

            # =========================
            # COMPANY DEFAULTS
            # =========================
            company_defaults = CompanySalaryStructure.objects.select_related(
                "component"
            ).filter(company_id=company_id)

            for row in company_defaults:
                amount = Decimal(row.default_value)

                items.append({
                    "component": row.component,
                    "name": row.component.name,
                    "type": row.component.component_type,
                    "amount": amount
                })

            # =========================
            # POSITION COMPONENTS
            # =========================
            for row in position_salary.components.all():
                amount = Decimal(row.value)

                items.append({
                    "component": row.component,
                    "name": row.component.name,
                    "type": row.component.component_type,
                    "amount": amount
                })

            # =========================
            # EMPLOYEE OVERRIDES
            # =========================
            overrides = EmployeeSalaryOverride.objects.select_related(
                "component"
            ).filter(employee=employee)

            for row in overrides:
                amount = Decimal(row.value)

                # replace existing component if same one exists
                items = [i for i in items if i["component"] != row.component]

                items.append({
                    "component": row.component,
                    "name": row.component.name,
                    "type": row.component.component_type,
                    "amount": amount
                })

            # =========================
            # PAYROLL INPUTS
            # bonuses / deductions / overtime
            # =========================
            inputs = PayrollInput.objects.select_related(
                "component"
            ).filter(
                payroll=payroll,
                employee=employee
            )

            for row in inputs:
                amount = Decimal(row.value)

                items.append({
                    "component": row.component,
                    "name": row.component.name,
                    "type": row.component.component_type,
                    "amount": amount
                })

            # =========================
            # TOTALS
            # =========================
            for item in items:
                if item["type"] == "allowance":
                    total_allowance += item["amount"]
                else:
                    total_deduction += item["amount"]

            net_salary = basic_salary + total_allowance - total_deduction

            # =========================
            # CREATE PAYSLIP
            # =========================
            payslip = Payslip.objects.create(
                payroll=payroll,
                employee=employee,
                basic_salary=basic_salary,
                total_allowance=total_allowance,
                total_deduction=total_deduction,
                net_salary=net_salary,
            )

            # =========================
            # PAYSLIP ITEMS
            # =========================
            PayslipItem.objects.bulk_create([
                PayslipItem(
                    payslip=payslip,
                    component=i["component"],
                    name=i["name"],
                    component_type=i["type"],
                    amount=i["amount"]
                )
                for i in items
            ])

        
        payroll.save()

        return payroll