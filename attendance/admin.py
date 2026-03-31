from django.contrib import admin
from .models import Attendance,Holiday

admin.site.register(Attendance)

# =========================
# HOLIDAY
# =========================
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "date")
    list_filter = ("company",)
    search_fields = ("name",)