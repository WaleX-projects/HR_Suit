from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from employees.views import EmployeeViewSet
from attendance.views import AttendanceViewSet, ShiftViewSet, EmployeeShiftViewSet
from leave.views import LeaveTypeViewSet, LeaveRequestViewSet
from payroll.views import SalaryViewSet, AllowanceViewSet, DeductionViewSet, PayrollViewSet, PayslipViewSet
from subscriptions.views import PlanViewSet, SubscriptionViewSet
from notifications.views import NotificationViewSet

router = DefaultRouter()

# 👥 Employees
router.register("employees", EmployeeViewSet, basename="employee")

# ⏱️ Attendance
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("shifts", ShiftViewSet, basename="shift")
router.register("employee-shifts", EmployeeShiftViewSet, basename="employee-shift")

# 🧾 Leave
router.register("leave-types", LeaveTypeViewSet, basename="leave-type")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")

# 💰 Payroll
router.register("salaries", SalaryViewSet, basename="salary")
router.register("allowances", AllowanceViewSet, basename="allowance")
router.register("deductions", DeductionViewSet, basename="deduction")
router.register("payrolls", PayrollViewSet, basename="payroll")
router.register("payslips", PayslipViewSet, basename="payslip")

# 💳 Subscriptions
router.register("plans", PlanViewSet, basename="plan")
router.register("subscriptions", SubscriptionViewSet, basename="subscription")

# 🔔 Notifications
router.register("notifications", NotificationViewSet, basename="notification")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("accounts.urls")),
    path("api/companies/", include("companies.urls")),
]
urlpatterns += [
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
]