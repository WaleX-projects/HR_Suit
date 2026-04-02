from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PositionSalaryViewSet,
    SalaryComponentViewSet,
    PayrollRunViewSet,
    employee_payslips
    
)

router = DefaultRouter()


router.register("positions", PositionSalaryViewSet, basename="postion")
router.register("components", SalaryComponentViewSet,basename="components")
router.register("payrolls", PayrollRunViewSet,basename="payroll")


urlpatterns = router.urls
urlpatterns = [
    path("", include(router.urls)),

    path("employees/<str:employee_id>/payslips/", employee_payslips),
]