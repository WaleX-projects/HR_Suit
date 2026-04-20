from django.urls import path
from .views import  CompanyListView, dashboard_stats,CompanySettingsView

urlpatterns = [
    path("dashboard/stats/", dashboard_stats),
    path("", CompanyListView.as_view()),
    path("company/settings/",CompanySettingsView.as_view(),name="settings")
]