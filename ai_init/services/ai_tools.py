from employees.models import Employee
from attendance.models import Attendance
from django.db.models import Q
from datetime import date

# ================= EMPLOYEES =================
def get_employees(company, search=None):
    qs = Employee.objects.filter(company=company)
    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Standard values() returns UUID objects. 
    # We must convert them to strings for the JSON encoder.
    data = list(qs.values("id", "first_name", "last_name", "email"))
    for item in data:
        item['id'] = str(item['id']) # Convert UUID to String
    return data

# ================= ATTENDANCE =================
def get_attendance(company, start_date=None, end_date=None, status=None):
    qs = Attendance.objects.filter(employee__company=company)
    # ... your existing filters ...

    data = list(qs.values(
        "id",
        "employee__first_name",
        "employee__last_name",
        "date",
        "status"
    ))
    
    for item in data:
        item['id'] = str(item['id']) # Convert UUID to String
        item['date'] = str(item['date']) # Dates also need to be strings!
        
    return data

# ================= ATTENDANCE =================
def get_attendance(company, start_date=None, end_date=None, status=None):
    qs = Attendance.objects.filter(employee__company=company)

    if start_date:
        qs = qs.filter(date__gte=start_date)

    if end_date:
        qs = qs.filter(date__lte=end_date)

    if status:
        qs = qs.filter(status=status)

    return list(qs.values(
        "id",
        "employee__first_name",
        "employee__last_name",
        "date",
        "status"
    ))


def get_absent_employees(company):
    today = date.today()

    qs = Attendance.objects.filter(
        employee__company=company,
        date=today,
        status="absent"
    )

    return list(qs.values(
        "employee__first_name",
        "employee__last_name"
    ))