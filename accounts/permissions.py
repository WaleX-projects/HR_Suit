from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "company_admin"


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "hr"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "employee"


class IsAdminOrHR(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ["company_admin", "hr"]
