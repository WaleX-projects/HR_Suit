from rest_framework import generics
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer, CompanySignupSerializer
from rest_framework.permissions import AllowAny
from rest_framework import status

class CompanySignupView(generics.CreateAPIView):
    serializer_class = CompanySignupSerializer
    permission_classes = [AllowAny]  

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response({
            "message": "Company created successfully",
            "company_id": result["company"].id,
            "admin_email": result["user"].email
        },status=status.HTTP_201_CREATED)


class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySerializer
    def get_queryset(self):
        if user.role == 'super_admin':
            return Company.objects.all()
        return Company.objects.filter(id=self.request.user.company_id)