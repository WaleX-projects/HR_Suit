from django.contrib import admin
from .models import (
    SalaryComponent,
    CompanySalaryStructure,
    PositionSalary,
    PositionSalaryComponent,
    EmployeeSalaryOverride,
    PayrollRun,
    PayrollInput,
    Payslip,
    PayslipItem,
)


# =====================================
# INLINE ADMINS
# =====================================

class PositionSalaryComponentInline(admin.TabularInline):
    model = PositionSalaryComponent
    extra = 1


class PayrollInputInline(admin.TabularInline):
    model = PayrollInput
    extra = 0


class PayslipItemInline(admin.TabularInline):
    model = PayslipItem
    extra = 0


class PayslipInline(admin.TabularInline):
    model = Payslip
    extra = 0
    readonly_fields = (
        "employee",
        "basic_salary",
        "total_allowance",
        "total_deduction",
        "net_salary",
        "created_at",
    )


# =====================================
# SALARY COMPONENT
# =====================================

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "component_type",
        "is_percentage",
        "is_active",
    )
    list_filter = (
        "company",
        "component_type",
        "is_percentage",
        "is_active",
    )
    search_fields = ("name", "company__name")


# =====================================
# COMPANY SALARY STRUCTURE
# =====================================

@admin.register(CompanySalaryStructure)
class CompanySalaryStructureAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "component",
        "default_value",
        "is_mandatory",
    )
    list_filter = ("company", "is_mandatory")
    search_fields = (
        "company__name",
        "component__name",
    )


# =====================================
# POSITION SALARY
# =====================================

@admin.register(PositionSalary)
class PositionSalaryAdmin(admin.ModelAdmin):
    list_display = (
        "position",
        "company",
        "basic_salary",
        "created_at",
    )
    list_filter = ("company",)
    search_fields = (
        "position__title",
        "company__name",
    )
    inlines = [PositionSalaryComponentInline]


# =====================================
# POSITION COMPONENTS
# =====================================

@admin.register(PositionSalaryComponent)
class PositionSalaryComponentAdmin(admin.ModelAdmin):
    list_display = (
        "position_salary",
        "component",
        "value",
    )
    search_fields = (
        "position_salary__position__title",
        "component__name",
    )


# =====================================
# EMPLOYEE OVERRIDES
# =====================================

@admin.register(EmployeeSalaryOverride)
class EmployeeSalaryOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "component",
        "value",
    )
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "component__name",
    )


# =====================================
# PAYROLL RUN
# =====================================

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "month",
        "year",
        "status",
        "created_at",
    )
    list_filter = (
        "company",
        "status",
        "year",
        "month",
    )
    search_fields = ("company__name",)
    inlines = [PayrollInputInline, PayslipInline]

    actions = ["mark_as_processed", "mark_as_paid"]

    @admin.action(description="Mark selected payrolls as Processed")
    def mark_as_processed(self, request, queryset):
        for payroll in queryset:
            if payroll.status == "draft":
                payroll.status = "processed"
                payroll.save()

    @admin.action(description="Mark selected payrolls as Paid")
    def mark_as_paid(self, request, queryset):
        for payroll in queryset:
            if payroll.status == "processed":
                payroll.status = "paid"
                payroll.save()


# =====================================
# PAYROLL INPUT
# =====================================

@admin.register(PayrollInput)
class PayrollInputAdmin(admin.ModelAdmin):
    list_display = (
        "payroll",
        "employee",
        "component",
        "value",
    )
    list_filter = ("payroll",)
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "component__name",
    )


# =====================================
# PAYSLIP
# =====================================

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "payroll",
        "basic_salary",
        "total_allowance",
        "total_deduction",
        "net_salary",
        "created_at",
    )
    list_filter = (
        "payroll",
        "created_at",
    )
    search_fields = (
        "employee__first_name",
        "employee__last_name",
    )
    readonly_fields = (
        "created_at",
    )
    inlines = [PayslipItemInline]


# =====================================
# PAYSLIP ITEMS
# =====================================

@admin.register(PayslipItem)
class PayslipItemAdmin(admin.ModelAdmin):
    list_display = (
        "payslip",
        "name",
        "component_type",
        "amount",
    )
    list_filter = ("component_type",)
    search_fields = ("name",)