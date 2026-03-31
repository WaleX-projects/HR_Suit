from django.urls import path
from .views import  CompanyListView, dashboard_stats

urlpatterns = [
    path("dashboard/stats/", dashboard_stats),
    path("", CompanyListView.as_view()),
]