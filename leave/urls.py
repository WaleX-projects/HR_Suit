# payroll/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PayrollDashboardView,

    SalaryComponentViewSet,
    CompanySalaryStructureViewSet,
    PositionSalaryViewSet,
    PositionSalaryComponentViewSet,
    EmployeeSalaryOverrideViewSet,

    AttendanceViewSet,
    HolidayViewSet,

    PayrollInputViewSet,
    PayrollRunViewSet,
    PayslipViewSet,

    employee_payslips,
)

# ==================================================
# ROUTER
# ==================================================

router = DefaultRouter()

# Payroll Setup
router.register(
    r"salary-components",
    SalaryComponentViewSet,
    basename="salary-components"
)

router.register(
    r"salary-structures",
    CompanySalaryStructureViewSet,
    basename="salary-structures"
)

router.register(
    r"position-salaries",
    PositionSalaryViewSet,
    basename="position-salaries"
)

router.register(
    r"position-components",
    PositionSalaryComponentViewSet,
    basename="position-components"
)

router.register(
    r"employee-overrides",
    EmployeeSalaryOverrideViewSet,
    basename="employee-overrides"
)

# Attendance
router.register(
    r"attendance",
    AttendanceViewSet,
    basename="attendance"
)

router.register(
    r"holidays",
    HolidayViewSet,
    basename="holidays"
)

# Payroll Core
router.register(
    r"inputs",
    PayrollInputViewSet,
    basename="inputs"
)

router.register(
    r"runs",
    PayrollRunViewSet,
    basename="runs"
)

router.register(
    r"payslips",
    PayslipViewSet,
    basename="payslips"
)

# ==================================================
# URLS
# ==================================================

urlpatterns = [
    # Dashboard
    path(
        "dashboard/",
        PayrollDashboardView.as_view(),
        name="payroll-dashboard"
    ),

    # Employee Payslips
    path(
        "employees/<uuid:employee_id>/payslips/",
        employee_payslips,
        name="employee-payslips"
    ),

    # Router URLs
    path("", include(router.urls)),
]