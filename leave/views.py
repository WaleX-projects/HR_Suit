from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import LeaveType, LeaveRequest
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 👑 Super admin sees all
        if user.role == "super_admin":
            return LeaveRequest.objects.all().order_by("-created_at")

        # 🏢 Company users see only their company leaves
        return LeaveRequest.objects.filter(
            company=user.company
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(
            company=user.company,
            employee=user.employee  # assuming user linked to employee
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        # ❌ Only admin can approve/reject
        if "status" in serializer.validated_data:
            if user.role != "admin":
                raise PermissionError("Not allowed to approve/reject")

            serializer.save(approved_by=user)
        else:
            serializer.save()