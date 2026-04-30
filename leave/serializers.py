# serializers.py

from rest_framework import serializers
from .models import (
    LeaveType,
    LeaveBalance,
    LeaveRequest,
    LeaveApprovalLog,
    LeavePolicy
)


# ==========================================
# LEAVE TYPE
# ==========================================
class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


# ==========================================
# LEAVE BALANCE
# ==========================================
class LeaveBalanceSerializer(serializers.ModelSerializer):
    remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = LeaveBalance
        fields = "__all__"


# ==========================================
# LEAVE REQUEST
# ==========================================
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"


# ==========================================
# APPROVAL LOG
# ==========================================
class LeaveApprovalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApprovalLog
        fields = "__all__"


# ==========================================
# POLICY
# ==========================================
class LeavePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicy
        fields = "__all__"