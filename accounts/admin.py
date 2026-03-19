"""from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
#EmployeeInvite

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'company', 'is_staff', 'is_super_admin')
    list_filter = ('is_staff', 'is_super_admin', 'company')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone', 'company', 'is_super_admin')}),
    )

@admin.register(EmployeeInvite)
class EmployeeInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'company', 'token', 'used', 'created_at')
    list_filter = ('used', 'company')
    search_fields = ('email',)
    readonly_fields = ('token', 'created_at')
"""