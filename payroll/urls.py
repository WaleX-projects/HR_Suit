from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PositionSalaryViewSet,
    SalaryComponentViewSet,
    PayrollRunViewSet,
    employee_payslips
    
)

router = DefaultRouter()


router.register("positions", PositionSalaryViewSet)
router.register("components", SalaryComponentViewSet)
router.register("payrolls", PayrollRunViewSet)


urlpatterns = router.urls
urlpatterns = [
    path("", include(router.urls)),

    path("employees/<str:employee_id>/payslips/", employee_payslips),
]