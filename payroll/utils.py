import calendar
from datetime import date
from decimal import Decimal

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from employees.models import Employee
from attendance.models import Holiday



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

        if current.weekday() >= 5:
            continue

        if current in holidays:
            continue

        working_days.append(current)

    return working_days


