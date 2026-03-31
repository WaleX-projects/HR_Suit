from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Employee,Department, Position
from .serializers import EmployeeSerializer,DepartmentSerializer,PositionSerializer
from accounts.permissions import IsAdminOrHR
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


# views.py
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class PositionViewSet(viewsets.ModelViewSet):
    """ crud event for positions of employee """
    queryset = Position.objects.all().order_by("title")
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    def get_queryset(self):
        department_id = self.request.query_params.get("department_id")
        
        if department_id:
            return Position.objects.filter(department_id=department_id)
        return self.queryset    
    
    
    
    def perform_create(self,serializer):
        user = self.request.user
        serializer.save(company= user.company)




class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    def get_queryset(self):
        user = self.request.user
        
        return Department.objects.filter(company=user.company)
        
    
    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(company=user.company)
        
        
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 🔥 FILTERS
    filterset_fields = ["department", "position", "status"]

    # 🔍 SEARCH
    search_fields = ["first_name", "last_name", "email"]

    # 🔄 ORDERING
    ordering_fields = ["created_at", "first_name"]
    
    def get_queryset(self):
        user = self.request.user
        print("user.company", user.company)

        if user.is_superuser or getattr(user, "role", "") == "super_user":
            return Employee.objects.all()

        if not user.company:
            return Employee.objects.none()

        return Employee.objects.filter(company=user.company)

    def perform_create(self, serializer):
        user = self.request.user

        if not user.company and not user.is_superuser:
            raise PermissionDenied("No company assigned")

        serializer.save(company=user.company)
        
        
        
    @action(detail=True, methods=["patch"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        try:
            employee = self.get_object()  # 🔥 best practice
            print(employee.status)
            employee.status = "deactivated"
            print(employee.status)
            employee.save()
    
            return Response(
                {"message": "Employee deactivated successfully"},
                status=status.HTTP_200_OK
            )
    
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    @action(detail=False, methods=["get"], url_path="resolve-account")
    def resolve_account(self, request):
        bank_code = request.query_params.get("bank_code")
        account_number = request.query_params.get("account_number")
    
        if not bank_code or not account_number:
            return Response(
                {"detail": "bank_code and account_number are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
        try:
            url = "https://api.paystack.co/bank/resolve"
    
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
            }
    
            params = {
                "account_number": account_number,
                "bank_code": bank_code
            }
    
            r = requests.get(url, headers=headers, params=params, timeout=10)
    
            # 🔥 DO NOT use raise_for_status
            data = r.json()
            print("PAYSTACK RESPONSE:", data)
    
            if r.status_code != 200:
                return Response(
                    {"detail": data.get("message", "Paystack error")},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
            if not data.get("status"):
                return Response(
                    {"detail": data.get("message")},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
            return Response({
                "account_name": data["data"]["account_name"]
            })
    
        except requests.Timeout:
            return Response(
                {"detail": "Request timeout from Paystack"},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
    
        except Exception as e:
            print("ERROR:", str(e))
            return Response(
                {"detail": "Something went wrong"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    