from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.decorators import action
from django.db import models
from .models import LeaveType, LeaveRequest
from .serializers import (
    LeaveTypeSerializer,
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

    # Optional: Only allow listing if needed
    def get_queryset(self):
        return LeaveType.objects.all().order_by('name')


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'approved_by', 'company'
        ).order_by("-created_at")

        # Super Admin sees everything
        if getattr(user, 'role', None) == "super_admin":
            return queryset

        # Company users see only their company
        return queryset.filter(company=user.company)

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer

    def perform_create(self, serializer):
        user = self.request.user
        
        # Important: Do NOT auto-assign employee to current user
        # Let the frontend send the employee_id
        serializer.save(
            company=user.company,
            # approved_by and status remain default (pending)
        )

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()

        # Only allow status change for approval/rejection
        if 'status' in serializer.validated_data:
            if user.role not in ["company_admin", "hr"]:
                raise PermissionDenied("Only admins can approve or reject leave requests.")

            serializer.save(approved_by=user)
        else:
            # Normal update (rarely needed)
            serializer.save()

    # Optional: Summary endpoint
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Return leave summary per leave type for the company"""
        user = request.user
        summaries = []

        leave_types = LeaveType.objects.all()

        for lt in leave_types:
            total_leaves = LeaveRequest.objects.filter(
                company=user.company,
                leave_type=lt
            ).count()

            approved_days = LeaveRequest.objects.filter(
                company=user.company,
                leave_type=lt,
                status="approved"
            ).aggregate(total_days=models.Sum(
                models.ExpressionWrapper(
                    models.F('end_date') - models.F('start_date') + 1,
                    output_field=models.IntegerField()
                )
            ))['total_days'] or 0

            summaries.append({
                "leave_type": lt.name,
                "days_allowed": lt.days_allowed,
                "used": approved_days,
                "remaining": max(0, lt.days_allowed - approved_days),
                "total": lt.days_allowed,
            })

        return Response(summaries)

    # Optional: Simple approve/reject actions
    @action(detail=True, methods=['post'])
    def approved(self, request, pk=None):
        leave = self.get_object()
        user = request.user

        if user.role not in ["company_admin", "hr"]:
            raise PermissionDenied("Only admins can approve leaves.")

        leave.status = "approved"
        leave.approved_by = user
        leave.save()

        return Response({"status": "approved"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def rejected(self, request, pk=None):
        leave = self.get_object()
        user = request.user

        if user.role not in ["company_admin", "hr"]:
            raise PermissionDenied("Only admins can reject leaves.")

        leave.status = "rejected"
        leave.approved_by = user
        leave.save()

        return Response({"status": "rejected"}, status=status.HTTP_200_OK)