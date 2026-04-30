import calendar
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Q

from employees.models import Employee
from attendance.models import Attendance
from payroll.models import (
    PayrollRun,
    PayrollInput,
    SalaryComponent,
)


class AttendanceService:
    """
    Converts attendance records into PayrollInput rows.

    Example:
    - Absent days  -> deduction
    - Overtime hrs -> allowance
    - Late days    -> deduction (optional)
    """

    @staticmethod
    @transaction.atomic
    def run_attendance(company_id, month, year):
        """
        Generate payroll inputs from attendance
        """

        # =========================
        # GET / CREATE PAYROLL RUN
        # =========================
        payroll, created = PayrollRun.objects.get_or_create(
            company_id=company_id,
            month=month,
            year=year,
            defaults={"status": "draft"}
        )

        if payroll.status != "draft":
            raise Exception("Only draft payroll can sync attendance.")

        # =========================
        # COMPONENTS
        # =========================
        absence_component, _ = SalaryComponent.objects.get_or_create(
            company_id=company_id,
            name="Absence Deduction",
            defaults={
                "component_type": "deduction",
                "is_percentage": False,
                "is_active": True,
            }
        )

        overtime_component, _ = SalaryComponent.objects.get_or_create(
            company_id=company_id,
            name="Overtime",
            defaults={
                "component_type": "allowance",
                "is_percentage": False,
                "is_active": True,
            }
        )

        # =========================
        # CLEAR OLD AUTO INPUTS
        # =========================
        PayrollInput.objects.filter(
            payroll=payroll,
            component__in=[absence_component, overtime_component]
        ).delete()

        # =========================
        # EMPLOYEES
        # =========================
        employees = Employee.objects.filter(
            company_id=company_id,
            status=True
        ).select_related("position")

        total_days = calendar.monthrange(year, month)[1]

        for employee in employees:

            records = Attendance.objects.filter(
                employee=employee,
                date__year=year,
                date__month=month
            )

            # =========================
            # ABSENT DAYS
            # =========================
            absent_days = records.filter(status="absent").count()

            # =========================
            # OVERTIME HOURS
            # =========================
            overtime_hours = records.aggregate(
                total=Count("id", filter=Q(is_overtime=True))
            )["total"] or 0

            # =========================
            # POSITION SALARY
            # =========================
            if not hasattr(employee.position, "salary"):
                continue

            basic_salary = Decimal(employee.position.salary.basic_salary)

            daily_rate = basic_salary / Decimal(total_days)
            hourly_rate = daily_rate / Decimal("8")

            # =========================
            # ABSENCE DEDUCTION
            # =========================
            if absent_days > 0:
                deduction = daily_rate * Decimal(absent_days)

                PayrollInput.objects.create(
                    payroll=payroll,
                    employee=employee,
                    component=absence_component,
                    value=deduction
                )

            # =========================
            # OVERTIME PAY
            # =========================
            if overtime_hours > 0:
                overtime_pay = hourly_rate * Decimal("1.5") * Decimal(overtime_hours)

                PayrollInput.objects.create(
                    payroll=payroll,
                    employee=employee,
                    component=overtime_component,
                    value=overtime_pay
                )

        return payroll