import calendar
from datetime import date
from django.utils import timezone

from django.db import transaction
from rest_framework.exceptions import ValidationError

from employees.models import Employee
from attendance.models import Holiday 

from .models import (
    PayrollRun,
    Payslip,
    PayslipItem,
    PositionSalary
)

# payroll/rules/tax.py
from decimal import Decimal

def calculate_paye(annual_income):
    """
    Nigerian PAYE simplified
    """
    if annual_income <= 300000:
        return annual_income * Decimal("0.07")
    elif annual_income <= 600000:
        return annual_income * Decimal("0.11")
    elif annual_income <= 1100000:
        return annual_income * Decimal("0.15")
    else:
        return annual_income * Decimal("0.19")
        
        
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

        if current.weekday() >= 5:
            continue

        if current in holidays:
            continue

        working_days.append(current)

    return working_days


def calculate_attendance(employee, working_days):
    attendance_map = {
        a.date: a.status
        for a in employee.attendances.filter(date__in=working_days)
    }

    absent_days = 0

    for day in working_days:
        if attendance_map.get(day) != "present":
            absent_days += 1

    return absent_days


@transaction.atomic
def generate_payroll(company, year, month):

    
    today = timezone.localdate()
    current_year = today.year
    current_month = today.month

    # =========================
    # ❌ BLOCK FUTURE PAYROLL
    # =========================
    if (year, month) > (current_year, current_month):
        raise ValidationError("❌ Cannot run payroll for a future period")

    payroll, created = PayrollRun.objects.get_or_create(
        company=company,
        month=month,
        year=year
    )

    # =========================
    # 🔒 PAST PAYROLL LOCK
    # =========================
    if (year, month) < (current_year, current_month):
        if payroll.status != "draft":
            raise ValidationError("🔒 This is a past payroll and it is locked")

    # =========================
    # 🔒 CURRENT MONTH RULE
    # =========================
    if (year, month) == (current_year, current_month):
        if payroll.status == "paid":
            raise ValidationError("🔒 This payroll has already been paid")

    # =========================
    # ❌ GENERAL LOCK CHECK
    # =========================
    if payroll.status != "draft":
        raise ValidationError("Payroll is locked")

    # =========================
    # 🧹 CLEAN OLD DATA
    # =========================
    payroll.payslips.all().delete()

    employees = Employee.objects.filter(company=company)

    working_days = get_working_days(company, year, month)
    total_working_days = len(working_days)

    for employee in employees:

        position_salary = PositionSalary.objects.filter(
            company=company,
            position=employee.position
        ).first()

        if not position_salary:
            continue

        basic_salary = position_salary.basic_salary

        absent_days = calculate_attendance(employee, working_days)

        daily_salary = basic_salary / total_working_days if total_working_days else 0
        attendance_deduction = daily_salary * absent_days

        total_allowance = 0
        total_deduction = attendance_deduction

        payslip = Payslip.objects.create(
            payroll=payroll,
            employee=employee,
            basic_salary=basic_salary,
            total_allowance=0,
            total_deduction=0,
            net_salary=0,
        )

        # Attendance deduction
        if attendance_deduction > 0:
            PayslipItem.objects.create(
                payslip=payslip,
                name="Absence Deduction",
                component_type="deduction",
                amount=attendance_deduction
            )
            
        net_salary = basic_salary + total_allowance - total_deduction
        # =========================
        # 💰 TAX CALCULATION
        # =========================
        tax = calculate_paye(net_salary)

        if tax > 0:
            total_deduction += tax

            PayslipItem.objects.create(
                payslip=payslip,
                name="PAYE Tax",
                component_type="deduction",
                amount=tax
            )

        # Salary components
        for item in position_salary.components.all():
            comp = item.component

            if comp.is_percentage:
                amount = (comp.value / 100) * basic_salary
            else:
                amount = comp.value

            if comp.component_type == "allowance":
                total_allowance += amount
            else:
                total_deduction += amount

            PayslipItem.objects.create(
                payslip=payslip,
                name=comp.name,
                component_type=comp.component_type,
                amount=amount
            )

        
        net_salary = basic_salary + total_allowance - total_deduction
        payslip.total_allowance = total_allowance
        payslip.total_deduction = total_deduction
        payslip.net_salary = net_salary
        payslip.save()

    payroll.status = "draft"
    payroll.save()

    return payroll