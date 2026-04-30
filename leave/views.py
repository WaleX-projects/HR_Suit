# views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.decorators import api_view

from .models import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    LeaveApprovalLog,
    LeavePolicy
)

from .serializers import (
    LeaveTypeSerializer,
    LeaveBalanceSerializer,
    LeaveRequestSerializer,
    LeaveApprovalLogSerializer,
    LeavePolicySerializer
)


# ==========================================
# LEAVE TYPE
# ==========================================
class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


# ==========================================
# LEAVE BALANCE
# ==========================================
class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer


# ==========================================
# LEAVE REQUEST
# ==========================================
class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    
    

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        leave = self.get_object()

        leave.status = "approved"
        leave.approved_by = request.user
        leave.approved_at = timezone.now()
        leave.save()

        LeaveApprovalLog.objects.create(
            leave_request=leave,
            action="approved",
            action_by=request.user
        )

        return Response({"message": "Leave approved"})


    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        leave = self.get_object()

        leave.status = "rejected"
        leave.rejection_reason = request.data.get("reason", "")
        leave.save()

        LeaveApprovalLog.objects.create(
            leave_request=leave,
            action="rejected",
            action_by=request.user,
            note=leave.rejection_reason
        )

        return Response({"message": "Leave rejected"})


# ==========================================
# APPROVAL LOG
# ==========================================
class LeaveApprovalLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveApprovalLog.objects.all()
    serializer_class = LeaveApprovalLogSerializer


# ==========================================
# POLICY
# ==========================================
class LeavePolicyViewSet(viewsets.ModelViewSet):
    queryset = LeavePolicy.objects.all()
    serializer_class = LeavePolicySerializer
    
    
    
@api_view
def get_employee(self,request):
    employee_id = request.data.emplyee_id
    try:
        employee = Employee.objects.get(employee_id = employee_id )
    except Exception as e:
        return Response({"status":"failed","data":str(e)})
    
    return Response({"status":"successful","data":employee.name})
    