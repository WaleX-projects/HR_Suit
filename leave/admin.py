"""from django.contrib import admin
from .models import LeaveType, LeaveRequest


# =========================
# Leave Type Admin
# =========================
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "days_allowed")
    search_fields = ("name",)


# =========================
# Leave Request Admin
# =========================
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "company",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "approved_by",
        "created_at",
    )

    list_filter = (
        "status",
        "leave_type",
        "company",
        "start_date",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "employee__email",
    )

    readonly_fields = ("created_at", "updated_at")

    # =========================
    # Multi-tenant restriction
    # =========================
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        return qs.filter(company=request.user.company)

    # =========================
    # Auto-assign company
    # =========================
    def save_model(self, request, obj, form, change):
        if not obj.company:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    # =========================
    # Admin Actions
    # =========================
    actions = ["approve_leave", "reject_leave"]

    def approve_leave(self, request, queryset):
        queryset.update(status="approved", approved_by=request.user)
    approve_leave.short_description = "Approve selected leave requests"

    def reject_leave(self, request, queryset):
        queryset.update(status="rejected", approved_by=request.user)
    reject_leave.short_description = "Reject selected leave requests"
"""