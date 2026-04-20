from django.contrib import admin
from .models import LeaveType, LeaveRequest

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'days_allowed')
    search_fields = ('name',)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    # Organizes the list view for quick oversight
    list_display = (
        'employee', 
        'leave_type', 
        'start_date', 
        'end_date', 
        'status', 
        'company'
    )
    
    # Adds a sidebar for filtering by status, company, or type
    list_filter = ('status', 'leave_type', 'company', 'start_date')
    
    # Search by employee name or reason
    search_fields = ('employee__first_name', 'employee__last_name', 'reason')
    
    # Makes the admin form more organized
    fieldsets = (
        ('Request Info', {
            'fields': ('company', 'employee', 'leave_type', 'reason')
        }),
        ('Duration', {
            'fields': (('start_date', 'end_date'),)
        }),
        ('Approval Status', {
            'fields': ('status', 'approved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Hides these by default
        }),
    )
    
    # Sets created_at and updated_at to read-only
    readonly_fields = ('created_at', 'updated_at')

    # Automatically sets 'approved_by' to the logged-in admin when saving
    def save_model(self, request, obj, form, change):
        if obj.status == 'approved' and not obj.approved_by:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)
