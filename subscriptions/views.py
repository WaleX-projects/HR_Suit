from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = Plan.objects.all()

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        if user.role == 'super_admin':
            return Subscription.objects.all()
        return Subscription.objects.filter(company=self.request.user.company)