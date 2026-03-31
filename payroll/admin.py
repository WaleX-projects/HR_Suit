from django.contrib import admin
from .models import (
    PositionSalary,
    SalaryComponent,
    PositionSalaryComponent,
    PayrollRun,
    Payslip,
    PayslipItem,
   
)

 


# =========================
# SALARY COMPONENT
# =========================
@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "component_type", "value", "is_percentage", "company")
    list_filter = ("component_type", "company")
    search_fields = ("name",)


# =========================
# INLINE: Position Components
# =========================
class PositionSalaryComponentInline(admin.TabularInline):
    model = PositionSalaryComponent
    extra = 1


# =========================
# POSITION SALARY
# =========================
@admin.register(PositionSalary)
class PositionSalaryAdmin(admin.ModelAdmin):
    list_display = ("position", "basic_salary", "company")
    list_filter = ("company",)
    search_fields = ("position",)

    inlines = [PositionSalaryComponentInline]


# =========================
# INLINE: Payslip Items
# =========================
class PayslipItemInline(admin.TabularInline):
    model = PayslipItem
    extra = 0
    readonly_fields = ("name", "component_type", "amount")


# =========================
# PAYSLIP
# =========================
@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "payroll",
        "basic_salary",
        "total_allowance",
        "total_deduction",
        "net_salary",
    )

    list_filter = ("payroll",)
    search_fields = ("employee__first_name", "employee__last_name")

    inlines = [PayslipItemInline]


# =========================
# PAYROLL RUN
# =========================
@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ("company", "month", "year", "status", "created_at")
    list_filter = ("status", "company", "year")
    search_fields = ("company__name",)


