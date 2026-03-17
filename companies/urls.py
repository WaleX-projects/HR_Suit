from django.urls import path
from .views import CompanySignupView, CompanyListView

urlpatterns = [
    path("signup/", CompanySignupView.as_view()),
    path("", CompanyListView.as_view()),
]